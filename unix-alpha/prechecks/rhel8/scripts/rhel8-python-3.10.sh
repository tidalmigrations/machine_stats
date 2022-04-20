#!/bin/bash
set -x

echo ++ Install required dependencies
sudo yum install -y openssl-devel libffi-devel bzip2-devel
gcc --version

echo ++ Install Python3.10
cd /opt
sudo curl -O https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz  && sudo tar xvf Python-3.10.0.tgz

# echo ++ Updating PATH
export PATH=/usr/local/bin:$PATH

cd Python-3.10.0
sudo ./configure --enable-optimizations
sudo make altinstall

# ### Check installed python versions ##
#sudo ls /usr/local/bin/python*

echo ++ Install pipenv
pip3.10 install pipenv

echo ++ Check packaging
cd /home/ec2-user/machine_stats/unix
pipenv install --python /usr/local/bin/python3.10

echo ++ Run machine stats
pipenv run machine-stats -h

echo ++++ DONE ++++
