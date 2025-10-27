import pytest
from unittest.mock import patch, mock_open, MagicMock
from src.machine_stats.modules.proc_stats import parse_status, process_stats, run_module, _get_process_exe_info, _parse_proc_status_file, _get_username_from_uid

@patch('src.machine_stats.modules.proc_stats.Path')
def test__get_process_exe_info_success(mock_path):
    mock_path.return_value.resolve.return_value = '/usr/sbin/nginx'
    path, name = _get_process_exe_info('/proc/1')
    assert path == '/usr/sbin'
    assert name == 'nginx'

@patch('src.machine_stats.modules.proc_stats.Path.resolve', side_effect=Exception("Permission denied"))
def test__get_process_exe_info_fails(mock_resolve):
    result = _get_process_exe_info('/proc/1')
    assert result is None

def test__parse_proc_status_file():
    status_file_content = 'Name:\tnginx\nPid:\t1\n'
    with patch('builtins.open', mock_open(read_data=status_file_content)):
        status = _parse_proc_status_file('/proc/1')
    assert status == {'name': 'nginx', 'pid': '1'}

@patch('src.machine_stats.modules.proc_stats.getpwuid')
def test__get_username_from_uid_success(mock_getpwuid):
    mock_getpwuid.return_value.pw_name = 'root'
    username = _get_username_from_uid('0\t0\t0\t0')
    assert username == 'root'
    mock_getpwuid.assert_called_with(0)

@patch('src.machine_stats.modules.proc_stats.getpwuid', side_effect=KeyError)
def test__get_username_from_uid_fails(mock_getpwuid):
    username = _get_username_from_uid('1001\t1001\t1001\t1001')
    assert username == '1001'
    mock_getpwuid.assert_called_with(1001)


@patch('src.machine_stats.modules.proc_stats._get_username_from_uid')
@patch('src.machine_stats.modules.proc_stats._parse_proc_status_file')
@patch('src.machine_stats.modules.proc_stats.os.stat')
@patch('src.machine_stats.modules.proc_stats.time')
@patch('src.machine_stats.modules.proc_stats._get_process_exe_info')
def test_parse_status(mock_get_exe_info, mock_time, mock_stat, mock_parse_status_file, mock_get_username):
    """
    Test the parse_status function with mocked helpers.
    """
    # Mock helpers
    mock_get_exe_info.return_value = ('/usr/sbin', 'nginx')
    mock_time.return_value = 1672531260 # 60 seconds later
    mock_stat.return_value.st_ctime = 1672531200  # 2023-01-01 00:00:00 UTC
    mock_parse_status_file.return_value = {
        'name': 'nginx',
        'pid': '1',
        'ppid': '0',
        'uid': '0\t0\t0\t0',
        'vmpeak': '168 kB',
        'vmsize': '168 kB'
    }
    mock_get_username.return_value = 'root'

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
    mock_get_exe_info.assert_called_with('/proc/1')
    mock_stat.assert_called_with('/proc/1')
    mock_parse_status_file.assert_called_with('/proc/1')
    mock_get_username.assert_called_with('0\t0\t0\t0')


@patch('src.machine_stats.modules.proc_stats._get_process_exe_info', return_value=None)
def test_parse_status_exe_info_fails(mock_get_exe_info):
    """
    Test parse_status returns empty dict when exe info can't be resolved.
    """
    stats = parse_status('/proc/1')
    assert stats == {}
    mock_get_exe_info.assert_called_once_with('/proc/1')


@patch('src.machine_stats.modules.proc_stats._get_username_from_uid')
@patch('src.machine_stats.modules.proc_stats._parse_proc_status_file')
@patch('src.machine_stats.modules.proc_stats.os.stat')
@patch('src.machine_stats.modules.proc_stats.time')
@patch('src.machine_stats.modules.proc_stats._get_process_exe_info')
def test_parse_status_missing_fields(mock_get_exe_info, mock_time, mock_stat, mock_parse_status_file, mock_get_username):
    """
    Test parse_status with a status file missing memory fields.
    """
    mock_get_exe_info.return_value = ('/', 'nginx')
    mock_time.return_value = 1
    mock_stat.return_value.st_ctime = 0
    mock_parse_status_file.return_value = {
        'name': 'nginx', 'pid': '1', 'ppid': '0', 'uid': '0\t0\t0\t0'
    }
    mock_get_username.return_value = 'root'

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
    p1 = type('MockDirEntry', (object,), {'is_dir': lambda self: True, 'name': '1', 'path': f'{proc_dir}/1'})()
    p2 = type('MockDirEntry', (object,), {'is_dir': lambda self: True, 'name': '2', 'path': f'{proc_dir}/2'})()
    not_a_proc = type('MockDirEntry', (object,), {'is_dir': lambda self: True, 'name': 'self', 'path': f'{proc_dir}/self'})()
    not_a_dir = type('MockDirEntry', (object,), {'is_dir': lambda self: False, 'name': 'version', 'path': f'{proc_dir}/version'})()

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
