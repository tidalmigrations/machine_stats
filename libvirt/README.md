# Machine Stats for Hypervisors (Virt-Stats)

A simple and effective way to gather guest VM statistics (hostname, IP addresses) from a [libvirt](https://libvirt.org/)-based environment as a first layer of a [Tidal Migrations discovery process](https://guides.tidalmg.com/). A common use case is to use this to integrate your KVM-based virtual machine inventory into the Tidal Migrations Platform.

## Prerequisutes

* [Python 3+](https://python.org/)
* [libvirt](https://libvirt.org/) >=3.0.0 installed on both operator machine (i.e where you run Virt-Stats) and on remote machine (i.e where you run your virtual environmnent and guest VMs)

## Installation

Install locally in a Python 3 environment:

```
python3 -m pip install virt-stats
```

## Data captured

As of now Virt-Stats captures the following metrics:

* Hostname
* IP Addresses
* CPU count
* RAM allocated (GB)
* RAM used (GB)

## Usage

```
virt-stats --connection URI
```

Please refer to the [Connection URIs](https://libvirt.org/uri.html) documentation for additional information.

## Output

Virt-Stats outputs a JSON document suitable to be piped to Tidal Tools:

```
virt-stats --connection qemu+ssh://me@10.0.0.1/system | tidal sync servers
```

## Troubleshooting

### virt-stats: command not found

If running Virt-Stats as a CLI failed, try running it as the following:

```
python3 -m virt-stats
```

## Contributing

If you're interested in contributing to Virt-Stats, please check our [contributing](CONTRIBUTING.md) guide.
