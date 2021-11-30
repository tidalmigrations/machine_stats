import argparse
import json
import os
import sys
import io

import libvirt

from contextlib import contextmanager


def libvirt_version():
    version = libvirt.getVersion()
    major = version // 1000000
    version %= 1000000
    minor = version // 1000
    release = version % 1000

    return "%d.%d.%d" % (major, minor, release)


@contextmanager
def suppress_stderr():
    try:
        stderr = os.dup(sys.stderr.fileno())
        devnull = open(os.devnull, "w")
        os.dup2(devnull.fileno(), sys.stderr.fileno())
        yield
    finally:
        os.dup2(stderr, sys.stderr.fileno())
        devnull.close()


def hostname(domain: libvirt.virDomain):
    try:
        with suppress_stderr():
            hostname = domain.hostname()
        return hostname
    except libvirt.libvirtError:
        macs = []
        ifaces = domain.interfaceAddresses(
            libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE
        )
        for (_, val) in ifaces.items():
            if val["hwaddr"]:
                macs.append(val["hwaddr"])
        conn = domain.connect()
        for network in conn.listAllNetworks(libvirt.VIR_CONNECT_LIST_NETWORKS_ACTIVE):
            for lease in network.DHCPLeases():
                for mac in macs:
                    if lease["mac"] == mac:
                        return lease["hostname"]


def ip_addresses(domain: libvirt.virDomain):
    ips = []
    ifaces = domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)
    for (_, val) in ifaces.items():
        if val["addrs"]:
            for ipaddr in val["addrs"]:
                if (
                    ipaddr["type"] == libvirt.VIR_IP_ADDR_TYPE_IPV4
                    or ipaddr["type"] == libvirt.VIR_IP_ADDR_TYPE_IPV6
                ):
                    ips.append(ipaddr["addr"])
    return ips


def ram_allocated_gb(memory_stats: dict):
    v = memory_stats.get("available")
    if not v:
        return None
    return round(
        v / 1024 ** 2, 2
    )  # convert kb to gb and round to 2 digits precision after the decimal point.


def ram_used_gb(memory_stats: dict):
    mem_total = memory_stats.get("available")
    mem_free = memory_stats.get("unused")
    if not mem_total or not mem_free:
        return None
    mem_used = mem_total - mem_free
    return round(
        mem_used / 1024 ** 2, 2
    )  # convert kb to gb and round to 2 digits precision after the decimal point.


def storage_devices(domain: libvirt.virDomain) -> set:
    storage_devices = set()
    list_of_lists = [item[-1] for item in domain.fsInfo()]
    for sublist in list_of_lists:
        storage_devices.update(sublist)
    return storage_devices


def storage_allocated_gb(domain: libvirt.virDomain):
    capacity = 0
    for device in storage_devices(domain):
        capacity += domain.blockInfo(device)[0]
    return round(
        capacity / 1024 ** 3, 2
    )  # convert bytes to gb and round to 2 digits precision after the decimal point.


def storage_used_gb(domain: libvirt.virDomain):
    allocation = 0
    for device in storage_devices(domain):
        allocation += domain.blockInfo(device)[1]
    return round(
        allocation / 1024 ** 3, 2
    )  # convert bytes to gb and round to 2 digits precision after the decimal point.


def main():
    parser = argparse.ArgumentParser(prog="virt-stats")
    parser.add_argument(
        "-c",
        "--connect",
        metavar="URI",
        help="hypervisor connection URI (check https://libvirt.org/uri.html for details)",
    )
    args = parser.parse_args()
    try:
        conn = libvirt.open(args.connect)
    except libvirt.libvirtError:
        print("Failed to open connection to the hypervisor")
        sys.exit(1)

    results = []
    for domain in conn.listAllDomains(libvirt.VIR_CONNECT_LIST_DOMAINS_ACTIVE):
        memory_stats = domain.memoryStats()
        results.append(
            {
                "cpu_count": domain.vcpusFlags(),
                "host_name": hostname(domain),
                "ip_addresses": ip_addresses(domain),
                "ram_allocated_gb": ram_allocated_gb(memory_stats),
                "ram_used_gb": ram_used_gb(memory_stats),
                "storage_allocated_gb": storage_allocated_gb(domain),
                "storage_used_gb": storage_used_gb(domain),
            }
        )

    print(json.dumps(results, sort_keys=True, indent=4))


if __name__ == "__main__":
    main()
