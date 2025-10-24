import pytest
from unittest.mock import patch, mock_open, MagicMock
from src.machine_stats.modules.proc_stats import parse_status, process_stats, run_module

def test_parse_status():
    """
    Test the parse_status function with mocked data.
    """
    status_file_content = 'Name:\tnginx\nUmask:\t0000\nState:\tS (sleeping)\nTgid:\t1\nNgid:\t0\nPid:\t1\nPPid:\t0\nUid:\t0\t0\t0\t0\nVmPeak:\t168 kB\nVmSize:\t168 kB\n'
    with patch('src.machine_stats.modules.proc_stats.os.stat') as mock_stat, \
         patch('src.machine_stats.modules.proc_stats.Path.resolve') as mock_resolve, \
         patch('builtins.open', mock_open(read_data=status_file_content)), \
         patch('src.machine_stats.modules.proc_stats.time') as mock_time, \
         patch('src.machine_stats.modules.proc_stats.getpwuid') as mock_getpwuid:

        # Mock the return value of os.stat
        mock_stat.return_value.st_ctime = 1672531200  # 2023-01-01 00:00:00 UTC

        # Mock the return value of time.time
        mock_time.return_value = 1672531260 # 60 seconds later

        # Mock the return value of Path.resolve
        mock_resolve.return_value = '/usr/sbin/nginx'
        mock_getpwuid.return_value.pw_name = 'root'

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


def test_parse_status_resolve_fails():
    """
    Test parse_status when Path.resolve() fails.
    """
    with patch('src.machine_stats.modules.proc_stats.Path.resolve', side_effect=Exception("Permission denied")):
        stats = parse_status('/proc/1')
    assert stats == {}

def test_parse_status_getpwuid_fails():
    """
    Test parse_status when getpwuid fails and it falls back to UID.
    """
    status_file_content = 'Pid:\t1\nPPid:\t0\nUid:\t1001\t1001\t1001\t1001\n'
    with patch('src.machine_stats.modules.proc_stats.os.stat'), \
         patch('src.machine_stats.modules.proc_stats.Path.resolve'), \
         patch('builtins.open', mock_open(read_data=status_file_content)), \
         patch('src.machine_stats.modules.proc_stats.time'), \
         patch('src.machine_stats.modules.proc_stats.getpwuid', side_effect=KeyError):

        stats = parse_status('/proc/1')

    assert stats['user'] == '1001'

def test_parse_status_missing_fields():
    """
    Test parse_status with a status file missing memory fields.
    """
    status_file_content = 'Name:\tnginx\nPid:\t1\nPPid:\t0\nUid:\t0\n'
    with patch('src.machine_stats.modules.proc_stats.os.stat'), \
        patch('src.machine_stats.modules.proc_stats.Path.resolve'), \
        patch('builtins.open', mock_open(read_data=status_file_content)), \
        patch('src.machine_stats.modules.proc_stats.time'), \
        patch('src.machine_stats.modules.proc_stats.getpwuid'):
        stats = parse_status('/proc/1')

    assert 'memory_used_mb' not in stats
    assert 'max_memory_used_mb' not in stats


@patch('src.machine_stats.modules.proc_stats.parse_status')
@patch('src.machine_stats.modules.proc_stats.os.scandir')
def test_process_stats(mock_scandir, mock_parse_status):
    """
    Test the process_stats function with mocked data.
    """
    # Mock directory entries
    proc_dir = '/proc'
    p1 = type('MockDirEntry', (object,), {'is_dir': lambda: True, 'name': '1', 'path': f'{proc_dir}/1'})()
    p2 = type('MockDirEntry', (object,), {'is_dir': lambda: True, 'name': '2', 'path': f'{proc_dir}/2'})()
    not_a_proc = type('MockDirEntry', (object,), {'is_dir': lambda: True, 'name': 'self', 'path': f'{proc_dir}/self'})()
    not_a_dir = type('MockDirEntry', (object,), {'is_dir': lambda: False, 'name': 'version', 'path': f'{proc_dir}/version'})()

    mock_scandir.return_value = [p1, p2, not_a_proc, not_a_dir]

    # Mock parse_status to return one valid result and one empty result
    mock_parse_status.side_effect = [
        {'name': 'nginx', 'pid': 1},
        {}  # This empty dict should be filtered out
    ]

    stats = process_stats()

    assert len(stats) == 1
    assert stats[0]['name'] == 'nginx'
    assert stats[0]['pid'] == 1
    assert mock_parse_status.call_count == 2
    mock_parse_status.assert_any_call('/proc/1')
    mock_parse_status.assert_any_call('/proc/2')


@patch("src.machine_stats.modules.proc_stats.AnsibleModule")
def test_run_module_disabled(mock_ansible_module):
    mock_module = MagicMock()
    mock_module.params = {"process_stats": False}
    mock_ansible_module.return_value = mock_module

    run_module()

    mock_module.exit_json.assert_called_with(changed=False, ansible_proc_stats=None)


@patch("src.machine_stats.modules.proc_stats.AnsibleModule")
def test_run_module_check_mode(mock_ansible_module):
    mock_module = MagicMock()
    mock_module.params = {"process_stats": True}
    mock_module.check_mode = True
    mock_ansible_module.return_value = mock_module

    run_module()

    mock_module.exit_json.assert_called_with(changed=False, ansible_proc_stats=None)


@patch("src.machine_stats.modules.proc_stats.process_stats")
@patch("src.machine_stats.modules.proc_stats.AnsibleModule")
def test_run_module_success(mock_ansible_module, mock_process_stats):
    mock_module = MagicMock()
    mock_module.params = {"process_stats": True}
    mock_module.check_mode = False
    mock_ansible_module.return_value = mock_module

    expected_stats = [{"pid": 1, "name": "test"}]
    mock_process_stats.return_value = expected_stats

    run_module()

    mock_module.exit_json.assert_called_with(changed=False, ansible_proc_stats=expected_stats)


@patch("src.machine_stats.modules.proc_stats.process_stats")
@patch("src.machine_stats.modules.proc_stats.AnsibleModule")
def test_run_module_fail(mock_ansible_module, mock_process_stats):
    mock_module = MagicMock()
    mock_module.params = {"process_stats": True}
    mock_module.check_mode = False
    mock_ansible_module.return_value = mock_module

    error_message = "Test Exception"
    mock_process_stats.side_effect = Exception(error_message)

    run_module()

    mock_module.fail_json.assert_called_with(msg=error_message, changed=False, ansible_proc_stats=None)

