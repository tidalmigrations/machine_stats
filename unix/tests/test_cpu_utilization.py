import pytest
from unittest.mock import patch
from src.machine_stats.modules.cpu_utilization import cpu_utilization, cpu_utilization_value

@patch('src.machine_stats.modules.cpu_utilization.get_date_time')
@patch('src.machine_stats.modules.cpu_utilization.get_perf')
def test_cpu_utilization(mock_get_perf, mock_get_date_time):
    """
    Test the cpu_utilization function with mocked data.
    """
    # Mock the return values of get_perf to simulate CPU stats
    mock_get_perf.side_effect = [
        (100, 200),  # First call: idle=100, total=200
        (150, 300)   # Second call: idle=150, total=300
    ]
    # Mock the return value of get_date_time
    mock_get_date_time.return_value = ('2025-10-23', '12:00:00')

    # Call the function with a timeout of 1 second
    average, peak, rtc_date, rtc_time = cpu_utilization(timeout=1)

    # Assert the results
    assert average == 50.0
    assert peak == 50.0
    assert rtc_date == '2025-10-23'
    assert rtc_time == '12:00:00'

@patch('src.machine_stats.modules.cpu_utilization.get_date_time')
@patch('src.machine_stats.modules.cpu_utilization.get_perf')
def test_cpu_utilization_value(mock_get_perf, mock_get_date_time):
    """
    Test the cpu_utilization_value function with mocked data.
    """
    # Mock the return values of get_perf to simulate CPU stats
    mock_get_perf.side_effect = [
        (100, 200),  # First call: idle=100, total=200
        (150, 300)   # Second call: idle=150, total=300
    ]
    # Mock the return value of get_date_time
    mock_get_date_time.return_value = ('2025-10-23', '12:00:00')

    # Call the function with a timeout of 1 second
    utilization, rtc_date, rtc_time = cpu_utilization_value(timeout=1)

    # Assert the results
    assert utilization == 50.0
    assert rtc_date == '2025-10-23'
    assert rtc_time == '12:00:00'