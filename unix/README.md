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

1. **Git**

    ```
    # Debian/Ubuntu
    sudo apt-get update
    sudo apt-get install git

    # Fedora
    sudo dnf -y update
    sudo dnf -y install git

    # RHEL/CentOS
    sudo yum update
    sudo yum install git

    # macOS (Xcode)
    xcode-select --install

    # macOS (brew)
    brew install git
    ```

    Or follow the installation instructions on [Git's web
    site](https://git-scm.com/downloads)

2. **`pipenv`**

    ```
    # Debian 10+/Ubuntu 20.04+
    sudo apt-get update
    sudo apt-get install pipenv

    # Fedora 32+
    sudo dnf -y update
    sudo dnf -y install pipenv

    # RHEL 7
    sudo yum install rh-python38
    scl enable rh-python38 bash
    python3.8 -m pip install --user pipenv

    # RHEL 8
    sudo yum install python3
    python3 -m pip install --user pipenv
    ```

    Or follow the installation instructions on [`pipenv` web
    site](https://pipenv.pypa.io/en/latest/install/#installing-pipenv)

## Installation

We are going to install Machine Stats for Unix-like systems in user's `$HOME`
directory instead of system-wide, so the installation won't affect system
libraries and packages.

First of all, let's obtain the sources of Machine Stats.

Open your terminal emulator and change the current working directory to your
`$HOME` directory by running this simple command:

```
cd 
```

Let's fetch the sources from our Git repository:

```
git clone https://github.com/tidalmigrations/machine_stats.git
```

All of the code should be downloaded into a `machine_stats` directory, let's
change into that directory:

```
cd machine_stats
```

This directory contains scripts for both Window version and the version for
Unix-like systems. We need the latter, so let's switch to the appropriate
directory:

```
cd unix
```

Let's install packages which are needed for Machine Stats to run properly by
executing the following command:

```
pipenv install
```

Congratulations! You have successfully installed Machine Stats for Unix-like
systems! Let's start actually using it!

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
6. Execute `pipenv run stats` and pipe its output to Tidal Tools:
```
$ pipenv run stats | tidal sync servers
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

## Troubleshooting

## How to permanently enable the Python 3.8 software collection on RHEL 7

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
