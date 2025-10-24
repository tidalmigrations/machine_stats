import pytest
from unittest.mock import patch, MagicMock
import io
import sys
from src.machine_stats import main

@patch('src.machine_stats.Application')
@patch('src.machine_stats.shutil')
@patch('src.machine_stats.os')
def test_main_cli_basic(
    mock_os,
    mock_shutil,
    mock_application
):
    mock_application_instance = mock_application.return_value
    mock_application_instance.run.return_value = None

    # Mock os.environ to control ANSIBLE_CONFIG
    mock_os.environ = {}
    mock_os.path.exists.return_value = False
    mock_os.access.return_value = False
    mock_os.getcwd.return_value = '/tmp'

    # Simulate command-line arguments
    test_hosts_path = "/Users/justin/dev/tidal/machine_stats/unix/tests/test_hosts"
    with patch('sys.argv', ['__main__.py', test_hosts_path, '--process-stats']):
        main()

    # Assertions
    mock_application_instance.run.assert_called_once()


@patch('src.machine_stats.Application')
@patch('src.machine_stats.shutil')
@patch('src.machine_stats.os')
def test_main_cli_cpu_utilization(
    mock_os,
    mock_shutil,
    mock_application
):
    mock_application_instance = mock_application.return_value
    mock_application_instance.run.return_value = None

    # Mock os.environ to control ANSIBLE_CONFIG
    mock_os.environ = {}
    mock_os.path.exists.return_value = False
    mock_os.access.return_value = False
    mock_os.getcwd.return_value = '/tmp'

    # Simulate command-line arguments
    test_hosts_path = "/Users/justin/dev/tidal/machine_stats/unix/tests/test_hosts"
    with patch('sys.argv', ['__main__.py', test_hosts_path, '--cpu-utilization-timeout', '1']):
        main()

    # Assertions
    mock_application_instance.run.assert_called_once()
