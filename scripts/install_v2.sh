#!/bin/bash

# スワップ領域を開ける
sudo dd if=/dev/zero of=/var/swapfile bs=1M count=1200
sudo chmod 600 /var/swapfile
sudo mkswap -L swap /var/swapfile
sudo swapon /var/swapfile
# 確認
# cat /proc/swaps
# 再起動時にスワップ領域が自動的にmountするようにする
echo '/var/swapfile swap swap defaults 0 0' | sudo tee -a /etc/fstab/var/swapfile swap swap defaults 0 0


# install package
sudo yum -y update
sudo yum install -y yum-utils device-mapper-persistent-data lvm2 git gcc openssl-devel bzip2-devel libffi-devel mariadb-devel nginx certbot

# install pyenv
git clone https://github.com/pyenv/pyenv.git ~/.pyenv

# set environment variable
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
source ~/.bash_profile

# install python3.8
pyenv install 3.8.0
pyenv global 3.8.0

sudo yum install python3-pip
pip install pipenv

# deploy
git clone https://github.com/yu-sekita/Tech-Blog.git
cd Tech-Blog
pipenv install
pipenv install gunicorn

sudo cp nginx/nginx.conf /etc/nginx/nginx.conf
setsebool -P httpd_can_network_connect 1

# update cerbot
# sudo crontab -e
# 00 0 * * 0 certbot renew --pre-hook "systemctl stop nginx" --post-hook "systemctl start nginx"

# start nginx
# sudo systemctl start nginx

# start gunicorn
# pipenv run gunicorn config.wsgi --bind 0.0.0.0:8000 -D

# stop gunicorn
# pkill gunicorn