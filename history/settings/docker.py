# -*- coding: utf-8 -*-
"""
Docker settings file
"""
# Local imports
# Third-party imports
import pymongo
import os


# Local imports
from base import *

replica_set = os.environ.get('MONGO_REPLICA_SET', None)

MONGO_DB = pymongo.MongoClient('mongodb', replicaSet=replica_set)
