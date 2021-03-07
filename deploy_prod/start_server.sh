#!/bin/sh

nginx & pipenv run gunicorn -w 4 -b unix:/tmp/gunicorn.sock "cbpc:create_app()"

