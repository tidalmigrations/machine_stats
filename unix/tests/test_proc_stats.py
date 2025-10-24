import pytest
from unittest.mock import patch, mock_open
from src.machine_stats.modules.proc_stats import parse_status, process_stats

def test_parse_status():
    """
    Test the parse_status function with mocked data.
    """
    status_file_content = 'Name:\tnginx\nUmask:\t0000\nState:\tS (sleeping)\nTgid:\t1\nNgid:\t0\nPid:\t1\nPPid:\t0\nUid:\t0\t0\t0\t0\nVmPeak:\t168 kB\nVmSize:\t168 kB\n'
    with patch('src.machine_stats.modules.proc_stats.os.path.exists', return_value=True), \
         patch('src.machine_stats.modules.proc_stats.os.stat') as mock_stat, \
         patch('src.machine_stats.modules.proc_stats.Path.resolve') as mock_resolve, \
         patch('builtins.open', mock_open(read_data=status_file_content)), \
         patch('src.machine_stats.modules.proc_stats.time') as mock_time:

        # Mock the return value of os.stat
        mock_stat.return_value.st_ctime = 1672531200  # 2023-01-01 00:00:00 UTC

        # Mock the return value of time.time
        mock_time.return_value = 1672531260 # 60 seconds later

        # Mock the return value of Path.resolve
        mock_resolve.return_value = '/usr/sbin/nginx'

        stats = parse_status('/proc/1')

    # Assert the results
    assert stats['name'] == 'nginx'
    assert stats['path'] == '/usr/sbin'
    assert stats['pid'] == 1
    assert stats['ppid'] == 0
    assert stats['total_alive_time'] == 60
    assert stats['memory_used_mb'] == 168 / 1024
    assert stats['max_memory_used_mb'] == 168 / 1024
    assert stats['user'] == 'root'

@patch('src.machine_stats.modules.proc_stats.parse_status')
@patch('src.machine_stats.modules.proc_stats.os.scandir')
def test_process_stats(mock_scandir, mock_parse_status):
    """
    Test the process_stats function with mocked data.
    """
    # Mock the return value of os.scandir to return a list of mock directories
    mock_dir_entry = type('MockDirEntry', (object,), {'is_dir': lambda: True, 'name': '1', 'path': '/proc/1'})
    mock_scandir.return_value = [mock_dir_entry]

    # Mock the return value of parse_status
    mock_parse_status.return_value = {'name': 'nginx', 'pid': 1}

    # Call the function
    stats = process_stats()

    # Assert the results
    assert len(stats) == 1
    assert stats[0]['name'] == 'nginx'
    assert stats[0]['pid'] == 1

