sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install emacs -y
sudo apt-get install gcc -y
sudo apt-get install build-essential -y
sudo apt-get install gfortran -y
sudo apt-get install git-core -y
sudo curl https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py | sudo python
rm -f setuptools-*.tar.gz
sudo apt-get install python-pip -y
sudo apt-get install python-dev -y
sudo pip install --upgrade pip
sudo pip install --upgrade setuptools
git clone https://github.com/shoeybi/abq_web.git
cd abq_web
sudo pip install -r requirements.pip
