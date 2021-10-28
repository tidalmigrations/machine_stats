#!/usr/bin/env bash

# shellcheck source=/dev/null
source "/etc/os-release"

if [[ "$ID" == "rhel" || "$ID" == "centos" ]]
then
  # Use yum
  yum install -y \
    qemu-kvm \
    libvirt \
    libvirt-python \
    libguestfs-tools \
    virt-install
fi

if [[ "$ID" == "debian" || "$ID" == "ubuntu" ]]
then
  # Use apt
  apt update
  apt install -y \
    uml-utilities \
    qemu-kvm \
    bridge-utils \
    virtinst \
    libvirt-daemon-system \
    libvirt-clients
fi

# Needs to explicitly start on RHEL 7
systemctl start libvirtd 
# Start the default network if not already started
virsh net-list --name | grep --fixed-strings --line-regexp --quiet default || virsh net-start default

# There is no tunctl on RHEL 7
if type -P tunctl &>/dev/null
then
  tunctl -t tap0
else
  ip tuntap add tap0 mode tap
fi
ifconfig tap0 up

brctl addif virbr0 tap0

grep libvirt /etc/default/instance_configs.cfg \
  || sed -i '/^groups =/s/$/,libvirt/' /etc/default/instance_configs.cfg

systemctl restart google-guest-agent.service
