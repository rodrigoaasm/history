from dojotmodulepython import Messenger
from dojotmodulepython import config
import base64
import logging
import json
import time
from datetime import datetime
from dateutil.parser import parse
from multiprocessing import Process, active_children

import requests
from kafka import KafkaConsumer
from kafka.errors import KafkaTimeoutError
import pymongo
from history import conf

LOGGER = logging.getLogger('history.' + __name__)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.INFO)

db = None
client = None

def init_mongodb(collection_name=None):
    """
    MongoDB initialization

    :type collection_name: str
    :param collection_name: collection to create index 
    """
    global db
    global client
    try:
        client = pymongo.MongoClient(conf.db_host, replicaSet=conf.db_replica_set)
        db = client['device_history']
        if collection_name:
            create_indexes(collection_name)
        LOGGER.info("db initialized")
    except Exception as error:
        LOGGER.warn("Could not init mongo db client: %s" % error)

def create_indexes(collection_name):
    """
    Create index given a collection

    :type collection_name: str
    :param collection_name: collection to create index 
    """
    global db
    db[collection_name].create_index([('ts', pymongo.DESCENDING)])
    db[collection_name].create_index('ts', expireAfterSeconds=conf.db_expiration)

def enable_collection_sharding(self, collection_name):
    """
    Create index given a collection

    :type collection_name: str
    :param collection_name: collection to create index 
    """
    global db
    global client
    db[collection_name].create_index([('attr', pymongo.HASHED)])
    client.admin.command('enableSharding', self.db.name)
    client.admin.command('shardCollection', self.db[collection_name].full_name, key={'attr': 'hashed'})

def parse_message(data):
    """
    Formats message to save in MongoDB

    :type data: dict
    :param data: data that will be parsed to a format
    """
    parsed_message = dict()
    parsed_message['attrs'] = data['data']['attrs']
    parsed_message['metadata'] = dict()
    parsed_message['metadata']['timestamp'] = int(time.time() * 1000)
    parsed_message['metadata']['deviceid'] = data['data']['id']
    parsed_message['metadata']['tenant'] = data['meta']['service']
    LOGGER.info("new message is: %s" % parsed_message)
    return json.dumps(parsed_message)

def parse_datetime(timestamp):
    """
    Parses date time

    :type timestamp: timestamp
    :param timestamp: timestamp
    """
    if timestamp is None:
        return datetime.utcnow()
    try:
        val = int(timestamp)
        if timestamp > ((2**31)-1):
            return datetime.utcfromtimestamp(val/1000)
        else:
            return datetime.utcfromtimestamp(float(timestamp))
    except ValueError as error:
        LOGGER.error("Failed to parse timestamp ({})\n{}".format(timestamp, error))
    try:
        return datetime.utcfromtimestamp(float(timestamp)/1000)
    except ValueError as error:
        LOGGER.error("Failed to parse timestamp ({})\n{}".format(timestamp, error))
    try:
        return parse(timestamp)
    except TypeError as error:
        raise TypeError('Timestamp could not be parsed: {}\n{}'.format(timestamp, error))

def handle_event_data(tenant, message):
    """
        Given a device data event, persist it to mongo

        :type tenant: str
        :param tenant: tenant related to the event

        :type message: str
        :param message: A device data event
    """
    global db

    data = None
    try:
        data = json.loads(message)
        LOGGER.info("THIS IS THE DATA: %s" % data)
    except Exception as error:
        LOGGER.error('Received event is not valid JSON. Ignoring\n%s', error)
        return
    LOGGER.debug('got data event %s', message)
    metadata = data.get('metadata', None)
    if metadata is None:
        LOGGER.error('Received event has no metadata associated with it. Ignoring')
        return
    device_id = metadata.get('deviceid', None)
    if device_id is None:
        LOGGER.error('Received event cannot be traced to a valid device. Ignoring')
        return
    timestamp = parse_datetime(metadata.get('timestamp', None))
    docs = []
    for attr in data.get('attrs', {}).keys():
        docs.append({
            'attr': attr,
            'value': data['attrs'][attr],
            'device_id': device_id,
            'ts': timestamp
        })
    # Persist device status history as well
    device_status = metadata.get('status', None)
    if device_status is not None:
        docs.append({
            'status': device_status,
            'device_id': device_id,
            'ts': timestamp
        })
    if len(docs) > 0:
        try:
            collection_name = "{}_{}".format(tenant,device_id)
            db[collection_name].insert_many(docs)
        except Exception as error:
            LOGGER.warn('Failed to persist received information.\n%s', error)
    else:
        LOGGER.info('Got empty event from device [%s] - ignoring', device_id)

def handle_event_devices(tenant, message):
    """
        Given a device management event, create (if not alredy existent) proper indexes
        to suppor the new device
        
        :type tenant: str
        :param tenant: tenant related to the event

        :type message: str
        :param message Device lifecyle message, as produced by device manager
    """
    data = json.loads(message)
    LOGGER.info('got device event %s', data)
    if(data['event'] != "configure"):
        collection_name = "{}_{}".format(data['meta']['service'], data['data']['id'])
        create_indexes(collection_name)
    else:
        new_message = parse_message(data)
        handle_event_data(tenant, new_message)


def main():
    init_mongodb()
    messenger = Messenger("Persister")
    messenger.init()
    messenger.create_channel(config.dojot['subjects']['devices'], "r")
    messenger.create_channel(config.dojot['subjects']['device_data'], "r")
    messenger.on(config.dojot['subjects']['devices'], "message", handle_event_devices)
    messenger.on(config.dojot['subjects']['device_data'], "message", handle_event_data)

if __name__=="__main__":
    main()