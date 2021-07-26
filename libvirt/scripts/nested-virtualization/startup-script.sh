#!/usr/bin/env bash

apt update
apt install -y \
  uml-utilities \
  qemu-kvm \
  bridge-utils \
  virtinst \
  libvirt-daemon-system \
  libvirt-clients

virsh net-start default

tunctl -t tap0
ifconfig tap0 up

brctl addif virbr0 tap0

grep libvirt /etc/default/instance_configs.cfg \
  || sed -i '/^groups =/s/$/,libvirt/' /etc/default/instance_configs.cfg

systemctl restart google-guest-agent.service
