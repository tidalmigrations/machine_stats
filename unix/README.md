# machine_stats for *nix

## Requirements

1. Install `virtualenv` and [activate virtual environment](https://virtualenv.pypa.io/en/latest/userguide/)
2. `pip install -r requirements.txt`

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
