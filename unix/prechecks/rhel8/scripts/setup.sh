#!/bin/bash
set -x

echo ++ Update
sudo yum -y update

echo ++ Install git
sudo yum install -y git

echo ++ Clone machine stats repo
git clone https://github.com/tidalmigrations/machine_stats.git /home/ec2-user/
cd /home/ec2-user/machine_stats
git checkout $BRANCH_NAME

echo ++ Install pipenv
sudo python3 -m pip install pipenv
