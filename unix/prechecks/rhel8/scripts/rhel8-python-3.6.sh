#!/bin/bash
set -x

ls /usr/bin/python*
echo ++ Install Python36
sudo yum install -y python36
sudo pip3 install --upgrade pip

echo ++ Updating PATH
export PATH=/usr/local/bin:$PATH

python --version
python3 --version
python3.6 --version
ls /usr/bin/python*

echo ++ Install pipenv
sudo python3 -m pip install pipenv

echo ++ Check packaging
cd /home/ec2-user/machine_stats/unix
pipenv install

echo ++ Run machine stats
pipenv run machine-stats -h

echo ++++ DONE ++++
