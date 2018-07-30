# dojot History service

This service handles all operations related to persisting and retrieving historical device
data.

## Installation

As this service is written in Python 2.7, it is recommended that all packages are
installed within a virtual environment. This can be created by:

```shell
virtualenv ./venv
source ./venv/bin/activate
```

Which will create a `venv` folder in current directory and install a bunch of
basic Python packages there. The second command will set all environment
variables so that new Python packages are installed there as well.

To install all dependencies from Auth, execute the following commands.

```shell
# you may need sudo for those
apt-get install -y python-pip versiontools
# There is a package that is not in PyPI
pip install -r ./requirements/requirements.txt
python setup.py install
```

The last command will generate a .egg file and install it into your virtual
environment.

Another alternative is to use docker to run the service. To build the
container, from the repository"s root:

```shell
# you may need sudo on your machine: 
# https://docs.docker.com/engine/installation/linux/linux-postinstall/
docker build -t <tag> -f docker/history.docker .
docker build -t <tag> -f docker/persister.docker .
```

## Configuration

In order to properly start History, the following variables can be set. All
values are the default ones.

```shell
#####
## Config for History service
#####

#
# Configuration for MongoDB access
#

# MongoDB address
export HISTORY_DB_ADDRESS="mongodb"
# MongoDB port
export HISTORY_DB_PORT=27017
# How many seconds before remove an entry in MongoDB
export HISTORY_DB_DATA_EXPIRATION=604800

#
# Other services
#
# Where Auth is
export AUTH_URL="http://auth:5000"

```

In the same way, you could set all the following variables that affect how
Persister works.

```shell

#####
## Config for Persister service
#####

#
# Configuration for MongoDB access
#

# MongoDB address
export HISTORY_DB_ADDRESS="mongodb"
# MongoDB port
export HISTORY_DB_PORT=27017
# How many seconds before remove an entry in MongoDB
export HISTORY_DB_DATA_EXPIRATION=604800

#
# Other services
#

# Kafka address
export KAFKA_ADDRESS="kafka"
# Kafka port
export KAFKA_PORT=9092
# Kafka group ID to be used when creating consumers
export KAFKA_GROUP_ID="history"
# Where Data Broker is
export DATA_BROKER_URL="http://data-broker"
# Where Auth is
export AUTH_URL="http://auth:5000"


#
# dojot variables
#

# Global subject to use when publishing tenancy lifecycle events
export DOJOT_SUBJECT_TENANCY="dojot.tenancy"
# Global subject to use when receiving device lifecycle events
export DOJOT_SUBJECT_DEVICES="dojot.device-manager.device"
# Global subject to use when receiving data from devices
export DOJOT_SUBJECT_DEVICE_DATA="device-data"
# Global service to use when publishing dojot management events
# such as new tenants
export DOJOT_SERVICE_MANAGEMENT="dojot-management"

```

## How to run

For History service, just set all needed environment variables and execute:

```bash
./docker/falcon-docker-entrypoint.sh start
```

Persister is much simpler, just execute:
```bash
python -m history.subscriber.kafkaSubscriber
```

## API

The API documentation for this service is written as API blueprints.
To generate a simple web page from it, one may run the commands below.

```shell
npm install -g aglio # you may need sudo for this

# static webpage
aglio -i docs/history.apib -o docs/history.html

# serve apis locally
aglio -i docs/history.apib -s
```

## Tests

History has some automated test scripts. We use `Dredd
<http://dredd.org/en/latest/>`_ to execute them.