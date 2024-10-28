# beehive-backend

## Requirements

This service requires a mysql instance with updated schemas and a redis instance.

### Install python dependencies

```bash
$ pip install -r requirements.txt
```

### Mysql setup

* Start a mysql instance using docker:

```bash
$ docker run -d --name beehive-mysql -e MYSQL_ALLOW_EMPTY_PASSWORD=1 -p 3306:3306 mysql:8
```

* Create a database and user for the service:

```bash
$ mysql -h 127.0.0.1 -u root -e "CREATE DATABASE beehive character set UTF8 collate utf8_bin; CREATE USER 'bee_backend_service' IDENTIFIED BY 'bee_backend_service'; GRANT SELECT, INSERT, UPDATE, DELETE ON beehive.* TO 'bee_backend_service';"
```

* Run all migrations (do this with the root user and no password, not with bee_backend_service we just created).

First temporarily change the SQLALCHEMY_DATABASE_URI variable in DevelopmentConfig under the config.py file to use the root user with no password:

```python
SQLALCHEMY_DATABASE_URI = 'mysql://root@127.0.0.1/beehive'
```

Then run  

```bash
$ PYTHONPATH="$(pwd)/src:$PYTHONPATH" FLASK_APP="src.app:create_app" FLASK_ENV=development flask db upgrade
```

After you run this, restore the original value of the SQLALCHEMY_DATABASE_URI variable before running the next steps.

### Redis setup

* Start a redis instance using docker:

```bash
$ docker run -d --name beehive-redis -p 6379:6379 redis:6
```

### Autobook

This step is only required for react task delegation.

* Install autobook (download the latest release from [the repo](https://github.com/beehive-software/autobook/releases)), which is a node utility. It is best to install it in the backend's directory and not globally:

```bash
$ npm install autobook-0.2.9.tgz
```

## Run Flask Dev Server

```bash
$ PYTHONPATH="$(pwd)/src:$PYTHONPATH" FLASK_APP="src.app:create_app" FLASK_ENV=development flask run
```

## Run RQ Worker

For async tasks RQ is used. To run the queued tasks the worker must be run:

```bash
$ OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES PYTHONPATH="$(pwd)/src:$PYTHONPATH" FLASK_APP="src.app:create_app" FLASK_ENV=development flask rq worker
```

Note: `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` is required for Mac users so that RQ can fork itself. It shouldn't affect anything in other systems.

## Run Tests

Before running the tests test python dependencies should be installed:

```bash
$ pip install -r test_requirements.txt
```

Note: tests should be run on an empty database, otherwise some will fail.

```bash
$ PYTHONPATH="$(pwd)/src:$PYTHONPATH" pytest --cov=src -rs tests
```

## Misc

### Create a new migration

```bash
$ PYTHONPATH="$(pwd)/src:$PYTHONPATH" FLASK_APP="src.app:create_app" FLASK_ENV=development flask db migrate --rev-id <migration-id (eg. 0001)> -m "<migration-name>"
```

### Curls

```bash
$ curl -i http://127.0.0.1:5000/api/v1/tasks
$ curl -i http://127.0.0.1:5000/delegate -H "Content-Type: application/json" -X POST -d '{"function_name": "add"}'
```

### Updating the task templates

The task templates are available in [this SQL script](migrations/scripts/task_templates.sql). You may run the script locally by running
```bash
mysql -h 127.0.0.1 -u root beehive < task_templates.sql
```

### Register a new user

For the time being the system is based on invitation only and users need to receive a registration code that we generate in one of our slack channels. To register a user locally, uncomment the line
```
    # USER_REGISTRATION_OVERRIDE_CODE = 'fake-registration-code'
```
in the file [config.py](src/config.py). Then the fake registration code for new users is the value of the parameter USER_REGISTRATION_OVERRIDE_CODE.

### Prometheus

Beehive is using [Prometheus](https://prometheus.io/) for event monitoring in production.

To connect it to a local backend service you can either use docker-compose with the [docker-compose.yml](docker-compose.yml) file to start the entire stack (backend, prometheus and others) or start prometheus and connect it to a local flask instance.

To use docker-compose you first need to set two service config values:
```python
PROMETHEUS_ENABLED = True
METRICS_AUTH_KEYS = [
    'some_key'
]
```
As well as a [prometheus config](ops/prometheus/config.yml) value under the `beehive-backend` job:
```yaml
authorization:
  credentials: 'some_key'
```

To use a local flask instance the prometheus `beehive-backend` job config should be replaced with: (replace FLASK-IP with an ip the prometheus instance can reach the flask instance at)
```yaml
- job_name: 'beehive-backend'
  static_configs:
    - targets: ['FLASK-IP:5000']
  authorization:
    credentials: 'some_key'
```

If running prometheus as a docker container, the flask service should be available to the container on the gateway ip. Otherwise, if running prometheus directly the flask service should be available to it at localhost.

When running the flask service two environment variable should be set to make sure the metrics extension is initiazlied properly:
```bash
PROMETHEUS_MULTIPROC_DIR=/tmp
DEBUG_METRICS=1
```

Finally, if running prometheus as a docker container the flask service should be available on a network interface it can communicate with prometheus on. It is easiest to make it available on all interfaces by adding the host argument to the run command:
```bash
flask run --host=0.0.0.0
```

To start a prometheus docker container use:
```bash
$ docker run \
    --rm \
    -p 9090:9090 \
    -v [your_absolute_beehive-backend_directory]/ops/prometheus/config.yml:/etc/prometheus/prometheus.yml \
    prom/prometheus:v2.26.0
```
