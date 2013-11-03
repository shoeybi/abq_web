#!/bin/bash

sudo apt-get update
sudo apt-get upgrade -y

sudo apt-get install apache2 -y
sudo apt-get install libapache2-mod-wsgi -y

sudo apt-get install gcc -y
sudo apt-get install build-essential -y
sudo apt-get install gfortran -y

#sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080

sudo curl https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py | sudo python
rm -f setuptools-*.tar.gz
sudo apt-get install python-pip -y
sudo apt-get install python-dev -y
sudo pip install --upgrade pip
sudo pip install --upgrade setuptools

sudo apt-get install emacs -y
sudo apt-get install git-core -y
git clone https://github.com/shoeybi/abq_dev.git
git clone https://github.com/shoeybi/abq_web.git

cd abq_web
sudo pip install -r requirements.pip

