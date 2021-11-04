# Machine Stats for Virtual environments (Virt-Stats)

A simple and effective way to gather guest VM statistics (hostname, IP addresses) from a [libvirt](https://libvirt.org/)-based environment as a first layer of a [Tidal Migrations discovery process](https://guides.tidalmg.com/).

## Prerequisutes

* [Python 3+](https://python.org/)
* [libvirt](https://libvirt.org/) >=3.0.0 installed on both operator machine (i.e where you run Virt-Stats) and on remote machine (i.e where you run your virtual environmnent and guest VMs)
* [QEMU guest agent](https://wiki.qemu.org/Features/GuestAgent) installed and running on guest VMs _(optional)_.

## Installation

Install locally in a Python 3 environment:

```
python3 -m pip install virt-stats
```

## Data captured

As of now Virt-Stats captures the following metrics:

* Hostname
* IP Addresses

## Usage

```
virt-stats --connection URI
```

Please refer to the [Connection URIs](https://libvirt.org/uri.html) documentation for additional information.

## Output

Virt-Stats outputs a JSON document suitable to be piped to Tidal Tools:

```
virt-stats --connection qemu:///system | tidal sync servers
```

## Troubleshooting

### virt-stats: command not found

If running Virt-Stats as a CLI failed, try running it as the following:

```
python3 -m virt-stats
```
