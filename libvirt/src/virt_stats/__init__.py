import argparse
import libvirt
import sys


def libvirt_version():
    version = libvirt.getVersion()
    major = version // 1000000
    version %= 1000000
    minor = version // 1000
    release = version % 1000
    
    return "%d.%d.%d" % (major, minor, release)

def main():
    parser = argparse.ArgumentParser(prog="virt-stats")
    parser.add_argument(
        "-c", "--connect",
        metavar="URI",
        help="hypervisor connection URI"
    )
    args = parser.parse_args()
    try:
        conn = libvirt.open(args.connect)
    except libvirt.libvirtError:
        print("Failed to open connection to the hypervisor")
        sys.exit(1)
    
    for domain in conn.listAllDomains():
        if domain.isActive():
            print("hostname", domain.hostname())

if __name__ == "__main__":
    main()
