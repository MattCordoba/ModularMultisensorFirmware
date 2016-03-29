__author__ = 'ShayanRezaie,MattyCFireMixes,JDuece1994@hotmail.com'

from Sensor import Sensor
from TemperatureSensor import TemperatureSensor
from PhotoSensor import PhotoSensor
from AnalogSensor import AnalogSensor
import Adafruit_BBIO.GPIO as GPIO
from Database import Database
import commands
from ast import literal_eval

from EventTrigger import EventTrigger
from Relay import Relay
POWER_PINS = {0:'P8_14', 1:'P8_15', 2:'P8_16', 3:'P8_17'}
#CONNECTED_PINS = {0:'P9_25', 1:'P9_41', 2:'P8_9', 3:'P8_12'}
CONNECTED_PINS = {0:'P9_25', 1:'P9_42',2:'P8_13', 3:'P8_12'}
class MainChassis():
    def __init__(self):
        """
        Handles initilizing the initilal state of the MMS, including connecting to the database
        as well as detecting the connected sensors
        :return: an object representing the MMS unit
        :rtype: MainChassis
        """
        self.isConnected = dict()
        self.sensors = dict()
        self.events = dict()
        self.connectedAddresses = dict()
        self._parseUnitInfo()
        self._configurationSensors = dict()
        self._setupDB()
        self._setupPins()
        self._initPeripherals()

    def _setupDB(self):
        """
        Connects to the database by adding a reference to a database object (which connects to both MySQL + MongoDB)
        :return: None
        :rtype: None
        """
        self._internalDB = Database(self.serialNumber)

    def _parseUnitInfo(self):
        """
        Gathers meta data about the unit from a txt file stored in the device
        :return: None
        :rtype: None
        """
        with open('unitinfo.txt') as f:
            lines = f.readlines()
            self.serialNumber = lines[0].split(':')[1]
        f.close()

    def _setupPins(self):
        """
        Configures all the GPIO pins used in MMS to be GPIO
        :return: None
        :rtype:
        """
        # set pins to GPIO.OUT and High
        for pin in POWER_PINS.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)
        # set Connected_pins as inputs
        for pin in CONNECTED_PINS.values():
            GPIO.setup(pin, GPIO.IN)
    #Detects if a peripheral is connected to a port or not
    def _detectPeripherals(self):
        """
        Uses the detect pin on each channel to determine if a peripheral is currently connected on that channel
        :return: None
        :rtype: None
        """
        for channelNumber,pin in CONNECTED_PINS.items():
            print('Channel ' + str(channelNumber) + ' is :')
            print(GPIO.input(pin))
            if GPIO.input(pin):
                # identify the p
                self.isConnected[channelNumber]= True
            else:
                self.isConnected[channelNumber]= False
        print('connected status is :')
        print(self.isConnected)
    #return the number of peripherals connected
    def _initPeripherals(self):
        """
        initialzes the init state of all channels on the unit
        :return: None
        :rtype: None
        """
        self._detectPeripherals()
        self._initSensors()
    def _initSensors(self):
        """
        Sequentially reads all connected channels by turning off all byquad channels, turning on channel i and sensing
        the detected id on the I2C bus.  It then creates an object and stores it at the channel #
        :return: None
        :rtype: None
        """
        for channelNumber,valid in self.isConnected.items():
            if(valid):
                self._powerOffAllChannels()
                self._powerChannel(channelNumber)
                addreses = self._detectI2CBus()
                if(len(addreses) == 0):
                    print('no perihperals seem to be connected to this MMS')
                    break
                address = addreses[0] #should only be one address in this case
                sensor = self._getSensorType(address,channelNumber)
                self.connectedAddresses[channelNumber] = address
                if(sensor is not None):
                    self.sensors[channelNumber] = sensor
        self._powerOnAllChannels()
        print(self.sensors)
    def addNewPeripherals(self):
        """
        Detects if the channel status has been changed sense last read
        :return:
        :rtype:
        """
        changedStatus = False
        for channelNumber,pin in CONNECTED_PINS.items():
            connected = GPIO.input(pin)
            if(connected):
               if(not self.isConnected[channelNumber]):
                    print('new peripheral has been detect to be connected by channelNumber ' + str(channelNumber))
                    self.isConnected[channelNumber] = True
                    changedStatus = True
            else:
                if(self.isConnected[channelNumber]):
                    print('new peripheral has been detect to be connected by channelNumber ' + str(channelNumber))
                    self.isConnected[channelNumber] = False
                    changedStatus = True
        if(changedStatus):
            self._initSensors()
            self.updateSensorMetaData()
            self.events = dict()
            self.checkForRecordings()
            self.checkForEvents()
        else:
            print('no peripheral status change')
    def _hardcodeInitPeripherals(self):
        self._detectPeripherals()
        for channelNumber,valid in self.isConnected.items():
            if(valid):
                sensor = TemperatureSensor(0x41,channelNumber)
                self.connectedAddresses[channelNumber] = 0x41
                if(sensor is not None):
                    self.sensors[channelNumber] = sensor
    def _countPeripherals(self):
        return sum(self.isConnected.values())

    def _getSensorType(self,address,channelNumber):
        #TODO: Can we pull the contructor info directly off the cloud so we dont have to code this???
        sensorName = self._internalDB.getAddressConstructorType(address)
        print('For the address of ' + str(address) + ' I will use the sensor name' + sensorName)
        '''
        print('hardcoded the sensor -channels')
        if(channelNumber == 0):
            sensorName = 'Temperature Sensor V1.01'
            address = 0x48
        elif(channelNumber == 1):
            sensorName = 'Photo Sensor V1.01'
            address = 0x23
        elif(channelNumber == 2):
            sensorName = 'Analog Sensor V1.01'
            address = 0x49
        '''
        if(sensorName == 'Temperature Sensor V1.01'):
            return TemperatureSensor(address,channelNumber)
        elif(sensorName == 'Photo Sensor V1.01'):
            return PhotoSensor(address,channelNumber)
        elif(sensorName == 'Analog Sensor V1.01'):
            return AnalogSensor(address,channelNumber)
        elif(sensorName == 'AC Relay Control V1.01'):
            return Relay(address,channelNumber)
        else:
            print('invalid sensor name')
            return None

    def _powerOffAllChannels(self):
        for channelNumber, powerPin in POWER_PINS.items():

            GPIO.output(powerPin,GPIO.LOW)

    def _powerChannel(self,channelNumber):
        GPIO.output(POWER_PINS[channelNumber],GPIO.HIGH)

    def _powerOnAllChannels(self):
        for channelNumber, powerPin in POWER_PINS.items():
            GPIO.output(powerPin,GPIO.HIGH)
    def _detectI2CBus(self):
        returnInt,resultString = commands.getstatusoutput('i2cdetect -y -r 2')
        foundAddresses = []
        print(resultString)
        lines = resultString.split('\n')[1:] #remove row header
        for l in lines:
            l = l.strip() #remove white space on ends
            spots = l.split(' ')[1:] #remove column header
            for s in spots:
                s = s.strip()
                if(s != 'UU' and s != '--' and s != ''):
                    foundAddresses.append(literal_eval('0x' + s))
        return foundAddresses
    def read(self,channelNumber):
        if(not self.isConnected[channelNumber]):
            print('invalid...channel is not connected..returning none')
            return None
        return self.sensors[channelNumber].getData()
    def writeRawDict(self,collectionKey,jsonDocument):
        self._internalDB._insert(collectionKey,jsonDocument)
    def getSensorData(self):
        sensorData = []
        for channelNumber,sensorObj in self.sensors.items():
            if(self.isConnected[channelNumber]):
                sensorData.append(sensorObj.getData())
        return sensorData
    def getAndPushSensorData(self):
        sensorCommands = self._internalDB.getSensorCommands()
        for channelNumber,sensorObj in self.sensors.items():
            if(self.isConnected[channelNumber]):
                #print('pushing data ;)')
                data = sensorObj.getData()
                if(sensorObj.hasRecording):
                    recorder = sensorObj.recorder
                    if(not recorder.isComplete()):
                        #push data to recorder
                        #print('recorder handling data')
                        recorder.handleData(data)
                    else:
                        #end recorder
                        recorder.stopRecorder()
                        sensorObj.setRecorder(None)
                self._internalDB.updateData(data,channelNumber)
                if(sensorObj.InputAndOutputControl):
                    print('commands for output sensor received...sending')
                    sensorObj.handleCommands(sensorCommands[channelNumber])

        #self._internalDB.pushData(self.getSensorData())
    def testForNewDevices(self):
        addresses = self._detectI2CBus()
        currentAddresses = self.connectedAddresses.values()
        for address in addresses:
            if(address not in currentAddresses):
                print('found new address.....need to implement detection method')

    def updateSensorMetaData(self):
        sensorInfo = []
        print('updating sensor meta data')
        for channelNumber,status in self.isConnected.items():
            if(self.isConnected[channelNumber]):
                #print(self.sensors)
                sensorObj = self.sensors[channelNumber]
                metaData = sensorObj.getMetaDataInfo()
                #print(metaData)
                self._internalDB.updateSensorMetaData(metaData,channelNumber)
            else:
                print('updating null sensor data')
                d = {'sensorName':"","signals":"",
                'sensorReadingType':"",
                'plotType':"",'lastSyncTime':""}
                self._internalDB.unsetSensorMetaData(d,channelNumber)
        #self._internalDB.updateSensorMetaData(sensorInfo)
    def checkForRecordings(self):
        print('checking for recordings.....')
        recordings = self._internalDB.checkForRecordings()
        print(recordings)
        if(recordings is not None):
            for channelNumber,recorder in recordings.items():

                if(self.isConnected[channelNumber]):
                    if(not self.sensors[channelNumber].hasRecording):
                        self.sensors[channelNumber].setRecorder(recorder)
                    else:
                        print('Recording of id ' + str(recorder.recordingId) +
                              ' was not set because sensor already has a recording of id ' +
                              str(self.sensors[channelNumber].recorder.recordingId))
    def checkForEvents(self):
        print('checking for events')
        events = self._internalDB.checkForEvents()
        if(events is not None):
            for struct in events:
                if struct['eventID'] not in self.events:
                    #add the event
                    #elf,inputSensor,inputType,outputSensor,outputType,conditionalString,threshold,id):
                    try:
                        e = EventTrigger(self.sensors[struct['inputSensorChannel']],struct['inputType'],
                                         self.sensors[struct['outputSensorChannel']],struct['outputType'],
                                         struct['conditionalString'],float(struct['threshold']),struct['eventID'],self._internalDB)
                        self.events[e.id] = e
                    except KeyError:
                        print('One of the input or output channel select in the event is not connected...please try again')

            print(self.events)
    def handleEvents(self):
        for eventID,event in self.events.items():
            event.handleEvent()

