# -*- coding: utf-8 -*-
"""
Docker settings file
"""

import os

# This file contains the default configuration values
# and configuration retrieval functions

#Logger related configuration
log_level = os.environ.get("LOG_LEVEL","INFO")

# mongo related configuration
db_address = os.environ.get("HISTORY_DB_ADDRESS", "mongodb")
db_port = os.environ.get("HISTORY_DB_PORT", 27017)
db_host = "" + db_address + ":" + str(db_port)
db_replica_set = os.environ.get("HISTORY_DB_REPLICA_SET", None)
db_expiration = os.environ.get('HISTORY_DB_DATA_EXPIRATION', 604800)
db_shard = os.environ.get('MONGO_SHARD', False)

# Kafka configuration
kafka_address = os.environ.get("KAFKA_ADDRESS", "kafka")
kafka_port = os.environ.get("KAFKA_PORT", 9092)
kafka_host = "" + kafka_address + ":" + str(kafka_port)
kafka_group_id = os.environ.get('KAFKA_GROUP_ID', "history")

# Global subject to use when publishing tenancy lifecycle events
dojot_subject_tenancy = os.environ.get("DOJOT_SUBJECT_TENANCY", "dojot.tenancy")

# Global subject to use when listening to device CRUD events
dojot_subject_device = os.environ.get('DOJOT_SUBJECT_DEVICES', "dojot.device-manager.device")

# Global subject to use when listening to device data events
dojot_subject_device_data = os.environ.get('DOJOT_SUBJECT_DEVICE_DATA', "device-data")

# Global service to use when publishing dojot management events
# such as new tenants
dojot_service_management = os.environ.get("DOJOT_SERVICE_MANAGEMENT",
                                          "dojot-management")

#
# Other dojot services
#

# Kafka topic (subject) manager
data_broker_url = os.environ.get("DATA_BROKER_URL", "http://data-broker")
# auth related configuration
auth_url = os.environ.get('AUTH_URL', "http://auth:5000")
# device-manager URL
device_manager_url = os.environ.get('DEVICE_MANAGER_URL', "http://device-manager:5000")
