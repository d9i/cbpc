FROM python:3.9-alpine

# set work directory
WORKDIR /usr/src/app

# install nginx
RUN apk update
RUN apk add --no-cache openrc
RUN apk add --no-cache nginx
RUN apk add --no-cache redis

# install update pip if needed
RUN pip install --upgrade pip

# install required packages
RUN pip install pipenv
COPY ./Pipfile ./Pipfile
COPY ./Pipfile.lock ./Pipfile.lock
RUN pipenv install

# copy project
COPY ./cbpc ./cbpc

# copy instance folder with config
COPY ./deploy_prod ./deploy_prod

# add custom nginx config
RUN mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.old
RUN mv ./deploy_prod/nginx.conf /etc/nginx/nginx.conf

# set environmental variables
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV FLASK_APP cbpc
ENV FLASK_ENV production
ENV FLASK_INSTANCE_FOLDER deploy_prod
ENV FLASK_CFG app_cfg.py

# Start up gunicorn + nginx (serving the Flask API)
EXPOSE 80
ENTRYPOINT ["./deploy_prod/start_server.sh"]