import pytest
from unittest.mock import patch, MagicMock, mock_open
from src.machine_stats.modules.cpu_utilization import (
    cpu_utilization,
    cpu_utilization_value,
    run_module,
    get_perf,
    get_date_time,
)


@patch("src.machine_stats.modules.cpu_utilization.get_date_time")
@patch("src.machine_stats.modules.cpu_utilization.get_perf")
def test_cpu_utilization(mock_get_perf, mock_get_date_time):
    """
    Test the cpu_utilization function with mocked data.
    """
    # Mock the return values of get_perf to simulate CPU stats
    mock_get_perf.side_effect = [
        (100, 200),  # First call: idle=100, total=200
        (150, 300),  # Second call: idle=150, total=300
    ]
    # Mock the return value of get_date_time
    mock_get_date_time.return_value = ("2025-10-23", "12:00:00")

    # Call the function with a timeout of 1 second
    average, peak, rtc_date, rtc_time = cpu_utilization(timeout=1)

    # Assert the results
    assert average == 50.0
    assert peak == 50.0
    assert rtc_date == "2025-10-23"
    assert rtc_time == "12:00:00"


@patch("src.machine_stats.modules.cpu_utilization.get_date_time")
@patch("src.machine_stats.modules.cpu_utilization.get_perf")
def test_cpu_utilization_value(mock_get_perf, mock_get_date_time):
    """
    Test the cpu_utilization_value function with mocked data.
    """
    # Mock the return values of get_perf to simulate CPU stats
    mock_get_perf.side_effect = [
        (100, 200),  # First call: idle=100, total=200
        (150, 300),  # Second call: idle=150, total=300
    ]
    # Mock the return value of get_date_time
    mock_get_date_time.return_value = ("2025-10-23", "12:00:00")

    # Call the function with a timeout of 1 second
    utilization, rtc_date, rtc_time = cpu_utilization_value(timeout=1)

    # Assert the results
    assert utilization == 50.0
    assert rtc_date == "2025-10-23"
    assert rtc_time == "12:00:00"


def test_get_perf():
    """
    Test the get_perf function with mocked /proc/stat data.
    """
    proc_stat_content = "cpu  267349 2083 451457 41680197 22538 0 11293 0 0 0\n"
    with patch("builtins.open", mock_open(read_data=proc_stat_content)):
        idle, total = get_perf()
        assert idle == 41680197.0
        assert total == sum([267349, 2083, 451457, 41680197, 22538, 0, 11293, 0, 0, 0])


def test_get_date_time():
    """
    Test the get_date_time function with mocked /proc/driver/rtc data.
    """
    proc_rtc_content = "rtc_time\t: 12:00:00\nrtc_date\t: 2025-10-23\n"
    with patch("builtins.open", mock_open(read_data=proc_rtc_content)):
        date, time = get_date_time()
        assert date == "2025-10-23"
        assert time == "12:00:00"


@patch("src.machine_stats.modules.cpu_utilization.get_date_time")
@patch("src.machine_stats.modules.cpu_utilization.get_perf")
def test_cpu_utilization_zero_delta(mock_get_perf, mock_get_date_time):
    """
    Test cpu_utilization when total_delta is zero.
    """
    mock_get_perf.side_effect = [(100, 200), (100, 200)]  # No change
    mock_get_date_time.return_value = ("2025-10-23", "12:00:00")
    average, peak, _, _ = cpu_utilization(timeout=1)
    assert average == 50.0
    assert peak == 50.0


@patch("src.machine_stats.modules.cpu_utilization.get_date_time")
@patch("src.machine_stats.modules.cpu_utilization.get_perf")
def test_cpu_utilization_value_zero_delta(mock_get_perf, mock_get_date_time):
    """
    Test cpu_utilization_value when total_delta is zero.
    """
    mock_get_perf.side_effect = [(100, 200), (100, 200)]  # No change
    mock_get_date_time.return_value = ("2025-10-23", "12:00:00")
    utilization, _, _ = cpu_utilization_value(timeout=1)
    assert utilization == 0.0


@patch("src.machine_stats.modules.cpu_utilization.AnsibleModule")
def test_run_module_disabled(mock_ansible_module):
    mock_module = MagicMock()
    mock_module.params = {"timeout": 0, "only_value": False}
    mock_ansible_module.return_value = mock_module
    run_module()
    mock_module.exit_json.assert_called_with(
        changed=False, timeout=0, ansible_cpu_utilization=None
    )


@patch("src.machine_stats.modules.cpu_utilization.AnsibleModule")
def test_run_module_check_mode(mock_ansible_module):
    mock_module = MagicMock()
    mock_module.check_mode = True
    mock_module.params = {"timeout": 5}
    mock_ansible_module.return_value = mock_module
    run_module()
    mock_module.exit_json.assert_called_with(
        changed=False, timeout=0, ansible_cpu_utilization=None
    )


@patch("src.machine_stats.modules.cpu_utilization.cpu_utilization")
@patch("src.machine_stats.modules.cpu_utilization.AnsibleModule")
def test_run_module_success_default(mock_ansible_module, mock_cpu_utilization):
    mock_module = MagicMock()
    mock_module.check_mode = False
    mock_module.params = {"timeout": 1, "only_value": False}
    mock_ansible_module.return_value = mock_module
    mock_cpu_utilization.return_value = (50.0, 75.0, "2025-10-23", "12:00:00")

    run_module()

    expected_result = {
        "average": 50.0,
        "peak": 75.0,
        "rtc_date": "2025-10-23",
        "rtc_time": "12:00:00",
    }
    mock_module.exit_json.assert_called_with(
        changed=False, timeout=1, ansible_cpu_utilization=expected_result
    )


@patch("src.machine_stats.modules.cpu_utilization.cpu_utilization_value")
@patch("src.machine_stats.modules.cpu_utilization.AnsibleModule")
def test_run_module_success_only_value(mock_ansible_module, mock_cpu_utilization_value):
    mock_module = MagicMock()
    mock_module.check_mode = False
    mock_module.params = {"timeout": 1, "only_value": True}
    mock_ansible_module.return_value = mock_module
    mock_cpu_utilization_value.return_value = (60.0, "2025-10-23", "12:00:00")

    run_module()

    expected_result = {
        "value": 60.0,
        "rtc_date": "2025-10-23",
        "rtc_time": "12:00:00",
    }
    mock_module.exit_json.assert_called_with(
        changed=False, timeout=1, ansible_cpu_utilization=expected_result
    )


@patch("src.machine_stats.modules.cpu_utilization.cpu_utilization")
@patch("src.machine_stats.modules.cpu_utilization.AnsibleModule")
def test_run_module_fail(mock_ansible_module, mock_cpu_utilization):
    mock_module = MagicMock()
    mock_module.check_mode = False
    mock_module.params = {"timeout": 1, "only_value": False}
    mock_ansible_module.return_value = mock_module
    error_message = "Test Exception"
    mock_cpu_utilization.side_effect = Exception(error_message)

    run_module()

    mock_module.fail_json.assert_called_with(
        msg=error_message, changed=False, timeout=0, ansible_cpu_utilization=None
    )
