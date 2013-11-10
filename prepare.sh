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
cd awd
python manage.py syncdb
python manage.py shell < example.py
python manage.py collectstatic
cd ../..
sudo chown www-data -R abq_web

sudo cp ./abq_web/abq_apache_settings  /etc/apache2/sites-available/
cd  /etc/apache2/sites-enabled
sudo rm -f 000-default
sudo ln -sf ../sites-available/abq_apache_settings ./000-abaqual
sudo service apache2 restart

