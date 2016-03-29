__author__ = 'Matt Cordoba'
import datetime
from Recording import Recording
from Relay import Relay
import time
time.strftime('%Y-%m-%d %H:%M:%S')
def record(sensor,database,minutes):
    """

    :param sensor: the sensor to start a recording on
    :type sensor: Sensor (abstract class)
    :param database: the database object to use as a connection
    :type database: Database
    :param minutes: time to record for
    :type minutes: int
    :return: None
    :rtype: None
    """
    print('EVENT HAS BEEN TRIGGERED: creating a recorder')
    start = datetime.datetime.now()
    start = start - datetime.timedelta(hours=8)
    end =start + datetime.timedelta(minutes=minutes)
    channelNumber = sensor.channelNumber
    apiKey = database._apiKeyId
    sql = 'INSERT INTO innodb.kushmobile_recording' \
          '(kushmobile_recording.startDateTime,kushmobile_recording.endDateTime,kushmobile_recording.apiKey_id,kushmobile_recording.channelNumber,isActive,kushmovile_recording.user_id)' \
        'VALUES("%s","%s",%i,%i,1,1)' % (start,end,apiKey,channelNumber)
    print(sql)
    database._sqlcursor.execute(sql)
    database._sqlcnx.commit()
    recordingId = database._sqlcursor._last_insert_id
    start = time.mktime(start.timetuple())
    end = time.mktime(end.timetuple())
    recorder = Recording(recordingId,start,end,apiKey,channelNumber,database)
    if(not sensor.hasRecording):
        print('recorder created...setting')
        sensor.setRecorder(recorder)
    else:
        print('sensor is already recording')

def record5(sensor,database):
    """
    Start a recording for 5 minutes
    :param sensor: sensor to record
    :type sensor: Sensor
    :param database: the database object to use as a connection
    :type database: Database
    :return: None
    :rtype: None
    """
    record(sensor,database,2)
def engageDigitalOutput(sensor,database):
    """
    Engage a digital output
    :param sensor: Sensor to engage
    :type sensor: Sensor
    :param database: database object to use as a connection
    :type database: Database
    :return: None
    :rtype: None
    """
    if(type(sensor) is not Relay):
        print('sensor can not do this... I dont think so')
    else:
        sensor.command(True) #sets digital output high

OUTPUT_TYPE_TO_FCN = {1:record5,2:engageDigitalOutput}
class EventTrigger():
    def __init__(self,inputSensor,inputType,outputSensor,outputType,conditionalString,threshold,id,database):
        """
        creates an event trigger function
        :param inputSensor: A reference to the input sensor object
        :type inputSensor: Sensor
        :param inputType: The id of input typing (from SQL database) to gather from the sensor
        :type inputType: int
        :param outputSensor: A reference to the output sensor object
        :type outputSensor: Sensor
        :param outputType: The id of the output function type to execute on completion
        :type outputType: int
        :param conditionalString: A conditional string such as > , >= , etc. to execute logic on the sensor values
        :type conditionalString: str
        :param threshold: The threshold float value for the condition
        :type threshold: float
        :param id: the id of the event trigger as referenced by SQL
        :type id: int
        :param database: the database connection for the event trigger to use
        :type database: Database
        :return: an event trigger object
        :rtype: EventTrigger
        """
        self.inputSensor = inputSensor
        self.inputType = inputType
        self.outputSensor = outputSensor
        self.outputType = outputType
        print(self.outputType)
        self.condition = conditionalString
        self.threshold = threshold
        self.id = id
        self.lockOutStart = 0
        self.duration = 5 * 3600 #lock out for 5 minutes
        self._conditionalCode = "if(self._currentInputValue %s self.threshold): valid = True" % self.condition
        self.outputFunction = OUTPUT_TYPE_TO_FCN[self.outputType]
        self.database = database
        self.triggered = False
    def runResultFunction(self):
        """
        Execute the result function for the event trigger
        :return: None
        :rtype: None
        """
        self.outputFunction(self.outputSensor,self.database)
    def handleEvent(self):
        """

        :return:
        :rtype:
        """
        if(self.testConditionalFunction()):
            #print(time.time() - self.lockOutStart)
            if(time.time() - self.lockOutStart > self.duration):
                self.lockOutStart = time.time() #disables the event for a duration of time
                self.runResultFunction()
                self.triggered = True
    def testConditionalFunction(self):
        self._currentInputValue = self.inputSensor.getValue()
        valid = False
        exec(self._conditionalCode)

        return valid