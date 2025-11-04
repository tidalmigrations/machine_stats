import os
import unittest
from unittest.mock import patch

from machine_stats.config import find_config_file, load_config


class TestConfig(unittest.TestCase):
    def test_find_config_file(self):
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            with patch("os.access") as mock_access:
                mock_access.return_value = True
                # Test that the function finds a config file in the current directory
                with patch("os.getcwd") as mock_getcwd:
                    mock_getcwd.return_value = "/tmp"
                    self.assertEqual(find_config_file(), "/tmp/machine_stats.cfg")

    def test_load_config(self):
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            with patch("os.access") as mock_access:
                mock_access.return_value = True
                with patch.dict(os.environ, {}, clear=True):
                    with patch("os.getcwd") as mock_getcwd:
                        mock_getcwd.return_value = "/tmp"
                        load_config()
                        self.assertEqual(
                            os.environ["ANSIBLE_CONFIG"], "/tmp/machine_stats.cfg"
                        )


if __name__ == "__main__":
    unittest.main()