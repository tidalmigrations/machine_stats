# machine_stats for *nix

## Requirements

1. Install `virtualenv` and [activate virtual environment](https://virtualenv.pypa.io/en/latest/userguide/)
2. `pip install -r requirements.txt`
3. [Add your SSH key to `ssh-agent`](https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/#adding-your-ssh-key-to-the-ssh-agent)

## Usage

1. Create a `hosts` file in the current directory.
2. Add IP addresses or domain names of your hosts to the `hosts` file one per line.
3. Make sure that Python is installed on the machines from `hosts` file.
4. If `python` executable was installed into non-default location (**not** in `/usr/bin/python`), add the `ansible_python_interpreter` parameter to the `hosts` file after the host IP/domain, for example:
```
freebsd.example.com ansible_python_interpreter=/usr/local/bin/python
```
5. Execute `runner` and pipe its output to Tidal Tools:
```
$ ./runner | tidal sync servers
```

## Generating `hosts` file with [Ansible Tower integration script](https://github.com/tidalmigrations/ansible-tower-integration)

If you already use Tidal Migrations Ansible Tower integration script you can use its output to generate the `hosts` file for `machine_stats`.

### Requirements

* [`jq`](https://stedolan.github.io/jq/)

### Usage

```
cd ansible-tower-integration
./tidal_inventory.py | jq -r '.servers.hosts[]' > path/to/hosts
```

## Generating `hosts` file with [Tidal Tools](https://get.tidal.sh/)

If you already use Tidal Tools you can use one of its commands — `tidal export servers` — to generate the `hosts` fiile for `machine_stats`.

### Requirements

* [Tidal Tools](https://get.tidal.sh/)
* [`jq`](https://stedolan.github.io/jq/)

### Usage

```
tidal export servers | jq -r '.[].fqdn' > path/to/hosts
```
