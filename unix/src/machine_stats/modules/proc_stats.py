#!/usr/bin/python

ANSIBLE_METADATA = {"metadata_version": "1.1"}

import os
from time import time
from pathlib import Path

from ansible.module_utils.basic import AnsibleModule

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(process_stats=dict(type="bool", required=False, default=True))

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(changed=False, ansible_proc_stats=None)

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    # if proc-stats isn't defined or false that means that the module
    # is disabled
    if not module.params["process_stats"]:
        module.exit_json(**result)

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # get stats from processes running on server
    try:
        stats = process_stats()
    except Exception as e:
        module.fail_json(msg=str(e), **result)

    result["ansible_proc_stats"] = stats

    module.exit_json(**result)

def parse_status(process_path):
    '''Takes in a string value of a process path, returns a dictionary container the
    following attributes ['path', 'name', 'total_alive_time', 'pid', 'ppid',
    'max_memory_used_mb', 'memory_used_mb']'''

    stats = dict()
    # Follow the symlink for the exe file to get the path and name of
    # the executable
    #
    # Note : This call requires root level access to be able to follow
    # all symlinks. Otherwise some processes will be identified as
    # /proc/2138/exe
    path, name = str(Path(process_path + "/exe").resolve()).rsplit("/", 1)
    stats["path"] = path
    stats["name"] = name

    # Use the folder create time for the process as an indicator for
    # the start time.
    #
    # There is a caveat that on Linux, st_ctime tracks the last time
    # the metadata for a folder changed. So we're making an assumption
    # that the folder metadata has not changed since creation
    stats["total_alive_time"] =  round(time() - os.stat(process_path).st_ctime)

    # This algorithm expects all status files to be formatted like:
    # ```
    # Name:	init
    # Umask:	0000
    # State:	S (sleeping)
    # Tgid:	1
    # Ngid:	0
    # Pid:	1
    # PPid:	0
    # ...
    # ```
    status = dict()
    with open(process_path + "/status") as proc_status:
        for line in proc_status:
            name, value = line.split(":")
            name = name.lower().strip()
            status[name] = value.strip()

    # Parse error will throw to parent function
    stats["pid"] = int(status["pid"])
    stats["ppid"] = int(status["ppid"])
    # Virtual Memory data is usually stored in a human
    # readable string based off of KB
    # Ex:
    #
    # VmPeak: 168 kB
    stats["memory_used_mb"] = int(status["vmsize"].split()[0])/1024
    stats["max_memory_used_mb"] = int(status["vmsize"].split()[0])/1024

    # Let's try to do some error recovery here, we
    # can't get the process name because the
    # script/runner doesn't have enough priveleges,
    # but we can still get the process name from
    # status file..
    if stats["name"] == "exe":
        stats["name"] = status["name"]
        stats["path"] = "/"

    return stats

def process_stats():
    '''Returns a list of dictionaries representing important stats for
    processes. These attributes include ['path', 'name', 'total_alive_time', 'pid',
    'ppid', 'max_memory_used_mb', 'memory_used_mb']'''

    process_paths = [folder.path for folder in os.scandir("/proc") if
                     folder.is_dir() and str.isdigit(folder.name)]

    return [parse_status(process) for process in process_paths]

def main():
    run_module()

if __name__ == "__main__":
    main()
