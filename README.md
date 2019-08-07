# dojot History service

This service handles all operations related to persisting and retrieving historical device
data. For more information about the usage, check the [API documentation](https://dojot.github.io/history/apiary_latest.html).

## Dependencies

- falcon
- gunicorn
- gevent
- python-dateutil
- pymongo
- requests

The setup of these dependencies are described in the following section.

## Configuration

In order to properly start History, the following variables must be set. All
values are the default ones, and they need to be modified to the services' address.

Key                         | Purpose                                                      | Default Value
----------------------------|--------------------------------------------------------------|----------------
HISTORY_DB_ADDRESS          |History database's address                                    |"mongodb"
HISTORY_DB_PORT             |History database's port                                       |27017
HISTORY_DB_REPLICA_SET      |History database's replica set address                        |None
HISTORY_DB_DATA_EXPIRATION  |Seconds before removing an entry in MongoDB                   |604800
MONGO_SHARD                 |                                                              |False
AUTH_URL                    |Auth url address                                              |"http://auth:5000"
KAFKA_ADDRESS               |Kafta address                                                 |"kafka"
KAFKA_PORT                  |Kafka port                                                    |9092
KAFKA_HOSTS                 |KAFKA_ADDRESS concatenated wiht KAFKA_PORT                    |"kafka:9092"
KAFKA_GROUP_ID              |Group ID used when creating consumers                         |"history"
DATA_BROKER_URL             |Data Broker address                                           |"http://data-broker"
DEVICE_MANAGER_URL          |Device Manager address                                        |"http://device-manager:5000"
DOJOT_SUBJECT_TENANCY       |Global subject to use when publishing tenancy lifecycle events|"dojot.tenancy"
DOJOT_SUBJECT_DEVICES       |Global subject to use when receiving device lifecycle events  |"dojot.device-manager.device"
DOJOT_SUBJECT_DEVICE_DATA   |Global subject to use when receiving data from devices        |"device-data"
DOJOT_SERVICE_MANAGEMENT    |Global service to use when publishing dojot management events |"dojot-management"

## Installation

### Standalone setup

As this service is written in **Python 2.7**, it is recommended that all packages are
installed within a [virtual environment](https://github.com/pypa/virtualenv). It can be created by:

```shell
$ virtualenv ./venv
$ source ./venv/bin/activate
```

Which will create a `venv` folder in current directory and install
basic Python packages there. The second command will set all environment
variables so that new Python packages are installed there as well.

To install all dependencies from Auth, execute the following commands.

```shell
# you may need sudo for those
$ apt-get install -y python-pip versiontools
# There is a package that is not in PyPI
$ pip install -r ./requirements/requirements.txt
$ python setup.py install
```

The last command will generate a .egg file and install it into your virtual
environment.

### Docker setup

Another alternative is to use **docker** to run the service. To build the
container, from the repository"s root:

```shell
# you may need sudo on your machine: 
# https://docs.docker.com/engine/installation/linux/linux-postinstall/
$ docker build -t <tag-for-history-docker> -f docker/history.docker .
$ docker build -t <tag-for-persister-docker> -f docker/persister.docker .
```
You can run the built containers using the following commands:

```shell
# may need sudo to run
$ docker run -i -t <tag-for-history-docker>
$ docker run -i -t <tag-for-persister-docker>
```

## How to run

For History service, just set all needed environment variables and execute:

```bash
./docker/falcon-docker-entrypoint.sh start
```

Persister is much simpler, just execute:
```bash
#python -m history.subscriber.kafkaSubscriber
$ python history/subscriber/persister.py
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
