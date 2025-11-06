"""
Configuration loader for machine_stats
"""

import os
import sys


def find_config_file():
    """Find configuration file"""

    potential_paths = []
    cfg_files = [
        "machine_stats.cfg",
        "machine-stats.cfg",
        "machinestats.cfg",
        "ansible.cfg",
    ]

    # Look for config file in the current working directory
    try:
        cwd = os.getcwd()
        for cfg_file in cfg_files:
            cwd_cfg = os.path.join(cwd, cfg_file)
            potential_paths.append(cwd_cfg)
    except OSError:
        # If we can't access cwd, we'll simply skip it as a possible config source
        pass

    # Per user location
    for cfg_file in cfg_files:
        potential_paths.append(os.path.expanduser("~/." + cfg_file))

    for path in potential_paths:
        if os.path.exists(path) and os.access(path, os.R_OK):
            sys.stderr.write("Using configuration file: %s\n" % path)
            break
    else:
        path = None

    return path


def load_config():
    """Load configuration from file"""
    # Do nothing if ANSIBLE_CONFIG environment variable was already set.
    if "ANSIBLE_CONFIG" in os.environ:
        pass
    else:
        cfg_file = find_config_file()
        if cfg_file is not None:
            os.environ["ANSIBLE_CONFIG"] = cfg_file
