__author__ = 'Matt Cordoba'
import time
import math
TEN_MINUTES = 60 * 1 * 1000 #in millis
class Recording():
    def __init__(self,recordingId,startTime,endTime,apiKey,channelNumber,internalDB):
        """
        Creates a recording object to bind to a sensor
        :param recordingId: the integer id of the recording in the SQL database
        :type recordingId: int
        :param startTime: the timestamp (epoch seconds) for the recording to start at
        :type startTime: int
        :param endTime: the timestamp (epoch seconds) for the recording to end at
        :type endTime: int
        :param apiKey: the api key for the mms unit
        :type apiKey: str
        :param channelNumber: the channel number that the recording is connecting to on the MMS device
        :type channelNumber: int
        :param internalDB: a connection to the SQL and mongo database
        :type internalDB: Database
        :return: a recording object
        :rtype: Recording
        """
        self.recordingId = recordingId
        self.startTime = startTime
        self.endTime = endTime
        self.apiKey = apiKey
        self._internalDB = internalDB
        self.sliceQueue = []
        self.channelNumber = channelNumber
        self.initialSlice = True
        self.timestampOfSlice = None
        self.relativeSliceAddress = None
    def isComplete(self):
        """
        Tests if the recording has reached its end time
        :return: returns true is completed, false if not
        :rtype: bool
        """
        if(time.time()-8*3600 > self.endTime): #correct for timezone
            return True
        return False
    def setSensorMetaData(self,metaData):
        """
        Sets the meta data for the recording sensor.  This is used so the sensor information can be pushed when
        the recording info is pushed
        :param metaData:  dictionary containing the sensor metadata
        :type metaData: dict
        :return: None
        :rtype: None
        """
        self.sensorMetaData = metaData
    def setSliceAddress(self,address):
        """
        Sets the address of the current timeslice that is being prepped to be pushed
        :param address: address of the slice (epoch seconds)
        :type address: int/long
        :return: None
        :rtype: None
        """
        self.relativeSliceAddress = address
        print(self.relativeSliceAddress)
    def handleData(self,data):
        """
        Handles a dictionary containing the data and arranging the data into timeslices.  Once the time threshold has been
        reached the data is pushed out in this function
        :param data: a dictionary of data from the sensor
        :type data: dict
        :return: None
        :rtype: None
        """
        print('handling recording data')
        value = data['value']
        timestamp = data['timestamp'] * 1000.0
        roundedTimestamp = math.floor(timestamp)
        if self.timestampOfSlice is None:
            #first itteration
            self.timestampOfSlice = roundedTimestamp
            if self.relativeSliceAddress is None:
                self.relativeSliceAddress = 0
            self.sliceEndTimestamp = self.timestampOfSlice + TEN_MINUTES
        if(roundedTimestamp > self.sliceEndTimestamp):
            #slice complete, push the slice and prepare to make a new one
            address = self.relativeSliceAddress  + 1
            newItem = {"initialSlice":self.initialSlice,"finalSlice":False,"recordingId":self.recordingId,
                       "data":self.sliceQueue,"sensorMetaData":self.sensorMetaData,"sliceAddress":self.relativeSliceAddress,
                       "sliceTimestampAddress":self.timestampOfSlice,"nextSliceAddress":address}
            self.relativeSliceAddress = address
            print('-------------------------pushing recording data----------------------------')
            self._internalDB.pushRecordingData(newItem)
            self.initialSlice = False
            self.timestampOfSlice = None
            del self.sliceQueue
            self.sliceQueue = []
        self.sliceQueue.append([timestamp,value])
    def stopRecorder(self):
        """
        Stops the recording action for the recorder.  This pushes all data that is queued up for the recorder to the
        database and preps the object for deconstruction
        :return: None
        :rtype: None
        """
        print('###----------------stopping recorder------------------------###')
        newItem = {"initialSlice":self.initialSlice,"finalSlice":True,"recordingId":self.recordingId,
                       "data":self.sliceQueue,"sensorMetaData":self.sensorMetaData,"sliceAddress":self.relativeSliceAddress,
                       "sliceTimestampAddress":self.timestampOfSlice,"nextSliceAddress":-1}
        self._internalDB.pushRecordingData(newItem)
        self.timestampOfSlice = self.timestampOfSlice + 1
        self.sliceEndTimestamp = self.timestampOfSlice + TEN_MINUTES
        del self.sliceQueue
        self.sliceQueue = []
        #set recording to inactive
        self._internalDB.setRecordingToInActive(self.recordingId)