# **History and Persister services**

The _History_ and _Persister_ services can be considered as "siblings",
_History_ has the role of retrieving the historical data that was recorded in
_MongoDB_, but in order for these data to reach _MongoDB_ it was necessary for
_Persister_ to take them there.

To better understand the scenario where these two services are employed, let's exemplify the data flow:

1. The devices send their measurement data to the dojot platform through some protocol, for example, _MQTT_;
2. The data reaches a _Broker*_ designed to work with the same protocol as the device;
3. After receiving the data, the _Broker_ forwards it to _Kafka_ so that the interested services can consume it;
4. The _Persister_ service comes on the scene, which is notified by _Kafka_ when there is device data to be persisted in _MongoDB_ to create a historical basis of measurements;
5. Once _Persister_ has saved the data to _MongoDB_, the _History_ service is able to see it;
6. _History_ service provides an _endpoint_ (REST API) so that platform users can consult the historical data of measurements made by the devices, so through the _History_ it is possible to retrieve any historical data.

> (*) A Broker is a component that allows a group of devices to send their data and be managed by it, using their own native protocols.


# **Table of Contents**

- [**History and Persister services**](#history-and-persister-services)
- [**Table of Contents**](#table-of-contents)
- [**History service**](#history-service)
  - [**History service configuration**](#history-service-configuration)
  - [**How to install History service**](#how-to-install-history-service)
    - [**History service in standalone mode**](#history-service-in-standalone-mode)
    - [**History service on Docker**](#history-service-on-docker)
  - [**How to run the History service**](#how-to-run-the-history-service)
- [**Persister service**](#persister-service)
  - [**Persister service configuration**](#persister-service-configuration)
        - [Kafka related configuration](#kafka-related-configuration)
        - [MongoDB related configuration](#mongodb-related-configuration)
  - [**How to install Persister service**](#how-to-install-persister-service)
    - [**Persister service in standalone mode**](#persister-service-in-standalone-mode)
    - [**Persister service on Docker**](#persister-service-on-docker)
  - [**Running the Persister service**](#running-the-persister-service)
- [**Tests**](#tests)
- [**Dependencies**](#dependencies)
  - [**Dojot Services**](#dojot-services)
  - [**Others Services**](#others-services)
- [**Documentation**](#documentation)
  - [**Generate API documentation**](#generate-api-documentation)
- [**Issues and help**](#issues-and-help)


# **History service**

The _History_ service is used when it is necessary to obtain historical data
from devices. Through its _REST_ interface it is possible to apply filters to
obtain only the desired data from a device, like the _attributes_ to be
returned, the _time period_ in which the data was measured, the _quantity_ and
_order_ in which the data was returned.

See the skeleton of the request that can be made to _History_ service:

```HTTP
http://{host}:{port}/device/{device_id}/history?attr={attr}&dateFrom={dateFrom}&dateTo={dateTo}&lastN|firstN={lastN|firstN}
```


## **History service configuration**

The settings are made through environment variables, so we have the following:

Environment variable        | Purpose                                                      | Default Value
----------------------------|--------------------------------------------------------------|----------------
AUTH_URL                    | Auth url address                                             | "http://auth:5000"
DEVICE_MANAGER_URL          | Device Manager url address                                   | "http://device-manager:5000"
HISTORY_DB_ADDRESS          |History database's address                                    |"mongodb"
HISTORY_DB_PORT             |History database's port                                       |27017
HISTORY_DB_REPLICA_SET      |History database's replica set address                        |None
LOG_LEVEL                   | Sets the log level                                           | "INFO"
********************************************************************************

## **How to install History service**

### **History service in standalone mode**

The service is written in Python 3.6 and to run it in standalone mode you need
to install the libraries that the service depends on.
A very common problem is when we need to use different versions of the same
library in different Python projects. This can lead to conflicts between
versions and a lot of headaches for the developer. To solve this problem, the
most correct thing is to create a _virtual environment_ for each project.
Basically, a _virtual environment_ packages and stores in a specific directory
all the dependencies that a project needs, making sure that no packages are
installed directly on the operating system. Therefore, each project can have its
own environment and, consequently, its libraries in specific versions.

There are several tools that create Python _virtual environments_, one of the
most well-known is [virtualenv](https://pypi.org/project/virtualenv/).
This is what we are going to use in this example.

We will use [pip](https://pypi.org/project/pip/) (_Package Installer for Python_)
to install _virtualenv_, in this case, we will use _pip_ in version _19.0.3_.

Make sure to [install the pip]((https://pip.pypa.io/en/stable/installing/))
according to your operating system, then [install virtualenv](https://virtualenv.pypa.io/en/latest/installation.html#via-pip).
That done, we will be able to create and manage our virtual environment to run
the service.

First let's create a new _virtual environment_ using the following command:

```bash
# The most common is to create virtualenv at the
# root of the project that it will belong to.
$> virtualenv ./venv
```

After creating a _virtual environment_, we need to activate it so that we can
install the necessary project packages. For this, we use the following command:

```bash
$> source ./venv/bin/activate
```

__NOTE THAT__ to exit the _virtual environment_ we use the `deactivate` command,
as we can see below:

```bash
# When you no longer want to run the History service,
# you need to leave the virtual environment created for it:
$> deactivate ./venv
```

To install all dependencies, execute the following commands.

```bash
# Some libraries depend on the specific version of the pip:
$> python -m pip install pip==19.0.3

$> pip install versiontools

$> pip install -r ./requirements/requirements.txt
```

The next and last command will generate a
[`.egg`](http://peak.telecommunity.com/DevCenter/PythonEggs) file and install
it into your virtual environment:
~~~bash
$> python setup.py install
~~~

### **History service on Docker**

Another alternative is to use [Docker](https://www.docker.com/)  to run the
service. To build the container, from the repository's root:

```bash
# you may need sudo on your machine:
# https://docs.docker.com/engine/installation/linux/linux-postinstall/
$> docker build -t <tag-for-history-docker> -f docker/history.docker .
```

__NOTE THAT__ you can use the official images provided by dojot in its
[DockerHub page](https://hub.docker.com/r/dojot/history).

********************************************************************************

## **How to run the History service**

Beforehand, you need an already running dojot instance in your machine.
Check out the [dojot documentation](https://dojotdocs.readthedocs.io)
for more information on installation methods.

To run the _History_ service on standalone mode, just set all needed environment
variables and execute:

```bash
# from the repository's root:
$> ./docker/falcon-docker-entrypoint.sh start
```

To run the service on docker, you can use:
```bash
# may need sudo to run
$> docker run -i -t <tag-for-history-docker>
```


# **Persister service**

The _History_ service (as we saw earlier) is only capable of retrieving data from
the MongoDB instance, it is not able to store any data. It is the _Persister's_
duty to make this happen: it is notified whenever a new message has arrived in
Kafka and stores it in MongoDB.

## **Persister service configuration**

The settings are made through environment variables, so we have the following:

Environment variable        | Purpose                                                      | Default Value
----------------------------|--------------------------------------------------------------|----------------
AUTH_URL                    |Auth url address                                              |"http://auth:5000"
DATA_BROKER_URL             |Data Broker address                                           |"http://data-broker"
DEVICE_MANAGER_URL          |Device Manager address                                        |"http://device-manager:5000"
LOG_LEVEL                   |Define minimum logging level                                  |"INFO"
PERSISTER_PORT              |Port to be used by persister sevice's endpoints               |8057
DOJOT_PERSIST_NOTIFICATIONS_ONLY                   |If 'True' only the notification events are persisted, otherwise if 'False' the notification and device events are persisted.                                         |False

##### Kafka related configuration

Environment variable        | Purpose                                                      | Default Value
----------------------------|--------------------------------------------------------------|----------------
DOJOT_SERVICE_MANAGEMENT    |Global service to use when publishing dojot management events |"dojot-management"
DOJOT_SUBJECT_TENANCY       |Global subject to use when publishing tenancy lifecycle events|"dojot.tenancy"
DOJOT_SUBJECT_DEVICES       |Global subject to use when receiving device lifecycle events  |"dojot.device-manager.device"
DOJOT_SUBJECT_DEVICE_DATA   |Global subject to use when receiving data from devices        |"device-data"
KAFKA_ADDRESS               |Kafta address                                                 |"kafka"
KAFKA_PORT                  |Kafka port                                                    |9092
KAFKA_GROUP_ID              |Group ID used when creating consumers                         |"history"


##### MongoDB related configuration

Environment variable        | Purpose                                                      | Default Value
----------------------------|--------------------------------------------------------------|----------------
HISTORY_DB_ADDRESS          | History database's address                                   | "mongodb"
HISTORY_DB_PORT             | History database's port                                      | "27017"
HISTORY_DB_REPLICA_SET      | History database's replica set address                       | None
HISTORY_DB_DATA_EXPIRATION  | Time (in seconds) that the data must be kept in the database | "604800" (7 days)
MONGO_SHARD                 |Activate the use of sharding or not                           | False

********************************************************************************

## **How to install Persister service**

### **Persister service in standalone mode**

The Persister service is installed in exactly the
[same way as the History service](#history-service-in-standalone-mode), just
note that what changes is the _virtual environment_ to be created, in this case,
the directory name of the _virtual environment_ must refer to the _Persister_
service. If you want, you can also use the same _virtual environment_ as
_History_ service, no problem, but be aware of that.


### **Persister service on Docker**

Like the _standalone mode_, the _Persister_ on Docker is identical to the
[History service's one](#history-service-on-docker),
paying attention only to the name of the docker image to be generated.
In this case, it must refer to the Persister service.

__NOTE THAT__ you can use the official images provided by dojot in its
[DockerHub page](https://hub.docker.com/r/dojot/persister).

********************************************************************************

## **Running the Persister service**

Beforehand, you need an already running dojot instance in your machine.
Check out the [dojot documentation](https://dojotdocs.readthedocs.io)
for more information on installation methods.

To run the _Persister_, after setting the environment variables, execute:

```bash
$> python -m history.subscriber.persister
```

# **Tests**

History has some automated test scripts. We use [Dredd]
(<http://dredd.org/en/latest/>) to execute them:

```bash
# you may need sudo for this:
$> npm install -g dredd@5.1.4 --no-optional
```

Also install the python test dependencies:

```bash
$> pip install -r ./tests/requirements.txt

$> pip install codecov
```

Run _Dredd_ automated test scripts:

```bash
$> ./tests/start-test.sh
```

Run the `pytest` module to run the coverage tests:

```bash
$> python -m pytest --cov-report=html --cov=history tests/
```

# **Dependencies**

The service dependencies are listed in the next topics.

- _Dojot Services_: They are dojot services;
- _Others Services_: They are external services;

## **Dojot Services**

  - [Auth](https://github.com/dojot/auth);
  - [Device Manager](https://github.com/dojot/device-manager);
  - [Data Broker](https://github.com/dojot/data-broker);

## **Others Services**

  - Kafka (tested using Kafka version 2.12);
  - MongoDB (tested using MongoDB version 3.2);


# **Documentation**

Check the documentation for more information:

- [Latest History API documentation](https://dojot.github.io/history/apiary_latest.html)
- [Development History API documentation](https://dojot.github.io/history/apiary_development.html)
- [Latest dojot platform documentation](https://dojotdocs.readthedocs.io/en/latest)

## **Generate API documentation**

The API documentation for this service is written as
[API blueprint](https://apiblueprint.org/).
To generate a simple web page from it, you must execute the commands below:

```bash
# you may need sudo for this:
$> npm install -g aglio

# static webpage
$> aglio -i ./docs/history.apib -o ./docs/history.html

# serve apis locally
$> aglio -i ./docs/history.apib -s
```

# **Issues and help**

If you found a problem or need help, leave an issue in the main
[dojot repository](https://github.com/dojot/dojot) and we will help you!