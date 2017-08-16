# -*- coding: utf-8 -*-
"""
Docker settings file
"""
# Local imports
# Third-party imports
import pymongo


# Local imports
from base import *

MONGO_DB = pymongo.MongoClient('mongodb')
