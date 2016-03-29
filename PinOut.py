__author__ = 'mcordoba'
'''

NOT IN USE

#base pin out class
class PinOut():
    def __init__(self,idPin):
        self.idPin = idPin
        self.MAX_CHANNEL_NUMBER = 5
class SPI(PinOut):
    def __init__(self,idPin):
        super(SPI, self).__init__(idPin)

class I2C(PinOut):
    def __init__(self,idPin):
        super(I2C, self).__init__(idPin)

class DigitalOutput(PinOut):
    def __init__(self,idPin,channelNumber=1):
        super(DigitalOutput, self).__init__(idPin)
        if(channelNumber > self.MAX_CHANNEL_NUMBER):
            print('Channel Number cannot exceed ' + str(self.MAX_CHANNEL_NUMBER) + ' ..setting to max')
            channels = self.MAX_CHANNEL_NUMBER
        else:
            channels = channelNumber
class AnalogInput(PinOut):
    def __init__(self,idPin,channelNumber=1):
        super(AnalogInput, self).__init__(idPin)
        if(channelNumber > self.MAX_CHANNEL_NUMBER):
            print('Channel Number cannot exceed ' + str(self.MAX_CHANNEL_NUMBER) + ' ..setting to max')
            channels = self.MAX_CHANNEL_NUMBER
        else:
            channels = channelNumber
class DigitalInput(PinOut):
    def __init__(self,idPin,channelNumber=1):
        super(DigitalInput, self).__init__(idPin)
        if(channelNumber > self.MAX_CHANNEL_NUMBER):
            print('Channel Number cannot exceed ' + str(self.MAX_CHANNEL_NUMBER) + ' ..setting to max')
            channels = self.MAX_CHANNEL_NUMBER
        else:
            channels = channelNumber
'''