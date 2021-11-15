# Nested Virtualization

This script crates a new VM on Google Cloud Platform having nested
virtualization enabled.

## Prerequisites

- Google Cloud Platform [SDK](https://cloud.google.com/sdk/docs/install)

## Configuration

Copy `.env.example` to `.env` and edit the variables. Please check the [Restrictions](https://cloud.google.com/compute/docs/instances/nested-virtualization/overview#restrictions) before making any VM configuration changes.

## Usage

```
./main.sh
```
