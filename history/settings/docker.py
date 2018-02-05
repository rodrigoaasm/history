# -*- coding: utf-8 -*-
"""
Docker settings file
"""
# Local imports
import os
# Third-party imports
# Local imports
from history.settings.base import *

MONGO_DB = os.environ.get('MONGO_DB', 'mongodb')
REPLICA_SET = os.environ.get('MONGO_REPLICA_SET', None)

DATA_EXP = int(os.environ.get('DATA_EXP', '604800'))

AUTH = os.environ.get('AUTH', "http://auth:5000")
DATA_BROKER = os.environ.get('DATA_BROKER', "http://data-broker")
KAFKA_HOST = os.environ.get('KAFKA_HOST', "kafka:9092")
KAFKA_GROUP_ID = os.environ.get('KAFKA_GROUP_ID', "history")

TENANCY_SUBJECT = os.environ.get('TENANCY_SUBJECT', "dojot.tenancy")
DEVICE_SUBJECT = os.environ.get('DEVICE_SUBJECT', "dojot.device-manager.device")
DATA_SUBJECT = os.environ.get('DATA_SUBJECT', "device-data")
