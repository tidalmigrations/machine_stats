# Machine Stats for Unix-like systems

Machine Stats for Linux/Unix leverages [Ansible](https://www.ansible.com/) to gather facts in a cross-platform way.

## Data captured

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

## Requirements

1. Install `virtualenv` and [activate virtual environment](https://virtualenv.pypa.io/en/latest/user_guide.html)
2. `pip install -r requirements.txt`
3. [Add your SSH key to `ssh-agent`](https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/#adding-your-ssh-key-to-the-ssh-agent) or have your SSH identity file available.

## Usage

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

### Getting information about RHEL 5 hosts

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

## Generating a `hosts` file from Tidal Migrations

Pro-Tip: If you already use Tidal Migrations [Ansible Tower integration script](https://github.com/tidalmigrations/ansible-tower-integration) you can use its output to generate the `hosts` file for `machine_stats`.

### Requirements

* [`jq`](https://stedolan.github.io/jq/)

### Usage

```
cd ansible-tower-integration
./tidal_inventory.py | jq -r '.servers.hosts[]' > path/to/hosts
```
