#!/bin/bash

sleep 10
export C_FORCE_ROOT='true'
cd /app && python manage.py celeryd --concurrency=1 --loglevel=INFO --settings=salarium.settings

