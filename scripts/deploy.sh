#!/bin/bash
echo "start deploy"

echo "stop nginx"
sudo systemctl stop nginx

echo "stop gnicorn"
pkill gunicorn

echo "start deploy"
git pull origin master

pipenv run gunicorn config.wsgi --bind 0.0.0.0:8000 -D
echo "gunicorn started"

sudo systemctl start nginx
echo "nginx started"

echo "deploy done"
