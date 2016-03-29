__author__ = 'mcordoba'
#base class for all peripheral sensors
from threading import Thread,Lock
import time
import Adafruit_BBIO.GPIO as GPIO
from Adafruit_I2C import Adafruit_I2C
class Sensor():
    def __init__(self,hexAddress,channelNumber):
        """
        Abstract/Base class for all of the peripherals. Base constructor that can be called
        :param hexAddress: hex address of the device on the I2C bus
        :type hexAddress: hex/int
        :param channelNumber: channel # of the device on the MMS unit
        :type channelNumber:  int
        :return: Sensor object
        :rtype: Sensor
        """
        self.channelNumber = channelNumber
        self._address = hexAddress
    def getID(self):
        """
        Gets the hex I2C ID of the sensor
        :return: hex I2C id of the sensor
        :rtype: hex/int
        """
        return self._address
    def setRecorder(self,recorder):
        """
        Sets a recording for the sensor
        :param recorder: recorder object to bind to the sensor
        :type recorder: Recording
        :return: None
        :rtype: None
        """
        if recorder is None:
            self.hasRecording = False
            recorder = self.recorder
            self.recorder = None
            del recorder #clean up memory space
        else:
            self.hasRecording = True
            self.recorder = recorder
            self.recorder.setSensorMetaData(self.getMetaDataInfo())
    def getData(self):
        """
        Abstract function that must be overridden by classes that inherit from this
        :return: None
        :rtype: None
        """
        raise NotImplementedError
    def getValue(self):
        """
        Abstract function that must be overridden by classes that inherit from this
        :return: None
        :rtype: None
        """
        raise NotImplementedError
    def getMetaDataInfo(self):
        """
        Abstract function that must be overridden by classes that inherit from this
        :return: None
        :rtype: None
        """
        raise NotImplementedError
