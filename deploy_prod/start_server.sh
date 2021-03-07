#!/bin/sh

nginx & 
redis-server ./deploy_prod/redis.conf & 
pipenv run gunicorn -w 4 -b unix:/tmp/gunicorn.sock "cbpc:create_app()"

