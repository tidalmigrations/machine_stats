import argparse
from unittest.mock import MagicMock, patch

import pytest
from src.machine_stats import (
    ram_allocated_gb,
    ram_used_gb,
    storage_allocated_gb,
    storage_used_gb,
    cpu_logical_processors,
    cpu_name,
    ip_addresses,
    main,
)


def test_ram_allocated_gb():
    facts = {"ansible_memtotal_mb": 2048}
    assert ram_allocated_gb(facts) == 2.0


def test_ram_used_gb():
    facts = {"ansible_memtotal_mb": 2048, "ansible_memfree_mb": 1024}
    assert ram_used_gb(facts) == 1.0


def test_storage_allocated_gb():
    facts = {
        "ansible_mounts": [
            {"size_total": 1073741824, "size_available": 536870912},
            {"size_total": 1073741824, "size_available": 536870912},
        ]
    }
    assert storage_allocated_gb(facts) == 2.0


def test_storage_used_gb():
    facts = {
        "ansible_mounts": [
            {"size_total": 1073741824, "size_available": 536870912},
            {"size_total": 1073741824, "size_available": 268435456},
        ]
    }
    assert storage_used_gb(facts) == 1.25


def test_cpu_logical_processors():
    facts = {"ansible_processor_vcpus": 4}
    assert cpu_logical_processors(facts) == 4


def test_cpu_name():
    assert cpu_name(["Intel(R) Xeon(R) CPU E5-2676 v3 @ 2.40GHz"]) == "Intel(R) Xeon(R) CPU E5-2676 v3 @ 2.40GHz"
    assert cpu_name(["model name", ":", "Intel(R) Xeon(R) CPU E5-2676 v3 @ 2.40GHz"]) == "Intel(R) Xeon(R) CPU E5-2676 v3 @ 2.40GHz"


def test_ip_addresses():
    facts = {
        "ansible_all_ipv4_addresses": ["192.168.1.1"],
        "ansible_all_ipv6_addresses": ["2001:db8::1"],
    }
    expected_ips = [{"address": "192.168.1.1"}, {"address": "2001:db8::1"}]
    # The original function returns a list of dicts, but the callback flattens it.
    # For now, we test the direct output of the function.
    assert ip_addresses(facts) == expected_ips


@patch('src.machine_stats.argparse.ArgumentParser')
@patch('src.machine_stats.PluginManager')
@patch('src.machine_stats.Application')
def test_main(mock_app_cls, mock_pm_cls, mock_parser_cls):
    mock_parser = mock_parser_cls.return_value
    mock_args = argparse.Namespace(hosts=[], measurement=False, version=False)
    mock_parser.parse_args.return_value = mock_args

    # Mock the 'hosts' file
    with patch('builtins.open') as mock_open:
        mock_file = MagicMock()
        mock_file.name = "hosts"
        # Configure the mock for the 'with open(...) as f:' context manager.
        # open() returns a context manager object. The result of that
        # object's __enter__() method is what's assigned to 'f'.
        mock_open.return_value.__enter__.return_value = mock_file

        main()

    # Check that the fallback to open 'hosts' was triggered
    mock_open.assert_called_once_with('hosts', 'r')

    # Verify Application was called correctly
    mock_app_cls.assert_called_once_with(
        sources=['hosts'], plugins=mock_pm_cls.return_value, args=mock_args
    )
    mock_app_cls.return_value.run.assert_called_once()
