FROM python:3.11-slim AS builder

WORKDIR /src

# install build (for some package-dependencies) dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y libmariadb-dev-compat gcc pkg-config

# only copy the requirements files and internal wheels folder for the builder
COPY requirements.txt internal_requirements.txt ./
COPY internal ./internal

# install python requirements plus gunicorn before copying the code 
# to avoid having to create this layer per every code change
RUN pip install --no-cache-dir -r requirements.txt && \
pip install --no-cache-dir -r internal_requirements.txt && \
pip install --no-cache-dir gunicorn==21.2.0



FROM python:3.11-slim

ARG TARGET_ARCH=amd64

LABEL com.beehive.service=backend

# create non-root user for running the app & app log file
RUN addgroup --gid 10001 nonroot && \
    adduser --uid 10000 --ingroup nonroot --home /home/nonroot --disabled-password --gecos "" nonroot && \
    mkdir /var/log/beehive && \
    chown nonroot /var/log/beehive

# add tini and use it as the entrypoint
ADD https://github.com/krallin/tini/releases/download/v0.19.0/tini-$TARGET_ARCH /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

# install execution dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y libmariadb-dev-compat

WORKDIR /src

# copy all site-packages installed on the builder so we don't need
# gcc or any such heavy machinery
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/flask /usr/local/bin/gunicorn /usr/local/bin/

# copy the source and migrations directories
COPY migrations migrations/
COPY src app/

ENV FLASK_ENV=production \
    FLASK_APP=app.app:create_app \
    PYTHONPATH=/src \
    PROMETHEUS_MULTIPROC_DIR=/var/tmp

EXPOSE 8080

# use the non-root user to run the app
USER nonroot

CMD [ "gunicorn", "--bind", "0.0.0.0:8080", "--workers=3", "--timeout=120", "--log-level=info", "--access-logfile", "-", "app.app:create_app()" ]
