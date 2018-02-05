import base64
import logging
import json
import time
from datetime import datetime
from multiprocessing import Process

import requests
from kafka import KafkaConsumer
from kafka.errors import KafkaTimeoutError
import pymongo

from history import settings

LOGGER = logging.getLogger('history.' + __name__)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.INFO)

class ConfigurationError(Exception):
    pass


class KafkaEventHandler(object):
    """
        Base callback structure for kafka events callbacks
    """
    def handle_event(self, message):
        """
            Handles a given kafka received message
            :param message The message that has been received
        """
        raise NotImplementedError("Abstract method called")

class TenancyHandler(KafkaEventHandler):

    def __init__(self):
        pass

    @staticmethod
    def _spawn_watcher(service, subject, handler):
        topic = get_topic(service, subject)
        watcher = KafkaListener(topic, handler)
        watcher.start()
        return watcher

    def tenants_bootstrap(self):
        LOGGER.debug('will bootstrap')
        target = "{}/admin/tenants".format(settings.AUTH)
        response = requests.get(target, timeout=3)
        if 200 <= response.status_code < 300:
            payload = response.json()
            LOGGER.debug('Got list of tenants', payload)
            for tenant in payload['tenants']:
                LOGGER.debug('initializing tenant %s', tenant)
                TenancyHandler._spawn_watcher(tenant, settings.DEVICE_SUBJECT, DeviceHandler())
                TenancyHandler._spawn_watcher(tenant, settings.DATA_SUBJECT, DataHandler(tenant))
        else:
            LOGGER.error('Failed to retrieve list of existing tenants (%d)', response.status_code)
            exit(1)

        return None

    def handle_event(self, message):
        """
            Given a tenancy livecyle event, spawn the needed consumers to hanle its data
            :param message Tenant lifecyle message as produced by Auth
        """
        data = json.loads(message)
        LOGGER.debug('got tenancy event for tenant: %s', data['tenant'])

        tenant = data['tenant']
        TenancyHandler._spawn_watcher(tenant, settings.DEVICE_SUBJECT, DeviceHandler())
        TenancyHandler._spawn_watcher(tenant, settings.DATA_SUBJECT, DataHandler(tenant))


class DeviceHandler(KafkaEventHandler):
    def __init__(self):
        self.db = None

    def handle_event(self, message):
        """
            Given a device management event, create (if not alredy existent) proper indexes
            to suppor the new device
            :param message Device lifecyle message, as produced by device manager
        """
        data = json.loads(message)
        LOGGER.debug('got device event %s', message)

        if self.db is None:
            self.db = pymongo.MongoClient(settings.MONGO_DB, replicaSet=settings.REPLICA_SET)
            self.db = self.db['device_history']

        collection_name = "{}_{}".format(data['meta']['service'], data['data']['id'])
        self.db[collection_name].create_index([('ts', pymongo.DESCENDING),
                                               ('attr', pymongo.DESCENDING)],
                                              unique=True)
        self.db[collection_name].create_index('ts', expireAfterSeconds=settings.DATA_EXP)


class DataHandler(KafkaEventHandler):
    def __init__(self, service):
        self.service = service
        self.db = None

    def _get_collection(self, message):
        if self.db is None:
            self.db = pymongo.MongoClient(settings.MONGO_DB, replicaSet=settings.REPLICA_SET)
        collection_name = "{}_{}".format(self.service, message['metadata']['deviceid'])
        return self.db['device_history'][collection_name]

    def handle_event(self, message):
        """
            Given a device data event, persist it to mongo
            :param message A device data event
        """
        data = json.loads(message)
        LOGGER.debug('got data event %s', message)

        timestamp = None
        try:
            # TODO document timestamp format across channels within dojot
            timestamp = data['metadata']['timestamp']
        except Exception:
            timestamp = datetime.utcnow()

        docs = []
        for attr in data['attrs'].keys():
            entry = {}
            entry['attr'] = attr
            entry['value'] = data['attrs'][attr]
            entry['device_id'] = data['metadata']['deviceid']
            entry['ts'] = timestamp
            # Should we store value type too? it is not sent by agents anymore
            # Should we store template information too? it is not sent by agents anymore
            docs.append(entry)

        db = self._get_collection(data)
        db.insert_many(docs)


class KafkaListener(Process):
    """
        Threaded abstraction for a kafka consumer
    """

    def __init__(self, topic, callback):
        """
            Constructor.
            :param callback Who to call when a new message arrives. Must be an instance of
                            KafkaEventHandler
        """
        Process.__init__(self)

        self.topic = topic
        self.broker = [settings.KAFKA_HOST]
        self.group_id = settings.KAFKA_GROUP_ID
        self.consumer = None

        # Callback must be of type KafkaEventHandler
        self.callback = callback

    def wait_init(self):
        done = False
        while not done:
            try:
                # make sure we process initial partition assignment messages
                self.consumer.poll()
                self.consumer.seek_to_end()
                done = True
            except AssertionError as error:
                LOGGER.debug('ignoring assertion error [%s] %s', self.topic, error)
                # give kafka some time to assign us a partition
                time.sleep(1)


    def run(self):
        start = time.time()
        LOGGER.info('will create consumer %s %s %s', self.broker, self.group_id, self.topic)
        self.consumer = KafkaConsumer(bootstrap_servers=self.broker, group_id=self.group_id)
        self.consumer.subscribe(topics=[self.topic])
        self.wait_init()
        LOGGER.info('kafka consumer created %s - %s', self.topic, time.time() - start)
        for message in self.consumer:
            start = time.time()
            LOGGER.debug("Got kafka event [%s] %s", self.topic, message)
            self.callback.handle_event(message.value)
            LOGGER.debug('done %s', time.time() - start)


def _get_token(service):
    """
        Given a service, return an internal token, for usage with data-broker
        :param service          Service (tenancy context) whoose subject topic is to be retrieved
        :return string          JWT token (internal)
    """
    userinfo = {
        "username": "history",
        "service": service
    }

    return "{}.{}.{}".format(base64.b64encode("model"),
                             base64.b64encode(json.dumps(userinfo)),
                             base64.b64encode("signature"))

def get_topic(service, subject, global_subject=False):
    """
        Given a service and a subject, retrieve its associated kakfa topic
        :param  service             Service (tenancy context) whoose subject topic is to be
                                    retrieved
        :param  subject             Subject that is to be retrieved
        :param  global_subject      Whether the subject is not attached to any specific tenant
        :raises ConfigurationError  If broker could not be reached
    """
    start = time.time()
    opts = "?global=true" if global_subject else ""
    target = "{}/topic/{}{}".format(settings.DATA_BROKER, subject, opts)
    jwt = _get_token(service)
    response = requests.get(target, headers={"authorization": jwt}, timeout=3)
    if 200 <= response.status_code < 300:
        payload = response.json()
        LOGGER.debug('topic acquisition took %s [%s]', time.time() - start, payload['topic'])
        return payload['topic']

    raise ConfigurationError("Topic retrieval error: {} {}".format(response.status_code,
                                                                   response.reason))

if __name__ == '__main__':
    # Spawns tenancy management thread
    tenancyTopic = get_topic('internal', settings.TENANCY_SUBJECT, True)
    if tenancyTopic is None:
        LOGGER.error("Failed to obtain tenancy lifecyle topic")
        exit(1)
    handler = TenancyHandler()
    tenantWatcher = KafkaListener(tenancyTopic, handler)
    tenantWatcher.start()
    handler.tenants_bootstrap()
    tenantWatcher.join()

    # TODO bootstrap with previously existing tenants
