# Machine Stats
A simple and effective way to gather machine statistics (RAM, Storage, CPU)
from a server environment as a first layer of a [Tidal Migrations discovery process](https://guides.tidalmg.com).

Supports Windows, Linux and *nix platforms.

> _NB: For other platforms or custom integrations, see [the guides here](https://guides.tidalmg.com/sync-servers.html)._



## Table of Contents

- [Overview](#Overview)
- [Windows](#Windows)
- [*nix](#*NIX)
  - [Generating ansible hosts file](#Generating-a-hosts-file-from-Tidal-Migrations)



## Overview

Getting an accurate view of your infrastructure needs is useful when planning a cloud migration.  Most datacenter operations groups have a good view of their overall storage utilization from various SAN and virtualization management tools, but relying on these aggregated data points often causes teams to underestimate the storage needs of their applications in the cloud.

When taking an _application-centric_ approach to cloud migration, getting the resource utilization from each individual server gives you a more accurate view of each application's resource requirements in the cloud and ignores the trickery of thin-provisioning from SAN tools.  This allows you to confidently plan data replication time, or other migration metrics on an app-by-app basis.



```
┌ Machine Stats ─────────────┐                           ╔═ T I D A L   M I G R A T I O N S  ════╗
│                            │                           ║                                       ║
│  CPU, RAM, Storage etc.    │                           ║  - Single Source of Truth             ║
│                            │   `tidal sync servers`    ║  - Server, Database, and              ║
│                            │──────────────────────────▶║    Application Inventory              ║
│                            │                           ║                                       ║
│                            │                           ║                                       ║
└────────────────────────────┘                           ╚═══════════════════════════════════════╝
```



As your cloud migration will likely take place over many months or years, it's important to have current resource requirements throughout your journey. To accomplish this, setup `machine_stats` in a cron job or Scheduled Task and synchronize your data on a _daily_ basis to Tidal Migrations.





## Windows

Machine Stats for Windows uses WinRM to `Invoke-Command` across your servers, creating a JSON file to securely send to your [Tidal Migrations](https://tidalmigrations.com/) instance using the [tidal command](https://tidalmigrations.com/tidal-tools/).

See [windows/](windows/) for scripts:

The script `runner.ps1` should be customized for each environment.

1) Specifiy your username and a list of hostnames (either from reading a file, hard coded, or querying a directory).

2) If you plan on running this in a scheduled task, you may want to store your credential with the `PsCredential` method. See [this blog post](https://www.interworks.com/blog/trhymer/2013/07/08/powershell-how-encrypt-and-store-credentials-securely-use-automation-scripts) for an example.

> _NB: You do need WinRM enabled across your environment for this._
> _For a simple guide to do this via GPO, see [here](https://support.auvik.com/hc/en-us/articles/204424994-How-to-enable-WinRM-with-domain-controller-Group-Policy-for-WMI-monitoring)._

### Usage

1) Provide the needed Windows username to access to VMs, (line 19 in the [windows/runner.ps1.](windows/runner.ps1) file)

2) Ensure you are logged in to Tidal Migrations, via:
```
tidal login
```

3) Ensure you have a file `windows/servers.txt` that has a list of all the hostnames you want to scan. The hosts will need to be accessible via your network connection from the machine that you run this from.

You can easily export these with the 'Export' button from your Tidal Migrations account, https://your_domain.tidalmg.com/#/servers

4) Securely provide the password for the user account:
```
./windows/save_password.ps1`
```

5) Invoke the runner:
```
./windows/runner.ps1
```

You should be able to check your account and see the VMs and their corresponding attributes and metrics. You'll find that at a URL that is something like:

https://your_domain.tidalmg.com/#/servers

### Data captured

For Windows, by default, the following metrics are captured from the resources and sent and stored in Tidal Migrations:

```
Host Name
RAM Allocated (GB)
RAM Used (GB)
Storage Allocated (GB)
Storage Used (GB)
CPU Count
Operating System
Operating System Version
CPU name
```

It is also configured to capture the following values, however in order to see them in Tidal Migrations you must add the following as custom fields for servers. You can do that at a URL that looks like, https://your_domain.tidalmg.com/#/admin/servers

```
CPU_Description
CPU_Manufacturer
CPU_L2CacheSize
CPU_L3CacheSize
CPU_SocketDesignation
TotalVisible_Memory_GB
TotalVirtual_Memory_GB
```

*NB: The names must match the names above exactly. If you wish to change these or add other values you can do so at the end of the file in [windows/server_stats.ps1](windows/server_stats.ps1)*

## *NIX

Machine Stats for Linux/Unix leverages [Ansible](https://www.ansible.com/) to gather facts in a cross-platform way.

See [/unix/](unix/) for scripts:

### Data captured

For *nix based systems, by default, the following metrics are captured from the resources and sent and stored in Tidal Migrations:

```
Host Name
FQDN
IP Addresses
RAM Allocated (GB)
RAM Used (GB)
Storage Allocated (GB)
Storage Used (GB)
CPU Count
Operating System
Operating System Version
CPU name
```

### Requirements

1. Install `virtualenv` and [activate virtual environment](https://virtualenv.pypa.io/en/latest/userguide/)
2. `pip install -r requirements.txt`
3. [Add your SSH key to `ssh-agent`](https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/#adding-your-ssh-key-to-the-ssh-agent) or have your SSH identity file available.

### Usage

1. Create a `hosts` file in the current directory.
2. Add connection strings in the form of `ssh-user@ip-address` or `ssh-user@domain` to the `hosts` file one per line If the `ssh-user@` part is omitted, then the current user name is used.
3. If you need to use a custom SSH identity file for some particular host, provide it as the following:
```
my-user@example.com ansible_ssh_private_key_file=path/to/key-file.pem
```
4. Make sure that Python 2.6+ is installed on the machines from `hosts` file.
5. If `python` executable was installed into non-default location (**not** in `/usr/bin/python`), add the `ansible_python_interpreter` parameter to the `hosts` file after the host IP/domain, for example:
```
freebsd.example.com ansible_python_interpreter=/usr/local/bin/python
```
6. Execute `runner` and pipe its output to Tidal Tools:
```
$ ./runner | tidal sync servers
```

#### Getting information about RHEL 5 hosts

Red Hat Enterprise Linux 5 is shipped with Python 2.4 but `machine_stats` requires at least Python 2.6. To install Python 2.6 on your RHEL 5 machine follow these steps. **NOTE:** this doesn't update the existing Python packages, but installs Python 2.6 alongside with system Python packages.

1. Download Python 2.6 package and its dependencies from EPEL repository:
```
$ sudo curl -L -OOO -k \
    http://download.fedoraproject.org/pub/archive/epel/5/x86_64/{python26-libs-2.6.8-2.el5.x86_64.rpm,libffi-3.0.5-1.el5.x86_64.rpm,python26-2.6.8-2.el5.x86_64.rpm}
```
2. Install the packages:
```
$ sudo rpm -ivh python26*.rpm libffi*.rpm
```
3. Use non-standard Python location in your `hosts` file:
```
my-user@rhel5.example.com ansible_python_interpreter=/usr/bin/python2.6
```

### Generating a `hosts` file from Tidal Migrations

Pro-Tip: If you already use Tidal Migrations [Ansible Tower integration script](https://github.com/tidalmigrations/ansible-tower-integration) you can use its output to generate the `hosts` file for `machine_stats`.

#### Requirements

* [`jq`](https://stedolan.github.io/jq/)

#### Usage

```
cd ansible-tower-integration
./tidal_inventory.py | jq -r '.servers.hosts[]' > path/to/hosts
```
