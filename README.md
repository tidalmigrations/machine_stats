# Machine Stats

A simple and effective way to gather machine statistics (RAM, Storage, CPU)
from a server environment as a first layer of a [Tidal Migrations discovery
process](https://guides.tidalmg.com).

Supports Windows and Unix-like platforms.

> _NB: For other platforms or custom integrations, see [the guides
> here](https://guides.tidalmg.com/sync-servers.html)._

## Overview

Getting an accurate view of your infrastructure needs is useful when planning a
cloud migration.  Most datacenter operations groups have a good view of their
overall storage utilization from various SAN and virtualization management
tools, but relying on these aggregated data points often causes teams to
underestimate the storage needs of their applications in the cloud.

When taking an _application-centric_ approach to cloud migration, getting the
resource utilization from each individual server gives you a more accurate view
of each application's resource requirements in the cloud and ignores the
trickery of thin-provisioning from SAN tools.  This allows you to confidently
plan data replication time, or other migration metrics on an app-by-app basis.

```
┌ Machine Stats ─────────────┐                           ╔═ T I D A L   M I G R A T I O N S  ════╗
│                            │                           ║                                       ║
│  CPU, RAM, Storage etc.    │                           ║  - Single Source of Truth             ║
│                            │   `tidal sync servers`    ║  - Server, Database, and              ║
│                            │──────────────────────────>║    Application Inventory              ║
│                            │                           ║                                       ║
│                            │                           ║                                       ║
└────────────────────────────┘                           ╚═══════════════════════════════════════╝
```

As your cloud migration will likely take place over many months or years, it's
important to have current resource requirements throughout your journey. To
accomplish this, setup `machine_stats` in a cron job or Scheduled Task and
synchronize your data on a _daily_ basis to Tidal Migrations.

## Table of Contents

* [Machine Stats for Windows](/windows/README.md)
* [Machine Stats for Unix-like systems](/unix/README.md)
