#!/bin/bash
set -x

echo ++ Install required dependencies
sudo yum install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel xz-devel

echo ++ Install Python3.8
cd /opt
sudo curl -O https://www.python.org/ftp/python/3.8.12/Python-3.8.12.tgz && sudo tar xzf Python-3.8.12.tgz

# echo ++ Updating PATH
export PATH=/usr/local/bin:$PATH

cd Python-3.8.12
sudo ./configure --enable-optimizations
sudo make altinstall

# ### Check installed python versions ##
#sudo ls /usr/local/bin/python*

echo ++ Install pipenv
pip3.8 install pipenv

echo ++ Check packaging
cd /home/ec2-user/machine_stats/unix
pipenv install --python /usr/local/bin/python3.8

echo ++ Run machine stats
pipenv run machine-stats -h

echo ++++ DONE ++++
