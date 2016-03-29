__author__ = 'Shayan,MattyC_bestprogrammer_North_america'
from Sensor import Sensor
from Adafruit_I2C import Adafruit_I2C
import time
from PlotType import PlotType
class TemperatureSensor(Sensor):
    def __init__(self,hexAddress,channelNumber):
        """
        Creates a tempearture sensor peripheral
        :param hexAddress: the I2C address of the device on the bus
        :type hexAddress: hex/int
        :param channelNumber: the channel # of the device on the MMS unit
        :type channelNumber: int
        :return: TemperatureSensor object
        :rtype: TemperatureSensor
        """
        #super(TemperatureSensor, self).__init__(hexAddress,channelNumber)
        self._address = hexAddress
        self.recorder = None
        self.hasRecording = False
        self.channelNumber = channelNumber
        self._internalDevice = Adafruit_I2C(hexAddress,busnum=2)
        self.sensorName = 'Temperature Sensor V1.01'
        self.sensorReadingType = 'TEMPERATURE'
        self.plotType = PlotType.TimeSeries
        self.InputAndOutputControl = False
    def getData(self):
        """
        Gets the value and timestamp reading of the sensor (and some metadata) and packages it in a dictionary
        to prepare to be pushed to the database
        :return: Dictionary contianing the value, timestamp and some meta data
        :rtype: dict
        """
        value = self.getValue()
        return {'_id':self.channelNumber,'type':self.sensorReadingType,'timestamp':time.time(),'value':value}
    def getValue(self):
        """
        Gets the value from the I2C chip that the temperature sensor is connected to
        :return: float value of the temperature sensor in degrees C
        :rtype: float
        """
        bytes = self._internalDevice.readList(self._address,2)
        value = float(bytes[0]) + float(bytes[1])/2**8
        return value
    def getMetaDataInfo(self):
        """
        gets the meta data information for the sensor
        :return: meta data of the sensor
        :rtype: dict
        """
        return {'_id':self.channelNumber,'sensorName':self.sensorName,
                'sensorReadingType':self.sensorReadingType,
                'plotType':self.plotType,'lastSyncTime':time.time(),'signals':1}
