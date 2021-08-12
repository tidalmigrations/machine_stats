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
    print("Hello world!")
    print("libvirt version: " + libvirt_version())

if __name__ == "__main__":
    main()
