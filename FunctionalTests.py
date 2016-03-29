__author__ = 'Matt Cordoba'
from MainChassis import MainChassis
from AnalogSensor import AnalogSensor
from TemperatureSensor import TemperatureSensor
import time
SLEEP_TIME = 1
def main():
    """
    Executes the main control loop for the MMS with all features
    :return: None
    :rtype: None
    """
    m = MainChassis()
    m.updateSensorMetaData()
    m.checkForRecordings()
    m.checkForEvents()
    i = 0
    while(True):
        t0 = time.clock()
        #print(m.getSensorData())
        if(i >= 60):
            i = 0
            print('checking for events and recordings')
            m.checkForRecordings()
            m.checkForEvents()
        try:
            m.getAndPushSensorData()
            m.handleEvents()
        except TypeError:
            pass
        m.addNewPeripherals()
        #uncomment after reading test is complete m.getAndPushSensorData()
        i += 1
        print('pushed data and handled events')
        timeLeft = t0 + SLEEP_TIME - time.clock()
        if(timeLeft > 0):
            time.sleep(timeLeft)

def testRecordingCheck():
    """
    Tests the recording feature for the mms
    :return: None
    :rtype: None
    """
    m = MainChassis()
    m.checkForRecordings()
    while(True):
        t0 = time.clock()
        m.getAndPushSensorData()
        timeLeft = t0 + SLEEP_TIME - time.clock()
        if(timeLeft > 0):
            time.sleep(timeLeft)
def testEvents():
    """
    Tests the event triggers feature on the mms
    :return: None
    :rtype: None
    """
    m = MainChassis()
    print('chassis made')
    m.checkForEvents()
    while(True):
        print('pausing for 1 seconds')
        time.sleep(1)
        print('testing event')
        m.handleEvents()
def testAnalogSensor():
    """
    Tests the analog sensor peripheral
    :return: None
    :rtype: None
    """
    a = AnalogSensor(0x48,0)
    print(a.getMetaDataInfo())
    print(a.getData())
    print(a.isRational())
    time.sleep(1)
    print(a.isRational())
    a = AnalogSensor(0x49,0)
    print(a.getMetaDataInfo())
    print(a.getData())
    print(a.isRational())
    time.sleep(1)
    print(a.isRational())
    print('doing temperature version')
    a = TemperatureSensor(0x48,0)
    print(a.getMetaDataInfo())
    print(a.getData())
    time.sleep(1)
    a = TemperatureSensor(0x49,0)
    print(a.getMetaDataInfo())
    print(a.getData())

if(__name__ == '__main__'): #for multiprocessing library in case we use it.
    #main()
    testAnalogSensor()
    #testRecordingCheck()