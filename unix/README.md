# Machine Stats for Unix-like systems

[![PyPI](https://img.shields.io/pypi/v/machine-stats)](https://pypi.org/project/machine-stats/)

A simple and effective way to gather machine statistics (RAM, Storage, CPU)
from a server environment as a first layer of a [Tidal Migrations discovery
process](https://guides.tidalmg.com).

Machine Stats for Linux/Unix leverages [Ansible](https://www.ansible.com/) to
gather facts in a cross-platform way.

## Installation

Install locally in a Python 3 environment:

```
python3 -m pip install machine-stats
```

### Offline installation

**NOTE:** Creating the packages archive for offline installation and the actual
offline installation process must be performed on machines with the same OS and
Python versions.

1. On the machine with internet connection create the packages archive using
   the following commands:

   ```console
   $ python3 -m pip download -d machine-stats-offline machine-stats
   $ tar czf machine-stats-offline.tar.gz machine-stats-offline
   ```

2. Transfer the archive to the machine where you need to perform the offline
   installation (replace `<remote-host>` and `<remote-dir>` with the
   appropriate values):

   ```console
   $ scp machine-stats-offline.tar.gz <remote-host>:/<remote-dir>/
   ```

3. On the remote host, extract the archive and switch to extracted directory:

   ```
   $ tar xf machine-stats-offline.tar.gz
   $ cd machine-stats-offline
   ```

4. Install Machine Stats and its dependencies:

   ```
   $ python3 -m pip install --no-index --find-links . machine_stats-*.whl
   ```

## Data captured

For Linux/Unix based systems, by default, the following metrics are captured
from the resources and sent and stored in Tidal Migrations:

* Host Name
* FQDN
* IP Addresses
* RAM Allocated (GB)
* RAM Used (GB)
* Storage Allocated (GB)
* Storage Used (GB)
* CPU Count
* Operating System
* Operating System Version
* CPU name

## Minimal example

1. Create a `hosts` file in the current directory.
2. Add connection strings in the form of `ssh-user@ip-address` or
   `ssh-user@domain` to the `hosts` file one per line If the `ssh-user@` part
   is omitted, then the current user name is used.
3. If you need to use a custom SSH identity file for some particular host,
   provide it as the following:

   ```
   my-user@example.com ansible_ssh_private_key_file=path/to/key-file.pem
   ```
4. Make sure that Python 2.6+ is installed on the machines from `hosts` file.
5. If `python` executable was installed into non-default location (**not** in
   `/usr/bin/python`), add the `ansible_python_interpreter` parameter to the
   `hosts` file after the host IP/domain, for example:

   ```
   freebsd.example.com ansible_python_interpreter=/usr/local/bin/python
   ```
6. Execute `machine-stats` and pipe its output to Tidal Tools:

   ```
   $ machine-stats | tidal sync servers
   ```

### Additional notes

By default Machine Stats looks for the `hosts` file in current working
directory. If your inventory file has another name or is located on another
path, then you should specify it explicitly:

```
$ machine-stats /path/to/myhosts | tidal sync servers
```

You can specify multiple inventory files as the following:

```
$ machine-stats hosts myhosts /path/to/myhosts
```

### Getting information about RHEL 5 hosts

Red Hat Enterprise Linux 5 is shipped with Python 2.4 but `machine_stats`
requires at least Python 2.6. To install Python 2.6 on your RHEL 5 machine
follow these steps. **NOTE:** this doesn't update the existing Python packages,
but installs Python 2.6 alongside with system Python packages.

1. Download Python 2.6 package and its dependencies from EPEL repository:

   ```console
   $ sudo curl -L -OOO -k \
       http://download.fedoraproject.org/pub/archive/epel/5/x86_64/{python26-libs-2.6.8-2.el5.x86_64.rpm,libffi-3.0.5-1.el5.x86_64.rpm,python26-2.6.8-2.el5.x86_64.rpm}
   ```
2. Install the packages:

   ```console
   $ sudo rpm -ivh python26*.rpm libffi*.rpm
   ```
3. Use non-standard Python location in your `hosts` file:

   ```
   my-user@rhel5.example.com ansible_python_interpreter=/usr/bin/python2.6
   ```

## Generating a `hosts` file from Tidal Migrations

Pro-Tip: If you already use Tidal Migrations [Ansible Tower integration
script](https://github.com/tidalmigrations/ansible-tower-integration) you can
use its output to generate the `hosts` file for `machine_stats`.

### Requirements

* [`jq`](https://stedolan.github.io/jq/)

### Usage

```
cd ansible-tower-integration
./tidal_inventory.py | jq -r '.servers.hosts[]' > path/to/hosts
```

## Troubleshooting

### machine-stats: command not found

If running Machine Stats as a CLI failed, try running it as the following:

```console
$ python3 -m machine_stats
```

### How to permanently enable the Python 3.8 software collection on RHEL 7

You should always enable the Python software collection before using `pipenv`
with the following command:

```
scl enable rh-python38 bash
```

To permanently add Python 3 to your `$PATH`, you can add an `scl_source`
command to the “dot files” for your specific user. The benefit of this approach
is that the collection is already enabled at every login.

Using your preferred text editor, add the following line to your `~/.bashrc`:

```
# Add RHSCL Python 3 to my login environment
source scl_source enable rh-python38
```
