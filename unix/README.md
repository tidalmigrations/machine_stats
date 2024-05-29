# Machine Stats for Unix-like systems

[![PyPI](https://img.shields.io/pypi/v/machine-stats)](https://pypi.org/project/machine-stats/)

A simple and effective way to gather machine statistics (RAM, Storage, CPU)
from a server environment as a first layer of a [Tidal discovery process](https://guides.tidal.cloud/).

Machine Stats for Linux/Unix leverages [Ansible](https://www.ansible.com/) to
gather facts in a cross-platform way.

## Interactive tutorial

Get familiar with Machine Stats, Tidal Tools and Tidal Accelerator!

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://ssh.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https%3A%2F%2Fgithub.com%2Ftidalmigrations%2Fmachine-stats-workshop&cloudshell_image=gcr.io%2Ftidal-1529434400027%2Fmachine-stats-workshop&cloudshell_tutorial=machine-stats.md&shellonly=true)

## Installation

Install locally in a Python 3 environment:

```sh
python3 -m pip install machine-stats
```

_Need to install in an environment without internet access?_ [Checkout how to do that below](#offline-installation).

<details>
    <summary>Distribution-specific installation instructions</summary>

### Ubuntu 16.04

1. Make sure `pip` is installed and is one of the latest version available:
    ```sh
    sudo apt update && \
      sudo apt install -y python3-pip && \
      python3 -m pip install --user pip==18.1 && \
      python3 -m pip install --upgrade --user pip
    ```
    **Note:** Direct upgrade to the latest available `pip` version results with an unusable `pip` installation. That's why we perform the upgrade through the intermediate version (`18.1`).
2. Install `machine-stats`:
    ```sh
    python3 -m pip install machine-stats
    ```

### Debian 9/Ubuntu 18.04

1. Make sure `pip` is installed and is one of the latest version:
    ```sh
    sudo apt update && \
      sudo apt install -y python3-pip && \
      python3 -m pip install --upgrade pip
    ```
2. Install `machine-stats`:
    ```sh
    python3 -m pip install machine-stats
    ```

### Debian 10/Debian 11/Ubuntu 20.04/Ubuntu 21.04

1. Make sure `pip` is installed:
    ```sh
    sudo apt update && \
      sudo apt install -y python3-pip
    ```
2. Install `machine-stats`:
    ```sh
    python3 -m pip install machine-stats
    ```

### CentOS 7/CentOS 8/CentOS Stream/Red Hat Enterprise Linux 7/Red Hat Enterprise Linux 8/Rocky Linux 8

1. Install Python 3:
    ```sh
    sudo yum install -y python3
    ```
2. Upgrade `pip` to the latest available version:
    ```sh
    python3 -m pip install --upgrade --user pip
    ```
3. Install `machine-stats`:
    ```sh
    python3 -m pip install machine-stats
    ```

### SUSE Linux Enterprise Server 12

1. Install Python 3.6:
    ```sh
    sudo zypper install -y python36-base
    ```
2. Install `machine-stats`:
    ```sh
    pip install machine-stats
    ```

### SUSE Linux Enterprise Server 15

1. Install `pip`:
    ```sh
    sudo zypper install -y python3-pip
    ```
2. Install `machine-stats`:
    ```sh
    pip install machine-stats
    ```  
</details>

## Data captured

For Linux/Unix based systems, by default, the following metrics are captured
from the resources and sent and stored in Tidal Accelerator:

- Host Name
- FQDN
- IP Addresses
- RAM Allocated (GB)
- RAM Used (GB)
- Storage Allocated (GB)
- Storage Used (GB)
- CPU Count
- Operating System
- Operating System Version
- CPU name

Here is an example of the output of `machine-stats`:

```
{
    "servers": [
        {
            "cpu_count": 2,
            "cpu_name": "Intel(R) Xeon(R) Platinum 8259CL CPU @ 2.50GHz",
            "custom_fields": {
                "cpu_average": 0.9314873092946548,
                "cpu_peak": 20.46949490073019,
                "cpu_sampling_timeout": 30,
                "cpu_utilization_timestamp": "2024-05-17 11:54:19"
            },
            "fqdn": "ip-172-31-9-62.ca-central-1.compute.internal",
            "host_name": "ip-172-31-9-62",
            "ip_addresses": [
                "172.31.9.62",
                "172.17.0.1",
                "fe80::4ee:9cff:fe97:418f"
            ],
            "operating_system": "Ubuntu",
            "operating_system_version": "18.04",
            "ram_allocated_gb": 0.9267578125,
            "ram_used_gb": 0.7001953125,
            "storage_allocated_gb": 7.80632209777832,
            "storage_used_gb": 2.61613130569458
        }
    ]
}
```

It's also possible to capture point-in-time CPU utilization using the flags `--cpu-utilization-only-value` and `--cpu-utilization-timeout`.

Here's an example of the output of running `machine-stats hosts --cpu-utilization-only-value --cpu-utilization-timeout 1`:

```
{
    "servers": [
        {
            "cpu_count": 2,
            "cpu_name": "Intel(R) Xeon(R) Platinum 8259CL CPU @ 2.50GHz",
            "custom_fields": {
                "cpu_sampling_timeout": 1,
                "cpu_utilization": 0.497512437810943,
                "cpu_utilization_timestamp": "2024-05-17 11:59:54"
            },
            "fqdn": "ip-172-31-9-62.ca-central-1.compute.internal",
            "host_name": "ip-172-31-9-62",
            "ip_addresses": [
                "172.31.9.62",
                "172.17.0.1",
                "fe80::4ee:9cff:fe97:418f"
            ],
            "operating_system": "Ubuntu",
            "operating_system_version": "18.04",
            "ram_allocated_gb": 0.9267578125,
            "ram_used_gb": 0.7109375,
            "storage_allocated_gb": 7.80632209777832,
            "storage_used_gb": 2.6161465644836426
        }
    ]
}
```

You also can optionally capture metrics about processes running on the server:

- User
- Process Name
- Process Path
- Memory Used (MB)
- Max Memory Used (MB)
- Total Alive Time

To enable capturing process metrics add the command-line flag `--process-stats`:
```sh
machine-stats --process-stats
```

Here is an example of the output of this command:

```
{
    "servers": [
        {
            "cpu_count": 2,
            "cpu_name": "Intel(R) Xeon(R) Platinum 8259CL CPU @ 2.50GHz",
            "custom_fields": {
                "cpu_average": 0.4973174560230535,
                "cpu_peak": 13.43191223297967,
                "cpu_sampling_timeout": 30,
                "cpu_utilization_timestamp": "2024-05-17 11:56:39"
            },
            "fqdn": "ip-172-31-9-62.ca-central-1.compute.internal",
            "host_name": "ip-172-31-9-62",
            "ip_addresses": [
                "172.31.9.62",
                "172.17.0.1",
                "fe80::4ee:9cff:fe97:418f"
            ],
            "operating_system": "Ubuntu",
            "operating_system_version": "18.04",
            "process_stats": [
                {
                    "max_memory_used_mb": 283.7890625,
                    "memory_used_mb": 220.11328125,
                    "name": "systemd",
                    "path": "/",
                    "pid": 1,
                    "ppid": 0,
                    "total_alive_time": 420,
                    "user": "root"
                }
            ]
        }
    ]
}
```

## Minimal example

1. Create a `hosts` file in the current directory. See [below](#Generating-a-hosts-file-from-Tidal-Migrations) on a couple ways
   you can easily create this.

2. Add connection strings in the form of `ssh-user@ip-address` or
   `ssh-user@domain` to the `hosts` file one per line If the `ssh-user@` part
   is omitted, then the current user name is used.
3. If you need to use a custom SSH identity file for some particular host,
   provide it as the following:

   ```sh
   my-user@example.com ansible_ssh_private_key_file=path/to/key-file.pem
   ```

4. Make sure that Python 2.6+ is installed on the machines from `hosts` file.
5. If `python` executable was installed into non-default location (**not** in
   `/usr/bin/python`), add the `ansible_python_interpreter` parameter to the
   `hosts` file after the host IP/domain, for example:

   ```text
   freebsd.example.com ansible_python_interpreter=/usr/local/bin/python
   ```

6. Execute `machine-stats` and pipe its output to Tidal Tools:

   ```sh
   machine-stats | tidal sync servers
   ```

### Additional notes

By default Machine Stats looks for the `hosts` file in current working
directory. If your inventory file has another name or is located on another
path, then you should specify it explicitly:

```sh
machine-stats /path/to/myhosts | tidal sync servers
```

You can specify multiple inventory files as the following:

```sh
machine-stats hosts myhosts /path/to/myhosts
```

### Configuration

Machine Stats uses Ansible under the hood. Most of the [Ansible configuration
options](https://docs.ansible.com/ansible/2.9/reference_appendices/config.html#common-options)
can be used with Machine Stats too. By default, Machine Stats will look for
configuration files in the following locations:

- `$PWD/machine_stats.cfg`
- `$PWD/machine-stats.cfg`
- `$PWD/machinestats.cfg`
- `$PWD/ansible.cfg`
- `$HOME/.machine_stats.cfg`
- `$HOME/.machine-stats.cfg`
- `$HOME/.machinestats.cfg`
- `$HOME/.ansible.cfg`
- `/etc/ansible/ansible.cfg`

Also, it is possible to specify the custom configuration file location by
setting the `ANSIBLE_CONFIG` environment variable, for example:

```sh
ANSIBLE_CONFIG=/path/to/my/machine_stats.cfg machine_stats /path/to/my/hosts
```

**Note:** if `ANSIBLE_CONFIG` value points to a directory, then Machine Stats
will look for `ansible.cfg` in that directory.

### Getting information about RHEL 5 hosts

Red Hat Enterprise Linux 5 is shipped with Python 2.4 but `machine_stats`
requires at least Python 2.6. To install Python 2.6 on your RHEL 5 machine
follow these steps. **NOTE:** this doesn't update the existing Python packages,
but installs Python 2.6 alongside with system Python packages.

1. Download Python 2.6 package and its dependencies from EPEL repository:

   ```console
     sudo curl -L -OOO -k \
       http://download.fedoraproject.org/pub/archive/epel/5/x86_64/{python26-libs-2.6.8-2.el5.x86_64.rpm,libffi-3.0.5-1.el5.x86_64.rpm,python26-2.6.8-2.el5.x86_64.rpm}
   ```

2. Install the packages:

   ```console
   sudo rpm -ivh python26*.rpm libffi*.rpm
   ```

3. Use non-standard Python location in your `hosts` file:

   ```text
   my-user@rhel5.example.com ansible_python_interpreter=/usr/bin/python2.6
   ```

### Offline installation

**NOTE:** Creating the packages archive for offline installation and the actual
offline installation process must be performed on machines with the same OS and
Python versions.

1. On the machine with internet connection create the packages archive using
   the following commands:

   ```sh
   python3 -m pip download -d machine-stats-offline machine-stats
   tar czf machine-stats-offline.tar.gz machine-stats-offline
   ```

2. Transfer the archive to the machine where you need to perform the offline
   installation (replace `<remote-host>` and `<remote-dir>` with the
   appropriate values):

   ```sh
   scp machine-stats-offline.tar.gz <remote-host>:/<remote-dir>/
   ```

3. On the remote host, extract the archive and switch to extracted directory:

   ```sh
   tar xf machine-stats-offline.tar.gz
   cd machine-stats-offline
   ```

4. Install Machine Stats and its dependencies:

   ```sh
   python3 -m pip install --no-index --find-links . machine_stats-*.whl
   ```

## Generating a `hosts` file from Tidal Accelerator

You can easily generate a hosts file directly from your server inventory in
Tidal Accelerator. For example you can use this command:

```sh
tidal export servers | jq '.[].host_name' > hosts
```

This will create a file (`hosts`), in your current directory, that you can
use above in Step 1.

Alternatively, if you use Tidal Accelerator [Ansible Tower integration
script](https://github.com/tidalmigrations/ansible-tower-integration) you can
use its output to generate the `hosts` file for `machine_stats`.

### Requirements

- [`jq`](https://stedolan.github.io/jq/)

### Usage

```sh
cd ansible-tower-integration
./tidal_inventory.py | jq -r '.servers.hosts[]' > path/to/hosts
```

## Troubleshooting

### machine-stats: command not found

If running Machine Stats as a CLI failed, try running it as the following:

```sh
python3 -m machine_stats
```

### How to permanently enable the Python 3.8 software collection on RHEL 7

You should always enable the Python software collection before using `pipenv`
with the following command:

```sh
scl enable rh-python38 bash
```

To permanently add Python 3 to your `$PATH`, you can add an `scl_source`
command to the “dot files” for your specific user. The benefit of this approach
is that the collection is already enabled at every login.

Using your preferred text editor, add the following line to your `~/.bashrc`:

```sh
# Add RHSCL Python 3 to my login environment
source scl_source enable rh-python38
```
