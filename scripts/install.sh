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
sudo yum install -y yum-utils device-mapper-persistent-data lvm2 git
# Dockerリポジトリの設定
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
# 開発者向けのDocker CE Edgeのリポジトリを無効
sudo yum-config-manager --disable docker-ce-edge
# Docker CEのインストール
sudo yum makecache fast && sudo yum install -y \
docker-ce \
docker-ce-selinux

# Docker エンジンの起動
sudo systemctl daemon-reload
sudo systemctl restart docker
sudo systemctl status docker
sudo systemctl enable docker

# install docker-compose
sudo curl -L https://github.com/docker/compose/releases/download/v1.25.2/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose

# 実行権限を付与
sudo chmod +x /usr/local/bin/docker-compose

# dockerグループがなければ作る
sudo groupadd docker
# 現行ユーザをdockerグループに所属させる
sudo gpasswd -a $USER docker

# dockerデーモンを再起動する (CentOS7の場合)
sudo systemctl restart docker

# 再起動
exec $SHELL -l

# ソースコードデプロイ
git clone https://github.com/yu-sekita/Tech-Blog.git

# docker-compose 起動
cd Tech-Blog
docker-compose up --build