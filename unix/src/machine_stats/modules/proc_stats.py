#!/usr/bin/python

ANSIBLE_METADATA = {"metadata_version": "1.1"}

import os
from time import time
from pathlib import Path
from pwd import getpwuid

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
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # if proc-stats is disabled or we are in check mode, exit early.
    if not module.params["process_stats"] or module.check_mode:
        module.exit_json(**result)
    else:
        # get stats from processes running on server
        try:
            stats = process_stats()
            result["ansible_proc_stats"] = stats
            module.exit_json(**result)
        except Exception as e:
            module.fail_json(msg=str(e), **result)


def _get_process_exe_info(process_path):
    """
    Resolves the executable path for a process to get its path and name.
    Returns a tuple of (path, name) or None on failure.
    """
    try:
        path, name = str(Path(process_path + "/exe").resolve()).rsplit("/", 1)
        return path, name
    except Exception:
        return None


def _parse_proc_status_file(process_path):
    """
    Parses the /proc/<pid>/status file and returns a dictionary of its contents.
    """
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
    status = {}
    with open(process_path + "/status") as proc_status:
        for line in proc_status:
            result = line.split(":")
            key = result[0].lower().strip()
            value = result[1].strip()
            status[key] = value
    return status


def _get_username_from_uid(uid_str):
    """
    Takes a UID string from a proc status file and returns the username.
    Falls back to the UID if the username cannot be found.
    """
    uid = int(uid_str.split()[0])
    try:
        user_entry = getpwuid(uid)
        return user_entry.pw_name
    except KeyError:
        return str(uid)  # Fallback to UID


def parse_status(process_path):
    """Takes in a string value of a process path, returns a dictionary containing the
    following attributes ['path', 'name', 'total_alive_time', 'pid', 'ppid',
    'max_memory_used_mb', 'memory_used_mb']"""

    stats = {}

    exe_info = _get_process_exe_info(process_path)
    if not exe_info:
        return stats

    stats["path"], stats["name"] = exe_info

    # Use the folder create time for the process as an indicator for
    # the start time.
    #
    # There is a caveat that on Linux, st_ctime tracks the last time
    # the metadata for a folder changed. So we're making an assumption
    # that the folder metadata has not changed since creation
    stats["total_alive_time"] = round(time() - os.stat(process_path).st_ctime)

    status = _parse_proc_status_file(process_path)

    # Parse error will throw to parent function
    if status.get("pid"):
        stats["pid"] = int(status["pid"])

    if status.get("ppid"):
        stats["ppid"] = int(status["ppid"])

    # Virtual Memory data is usually stored in a human
    # readable string based off of KB
    # Ex:
    #
    # VmPeak: 168 kB
    if status.get("vmsize"):
        stats["memory_used_mb"] = int(status["vmsize"].split()[0]) / 1024

    if status.get("vmpeak"):
        stats["max_memory_used_mb"] = int(status["vmpeak"].split()[0]) / 1024

    # Let's try to do some error recovery here, we
    # can't get the process name because the
    # script/runner doesn't have enough priveleges,
    # but we can still get the process name from
    # status file..
    if stats.get("name") == "exe":
        stats["name"] = status["name"]
        stats["path"] = "/"

    # Finally, let's see if we can read the username
    if status.get("uid"):
        stats["user"] = _get_username_from_uid(status["uid"])

    return stats


def process_stats():
    """Returns a list of dictionaries representing important stats for
    processes. These attributes include ['path', 'name', 'total_alive_time', 'pid',
    'ppid', 'max_memory_used_mb', 'memory_used_mb']"""

    process_paths = [
        folder.path
        for folder in os.scandir("/proc")
        if folder.is_dir() and str.isdigit(folder.name)
    ]

    return list(filter(None, [parse_status(process) for process in process_paths]))


def main():
    run_module()


if __name__ == "__main__":
    main()
