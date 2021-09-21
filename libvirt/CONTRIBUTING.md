# Contributing to _Virt Stats_

Welcome! Happy to see you willing to make the project better.

## We're standing on the shoulders of giants

Under the hood Virt Stats relies on awesome [libvirt](https://libvirt.org/).

## Testing environments

- To create a test environment on Google Cloud Platform use the script in `scripts/nested-virtualization/main.sh`
- Connect to the created instance and check that your user is in a `libvirt` group. Add if necessary:
    ```
    $ sudo usermod -a -G libvirt $USER
    ```
- Download a [Debian Cloud image](https://cloud.debian.org/images/cloud/) suitable for QEMU, for example:
    ```
    $ curl -L -O https://cloud.debian.org/images/cloud/bullseye/latest/debian-11-nocloud-amd64.qcow2
    ```
- Move the image file to `/var/lib/libvirt/images` to workaround permissions issue:
    ```
    $ sudo mv debian-11-nocloud-amd64.qcow2 /var/lib/libvirt/images/
    ```
- Create a new VM using the following command:
    ```
    $ virt-install \
      --connect qemu:///system \
      --name debian11 \
      --memory 1024 \
      --vcpus 1 \
      --disk path=/var/lib/libvirt/images/debian-11-nocloud-amd64.qcow2,size=8,bus=virtio,format=qcow2 \
      --import \
      --graphics none \
      --os-variant debian11 \
      --network network=default,model=virtio
    ```
  * It will boot Debian 11
  * To login, use `root` without a password
  * Press `^[` (<kbd>Ctrl+[</kbd>) on your keyboard
  * `Domain creation completed` message should appear.
  * Verify, that the VM is up and running:
      ```
      virsh -c qemu:///system list
       Id   Name       State
      --------------------------
       1    debian11   running
      ```

## Finally

Thanks again for your interest in improving the project! You're taking action
when most people decide to sit and watch.
