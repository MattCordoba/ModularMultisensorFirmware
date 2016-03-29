__author__ = 'Matt Cordoba'
from pymongo import MongoClient
import mysql.connector
from Recording import Recording
from datetime import datetime
import time
#TODO: encrpt DB credentials
class Database():
    def __init__(self,serialNumber):
        """
        Connects to MySQL database and Mongo database and returns database object
        :param serialNumber: serial number of the MMS unit
        :type serialNumber: str
        :return: object representing database connection to both MySQL and MongoDB
        :rtype: Database
        """

        self._sqlConnect()
        self._connect()
        self._setAPIKey(serialNumber)
        self._setupCollections()
    def _setAPIKey(self,serialNumber):
        """
        Gets and sets the API key for the MMS unit serial # by querying MySQL
        :param serialNumber: serial # for the unit
        :type serialNumber: str
        :return: None
        :rtype: NOne
        """
        query = 'SELECT a.apiKey,a.userDBHash,a.id,m.id FROM innodb.kushmobile_mmschassis as m INNER JOIN innodb.kushmobile_apikey as a on m.pairedAPIKey_id = a.id WHERE serialNumber = "%s"' % serialNumber
        self._sqlcursor.execute(query)
        row = self._sqlcursor.fetchone()
        self._apiKey = row[0]
        self._userDBHash = row[1]
        self._apiKeyId = row[2]
        self._unitID = row[3]
    def _sqlConnect(self):
        """
        connect to mysql via mysql connector
        :return: None
        :rtype: None
        """
        self._sqlcnx = mysql.connector.connect(host='',
                                               port=3306,user='',password='',database='')
        self._sqlcursor = self._sqlcnx.cursor()

    def getAddressConstructorType(self,address):
        """
        Gets the contructor to use a sensor address off of the I2C bus
        :param address: address detected on I2C
        :type address: hex/integer
        :return: name of the sensor contructor to use
        :rtype: str
        """
        #print('finding address for ' + str(address))
        query = 'SELECT kushmobile_sensor.sensorName FROM innodb.kushmobile_sensor WHERE identificationAddress = %i' % address
        #print(query)
        self._sqlcursor.execute(query)
        data = self._sqlcursor.fetchone()
        sensorName = data[0]
        return sensorName

    def _setupCollections(self):
        """
        creates reference to all the MongoDB collections to be used and sets them as class variables.
        Uses the db hash which is linked to the api key for the MMS unit
        :return: None
        :rtype: None
        """
        MONGO_DB_COLLECTIONS = {
            'currentDataCollection':'currentData_',
            'sensorDataCollection':'sensorData_',
            'recordingDataCollection':'recordingData_',
            'commandDataCollection':'commandData_'
        }
        self.collections = {}
        self.collections['DATA'] = self.db[MONGO_DB_COLLECTIONS['currentDataCollection'] + self._userDBHash]
        self.collections['SENSOR_INFO'] = self.db[MONGO_DB_COLLECTIONS['sensorDataCollection'] + self._userDBHash]
        self.collections['RECORDING_DATA'] = self.db[MONGO_DB_COLLECTIONS['recordingDataCollection'] + self._userDBHash]
        self.collections['COMMAND_DATA'] = self.db[MONGO_DB_COLLECTIONS['commandDataCollection'] + self._userDBHash]
    def _connect(self):
        """
        connects to mongo database
        :return: None
        :rtype: None
        """
        #TODO: make this secret
        MONGO_DB_CREDENTIALS = {
            'ENGINE': '',
            'NAME': '',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',   # Or an IP Address that your DB is hosted on
            'PORT': ''
        }
        URI = 'mongodb://' + MONGO_DB_CREDENTIALS['USER'] + ':' + MONGO_DB_CREDENTIALS['PASSWORD'] + \
              '@' + MONGO_DB_CREDENTIALS['HOST'] + ':' + MONGO_DB_CREDENTIALS['PORT'] +'/' + MONGO_DB_CREDENTIALS['NAME']
        self.client = MongoClient(URI)
        self.db = self.client[MONGO_DB_CREDENTIALS['NAME']]
    def _insert(self,collectionKey,dataDictArray):
        """
        General function for inserting into mongoDB
        :param collectionKey: key of the collection to insert to
        :type collectionKey: str
        :param dataDictArray: document to insert into mongoDB
        :type dataDictArray: dict/json
        :return:None
        :rtype: None
        """
        self.collections[collectionKey].insert(dataDictArray)
    def _update(self,collectionKey,query,updateDoc):
        """
        General function for update to mongodb
        :param collectionKey: string key of the collection to update to
        :type collectionKey: str
        :param query: query dict of the objects to update with updateDoc
        :type query: dict
        :param updateDoc: fields to re-set in mongodb, with values
        :type updateDoc: dict
        :return: None
        :rtype: None
        """
        self.collections[collectionKey].update(query,{'$set':updateDoc})
    def _updateUnset(self,collectionKey,query,updateDoc):
        """
        General function to unset vales from a Mongo collection
        :param collectionKey: string key of the collection to update to
        :type collectionKey: str
        :param query: query dict of the objects to update with updateDoc
        :type query: dict
        :param updateDoc: fields to un-set in mongodb, with values
        :type updateDoc: dict
        :return: None
        :rtype: None
        """
        self.collections[collectionKey].update(query,{'$unset':updateDoc})
    def pushData(self,dataDictArray):
        """
        Push sensor data to mongo db
        :param dataDictArray: document to push to mongodb
        :type dataDictArray: dict
        :return: None
        :rtype: None
        """
        self._insert('DATA',dataDictArray)
    def pushRecordingData(self,dataDictArray):
        """
        push document containg recording data to mongo db
        :param dataDictArray: recording document to push
        :type dataDictArray: dict
        :return: None
        :rtype: None
        """
        self._insert('RECORDING_DATA',dataDictArray)
    def insertSensorMetaData(self,metaDataDictArray):
        """
        insert new meta data for sensor to mongo
        :param metaDataDictArray: metadata document to insert
        :type metaDataDictArray: dict
        :return: None
        :rtype: None
        """
        self._insert('SENSOR_INFO',metaDataDictArray)
    def updateSensorMetaData(self,jsonDoc,channelNumber):
        """
        Update sensor meta data for a channel on MMS unit
        :param jsonDoc: metadata document to set for the channel
        :type jsonDoc: dict
        :param channelNumber: channel # of the MMS unit to set
        :type channelNumber: int
        :return: None
        :rtype: None
        """
        self._update('SENSOR_INFO',{'_id':channelNumber},jsonDoc)
    def unsetSensorMetaData(self,jsonDoc,channelNumber):
        """
        Set metadata for a channel to null (nothing connected)
        :param jsonDoc: metadata document containing null set data
        :type jsonDoc: dict
        :param channelNumber:  channel # of sensor to unset
        :type channelNumber: int
        :return: None
        :rtype: None
        """
        self._updateUnset('SENSOR_INFO',{'_id':channelNumber},jsonDoc)
    def updateData(self,jsonDoc,channelNumber):
        """
        Update the data document at a channel #
        :param jsonDoc: document containg the new value to update to data collection
        :type jsonDoc:  dict
        :param channelNumber: channel # of sensor
        :type channelNumber:  int
        :return: None
        :rtype: None
        """
        self._update('DATA',{'_id':channelNumber},jsonDoc)
    def getRecordingAddress(self,recordingId):
        """
        Gets the slice address for a recording id still in progress
        :param recordingId: the MySQL recording id assigned to the recording
        :type recordingId: int
        :return: None
        :rtype: None
        """
        query = {'recordingId':recordingId}
        columns = {'sliceAddress':1}
        cursor = self.collections['RECORDING_DATA'].find(query,columns).sort('sliceAddress',-1).limit(1)
        address = None
        for doc in cursor:
            address = doc['sliceAddress']
        return address
    def getSensorCommands(self):
        """
        Gets all the sensor command sent from the application for two-way communication
        :return: None
        :rtype: None
        """
        collection = self.collections['COMMAND_DATA']
        return list(collection.find())
    def checkForRecordings(self):
        """
        Checks for new recording set by the front end application that need to be bound to sensor object
        :return: list of new recordings to add to sensors
        :rtype: Array/list of Recording objects
        """
        query = 'SELECT kushmobile_recording.startDateTime,kushmobile_recording.endDateTime' \
                ',kushmobile_recording.channelNumber,kushmobile_recording.id FROM innodb.kushmobile_recording ' \
                'WHERE apiKey_id = %i AND isActive = 1 AND endDateTime >= (NOW()-interval 8 hour)' % self._apiKeyId
        print(query)
        self._sqlcursor.execute(query)
        data = self._sqlcursor.fetchall()
        recordings = {}
        for d in data:
            #d[0] = startDateTime
            #d[1] = endDateTime
            #d[2] = channelNumber
            #d[3] = id
            startDateTime = time.mktime(d[0].timetuple())
            endDateTime = time.mktime(d[1].timetuple())
            r = Recording(d[3],startDateTime,endDateTime,self._apiKey,d[2],self)

            #########################################################################################################
            #        now we must test if the recordings have already began and initialize them has such             #
            #        this covers the corenr case where the user shutdown the MMS while a recording was running      #
            #########################################################################################################
            address = self.getRecordingAddress(r.recordingId)
            if(address is not None):
                r.setSliceAddress(address)
            recordings[d[2]] = r ####         recordings keyed by channel        ####
        return recordings
    def setRecordingToInActive(self,recordingId):
        """
        Sets a recording to complete once it has been completed by a sensor
        :param recordingId: MySQL id for the recording
        :type recordingId: int
        :return: None
        :rtype: None
        """
        query = 'UPDATE kushmobile_recording SET isActive = 0 WHERE id = % i' % recordingId
        self._sqlcursor.execute(query)
        self._sqlcnx.commit()
    def checkForEvents(self):
        """
        Gets new events for the MMS unit that need to be added
        :return: data regarding new events that need to be added to the MMS unit
        :rtype: list of dict objects containing info about the event
        """
        query = 'SELECT * FROM innodb.kushmobile_eventtrigger as et ' \
                'INNER JOIN innodb.kushmobile_conditions as c ON et.condition_id = c.id ' \
                'INNER JOIN innodb.kushmobile_sensoroutputtype as ot ON et.outputType_id = ot.id ' \
                'WHERE et.isEnabled = 1 AND et.isActive = 1 AND et.mmsunit_id = %i' % self._unitID

        self._sqlcursor.execute(query)
        data = self._sqlcursor.fetchall()
        events =[]
        for d in data:
            struct = {}
            struct['inputSensorChannel'] = d[1]
            struct['inputType'] = d[8]
            struct['outputSensorChannel'] = d[4]
            struct['outputType'] = d[17]
            struct['conditionalString'] = str(d[14])
            struct['threshold'] = d[3]
            struct['eventID'] = d[0]
            events.append(struct)
        return events