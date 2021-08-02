# Contributing to _Virt Stats_

Welcome! Happy to see you willing to make the project better.

## We're standing on the shoulders of giants

Under the hood Virt Stats relies on awesome [libvirt](https://libvirt.org/).

## Testing environments

- To create a test environment on Google Cloud Platform use the script in `scripts/nested-virtualization/main.sh`
- Connect to the created instance and check that your user is in a `libvirt` group. Add if necessary.
- Create a new VM using the following commands:
    ```
    $ qemu-img create -f qcow2 ./debian9.qcow2 8G
    $ virt-install \
        --name debian9 \
        --ram 1024 \
        --disk path=./debian9.qcow2,size=8 \
        --vcpus 1 \
        --os-type linux \
        --os-variant generic \
        --graphics none \
        --console pty,target_type=serial \
        --location 'http://deb.debian.org/debian/dists/stretch/main/installer-amd64/' \
        --extra-args 'console=ttyS0,115200n8 serial'
    $ virsh start debian9
    ```
- It is suggested to backup the `*.qcow2` file on Google Cloud Storage, so the next time there would be no need to install the VM from scratch.

## Finally

Thanks again for your interest in improving the project! You're taking action
when most people decide to sit and watch.
