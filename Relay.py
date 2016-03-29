__author__ = 'Matt Cordoba'

from Sensor import Sensor
import Adafruit_BBIO.GPIO as GPIO
import time
from PlotType import PlotType
IO_COMMAND_PINS = {0:'P9_23',1:'P9_30',2:'P8_8',3:'P8_11'}
class Relay(Sensor):
    def __init__(self,hexAddress,channelNumber):
        """
        Creates a relay peripheral object
        :param hexAddress: the hex address for the relay peripheral on the I2C bus
        :type hexAddress: hex/int
        :param channelNumber: the channel number, indexed from 0, that the device is currently connected to
        :type channelNumber: int
        :return: relay sensor peripheral
        :rtype: Relay
        """
        #super(TemperatureSensor, self).__init__(hexAddress,channelNumber)
        self._address = hexAddress
        self.recorder = None
        self.hasRecording = False
        self.channelNumber = channelNumber
        self._commandPin = IO_COMMAND_PINS[self.channelNumber]
        self.sensorName = 'AC Relay Control V1.01'
        self.sensorReadingType = 'DIGITAL'
        self.plotType = PlotType.TimeSeriesDigitalControl
        self.InputAndOutputControl = True
        self.state = False #the relay is Active Low, for the user sake here GPIO.HIGH = False, GPIO.LOW = True (opposite)
        self._setupCommandPin()
    def _setupCommandPin(self):
        """
        Sets the GPIO pins on the BBB to handle digital outputs using the Adafruit_BBIO library
        :return: None
        :rtype: None
        """
        GPIO.setup(self._commandPin,GPIO.OUT)
        GPIO.output(self._commandPin,GPIO.HIGH)
    def getData(self):
        """
        Gets the current data status of the relay sensor
        :return: dictionary containing, timestamp, value and some meta data about the sensor
        :rtype: dict
        """
        value = self.getValue()
        doc = {'_id':self.channelNumber,'type':self.sensorReadingType,'timestamp':time.time(),'value':value}
        return doc
    def getValue(self):
        """
        get the digital value of the relay status
        :return: the relay status
        :rtype: int
        """
        return int(self.state)
    def handleCommands(self,commands):
        """
        handles commands from the database to change the relay status
        :param commands: a dictionary containing command instructions
        :type commands: dict
        :return: None
        :rtype: None
        """
        digitalState = bool(commands['digitalState'])
        if(digitalState != self.state):
            self.command(digitalState)
            self.state = digitalState
    def command(self,state):
        """
        commands the relay module to a state.  Note: the relay is active LOW, so the state is inverted (state =high
        means GPIO=low)
        :param state: the state to command the relay to
        :type state: bool
        :return:None
        :rtype: None
        """
        if(state):
            GPIO.output(self._commandPin,GPIO.LOW)
        else:
            GPIO.output(self._commandPin,GPIO.HIGH)
    def getMetaDataInfo(self):
        """
        get the meta data for relay sensor
        :return: meta data for the sensor
        :rtype: dict
        """
        return {'_id':self.channelNumber,'sensorName':self.sensorName,
                'sensorReadingType':self.sensorReadingType,
                'plotType':self.plotType,'lastSyncTime':time.time(),'signals':1}