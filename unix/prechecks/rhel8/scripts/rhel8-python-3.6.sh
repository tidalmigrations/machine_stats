#!/bin/bash
set -x

echo ++ Install Python3.6 and pip
sudo yum install -y python36
sudo pip3 install --upgrade pip

echo ++ Updating PATH
export PATH=/usr/local/bin:$PATH

### Check installed python versions ##
# ls /usr/bin/python*

echo ++ Install pipenv
sudo python3 -m pip install pipenv

echo ++ Check packaging
cd /home/ec2-user/machine_stats/unix
pipenv install

echo ++ Run machine stats
pipenv run machine-stats -h

echo ++++ DONE ++++
