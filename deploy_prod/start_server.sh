#!/bin/sh

if [ "$IS_ECS" != "" ]
then
    redis-server ./deploy_prod/redis_ecs.conf &
else
    redis-server ./deploy_prod/redis_local.conf &
fi
nginx & 
pipenv run gunicorn --preload -w 4 -b unix:/tmp/gunicorn.sock "cbpc:create_app()"

