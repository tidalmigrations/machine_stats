# Contributing to _Virt Stats_

Welcome! Happy to see you willing to make the project better.

## We're standing on the shoulders of giants

Under the hood Virt Stats relies on awesome [libvirt](https://libvirt.org/).

## Technicalities

Development on the latest version of Python is preferred. As of this writing it's 3.9. You can use any operating system.

Install all development dependencies using:

```
pipenv install --dev
```

If you haven't used `pipenv` before but are comfortable with virtualenvs, just run `pip install pipenv` in the virtualenv you're already using and invoke the command above from the `libvirt` directory of the cloned _Machine Stats_ repo. It will do the correct thing.

Non `pipenv` install works too:

```
pip install -r requirements.txt
pip install -r dev-requirements.txt
pip install -e .
```

### Tools

We use the following tools:

* `black` for code formatting (`pipenv run black .`)
* `isort` to sort imports (`pipenv run isort .`)
* `flake8` or `pylint` for code linting (`pipenv run flake8
  src/machine_stats/*` or `pipenv run pylint src`)
* `bump2version` for version bumps (`pipenv run bump2version`)

## Testing environments

- To create a test environment on Google Cloud Platform use the script in `scripts/nested-virtualization/main.sh`
- Connect to the created instance and check that your user is in a `libvirt` group. Add if necessary:
    ```
    $ sudo usermod -a -G libvirt $USER
    ```
- Download a [Debian Cloud image](https://cloud.debian.org/images/cloud/) suitable for QEMU, for example:
    ```
    $ curl -L -O https://cloud.debian.org/images/cloud/buster/latest/debian-10-nocloud-amd64.qcow2
    ```
- Move the image file to `/var/lib/libvirt/images` to workaround permissions issue:
    ```
    $ sudo mv debian-10-nocloud-amd64.qcow2 /var/lib/libvirt/images/
    ```
- Create a new VM using the following command:
    ```
    $ virt-install \
      --connect qemu:///system \
      --name debian10 \
      --memory 1024 \
      --vcpus 1 \
      --disk path=/var/lib/libvirt/images/debian-10-nocloud-amd64.qcow2,size=8,bus=virtio,format=qcow2 \
      --import \
      --graphics none \
      --os-variant debian10 \
      --network network=default,model=virtio
    ```
  * It will boot Debian 10
  * To login, use `root` without a password
  * Install and enable QEMU Guest Agent:
      ```
      # apt-get update && apt-get install -y qemu-guest-agent
      # systemctl enable qemu-quest-agent
      # systemctl start qemu-guest-agent
      # logout
      ```
  * Press `^[` (<kbd>Ctrl+[</kbd>) on your keyboard
  * `Domain creation completed` message should appear.
  * Verify, that the VM is up and running:
      ```
      virsh -c qemu:///system list
       Id   Name       State
      --------------------------
       1    debian10   running
      ```

### How to release a new virt-stats version

To deploy a new version of Virt Stats, you will need to create a release. The steps are pretty simple, You can find Github's instruction [here](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository#creating-a-release).

* On the main repo page, click on [Releases](https://github.com/tidalmigrations/machine_stats/releases) (right side bar)
* Create a new release on the `master` branch.
* Choose a tag. The Tag that you create will be used as the new Tidal Tools version. Please follow this convention
  * Minor/Patch release: `v2.5.6` → `v2.5.7`
  * Major release: `v2.5.10` → `v2.6.0`
  * Version release: `v2.6.7` → `v3.0.0`
* **Note:** [machine stats](https://pypi.org/project/machine-stats/) also have the same version number as Virt Stats.

## Finally

Thanks again for your interest in improving the project! You're taking action
when most people decide to sit and watch.
