FROM python:3.5

RUN mkdir /app

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    npm \
    nodejs-legacy

ADD . /app

RUN pip install -r /app/requirments.txt && npm install -g bower && npm install -g grunt-cli && npm install grunt -g && cd /app && npm install && bower install --allow-root

VOLUME ["/app"]
WORKDIR /app
ENV PYTHONUNBUFFERED 1
