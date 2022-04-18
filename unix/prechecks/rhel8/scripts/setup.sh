#!/bin/bash
set -x

echo ++ Update
sudo yum -y update

echo ++ Install git
sudo yum install -y git

echo ++ Install required dependencies
sudo yum groupinstall -y 'Development Tools'

echo ++ Clone machine stats repo
git clone https://github.com/tidalmigrations/machine_stats.git /home/ec2-user/machine_stats
cd /home/ec2-user/machine_stats
git pull && git checkout $BRANCH_NAME
