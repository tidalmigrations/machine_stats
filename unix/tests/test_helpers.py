from machine_stats import (
    cpu_logical_processors,
    cpu_name,
    ip_addresses,
    ram_allocated_gb,
    ram_used_gb,
    storage_allocated_gb,
    storage_used_gb,
)


def test_ram_allocated_gb():
    facts = {"ansible_memtotal_mb": 2048}
    assert ram_allocated_gb(facts) == 2


def test_ram_used_gb():
    facts = {"ansible_memtotal_mb": 2048, "ansible_memfree_mb": 1024}
    assert ram_used_gb(facts) == 1


def test_storage_allocated_gb():
    facts = {
        "ansible_mounts": [
            {"size_total": 1073741824},
            {"size_total": 1073741824},
        ]
    }
    assert storage_allocated_gb(facts) == 2


def test_storage_used_gb():
    facts = {
        "ansible_mounts": [
            {"size_total": 1073741824, "size_available": 536870912},
            {"size_total": 1073741824, "size_available": 536870912},
        ]
    }
    assert storage_used_gb(facts) == 1


def test_cpu_logical_processors():
    facts = {"ansible_processor_vcpus": 4}
    assert cpu_logical_processors(facts) == 4


def test_cpu_name():
    assert cpu_name(["GenuineIntel", "Intel(R) Xeon(R) CPU E5-2686 v4 @ 2.30GHz"]) == "Unknown"
    assert cpu_name(["GenuineIntel", "Intel(R) Xeon(R) CPU E5-2686 v4 @ 2.30GHz", "Intel"]) == "Intel"


def test_ip_addresses():
    facts = {
        "ansible_all_ipv4_addresses": ["192.168.1.1"],
        "ansible_all_ipv6_addresses": ["::1"],
    }
    assert ip_addresses(facts) == [{"address": "192.168.1.1"}, {"address": "::1"}]
