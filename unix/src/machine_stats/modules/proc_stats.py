import os
from time import time
from pathlib import Path


def parse_status(process_path):
    '''Takes in a string value of a process path, returns a dictionary container the
    following attributes ['path', 'name', 'total_alive_time', 'pid', 'ppid',
    'max_memory_used_mb', 'memory_used_mb']'''

    status = dict()
    rename_dict = {"vmpeak": "max_memory_used_mb", "vmsize": "memory_used_mb"}
    # Follow the symlink for the exe file to get the path and name of
    # the executable
    #
    # Note : This call requires root level access to be able to follow
    # all symlinks. Otherwise some processes will be identified as
    # /proc/2138/exe
    path, name = str(Path(process_path + "/exe").resolve()).rsplit("/", 1)
    status["path"] = path
    status["name"] = name

    # Use the folder create time for the process as an indicator for
    # the start time.
    #
    # There is a caveat that on Linux, st_ctime tracks the last time
    # the metadata for a folder changed. So we're making an assumption
    # that the folder metadata has not changed since creation
    status["total_alive_time"] =  time() - os.stat(process_path).st_ctime

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
    with open(process_path + "/status") as proc_status:
        traits = ["pid", "ppid", "user", "vmpeak", "vmsize", "name"]
        for line in proc_status:
            name, value = line.split(":")
            name = name.lower().strip()
            if name in traits:
                if name in rename_dict.keys():
                    # Virtual Memory data is usually stored in a human
                    # readable string based off of KB
                    # Ex:
                    #
                    # VmPeak: 168 kB
                    status[rename_dict[name]] = int(value.strip().split()[0])/1024
                else:
                    status[name] = value.strip()
        return status

def process_stats():
    '''Returns a list of dictionaries representing important stats for
    processes. These attributes include ['path', 'name', 'total_alive_time', 'pid',
    'ppid', 'max_memory_used_mb', 'memory_used_mb']'''

    process_paths = [folder.path for folder in os.scandir("/proc") if
     folder.is_dir() and str.isdigit(folder.name)]

    return [parse_status(process) for process in process_paths]

def main():
    process_stats()

if __name__ == "__main__":
    main()
