__author__ = 'MattyC #1 programmer 2016'
from Sensor import Sensor
from Adafruit_I2C import Adafruit_I2C
import time
from PlotType import PlotType
class PhotoSensor(Sensor):
    def __init__(self,hexAddress,channelNumber):
        """
        Creates a photo sensor object for the channel
        :param hexAddress: hex I2C address of the device
        :type hexAddress:  hex/int
        :param channelNumber: channel number on the MMS the device is connected to
        :type channelNumber: int
        :return: photosensor object
        :rtype: PhotoSensor
        """
        #super(PhotoSensor, self).__init__(hexAddress,channelNumber)
        self._address = hexAddress
        self.recorder = None
        self.hasRecording = False
        self.channelNumber = channelNumber
        self._internalDevice = Adafruit_I2C(hexAddress,busnum=2)
        self.sensorName = 'Photo Sensor V1.01'
        self.sensorReadingType = 'LIGHT'
        self.plotType = PlotType.TimeSeries
        self.InputAndOutputControl = False
    def getData(self):
        """
        Returns a dictionary ccontaining the current value of the photosensor
        :return: a dictionary with the current data info
        :rtype: dict
        """
        value = self.getValue()
        return {'_id':self.channelNumber,'type':self.sensorReadingType,'timestamp':time.time(),'value':value}
    def getValue(self):
        """
        Gets the current value from the photosensor
        :return:  the value of the sensor
        :rtype: float

        """
        return self._internalDevice.readS8(self._address)
    def getMetaDataInfo(self):
        """
        Gets the meta data for the sensor
        :return: meta data for the sensor
        :rtype: dict
        """
        return {'_id':self.channelNumber,'sensorName':self.sensorName,
                'sensorReadingType':self.sensorReadingType,
                'plotType':self.plotType,'lastSyncTime':time.time(),'signals':1}
