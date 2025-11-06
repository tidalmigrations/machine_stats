"""
Script to prepare JSON output for tidal sync servers from the list of hosts
"""

import argparse
import json
import os
import shutil
from functools import partial
from machine_stats.config import load_config
import tempfile
import ansible_runner
import ansible.constants as C
from ansible.plugins.callback import CallbackBase
from ansible.utils.color import colorize, hostcolor
from ansible.utils.display import Display
from pluginbase import PluginBase
from machine_stats._version import __version__
# Setting default configuration parameters
default_config = {
    "ANSIBLE_HOST_KEY_CHECKING": "False",
    "ANSIBLE_GATHER_TIMEOUT": "180",
    "ANSIBLE_SSH_ARGS": "-o ServerAliveInterval=10",
}
for k, v in default_config.items():
    os.environ[k] = v

# For easier usage calculate the path relative to here.
here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)

display = Display()


class PluginManager:
    """
    Plugin manager for machine_stats
    """

    def __init__(self):
        # Setup a plugin base for "machine_stats.plugins" and make sure to load
        # all the default built-in plugins from the plugins folder.
        self._base = PluginBase(
            package="machine_stats_plugins", searchpath=[get_path("./plugins")]
        )

        self._source = self._base.make_plugin_source(searchpath=[])

    def __getattr__(self, fn):
        def method(*args, **kwargs):
            for plugin_name in self._source.list_plugins():
                plugin = self._source.load_plugin(plugin_name)
                if not hasattr(plugin, fn):
                    display.warning(
                        "no method '%s' for plugin '%s'" % (fn, plugin_name)
                    )
                    break
                # calling a function of a module by using its name (a string)
                getattr(plugin, fn)(*args, **kwargs)

        return method


def ram_allocated_gb(facts):
    """Return total memory allocation in GB"""
    return facts["ansible_memtotal_mb"] / 1024


def ram_used_gb(facts):
    """Return used memory in GB"""
    return (facts["ansible_memtotal_mb"] - facts["ansible_memfree_mb"]) / 1024


def _size(key, mounts):
    return sum([item.get(key, 0) for item in mounts])


def storage_allocated_gb(facts):
    """Return total storage allocation in GB"""
    if "ansible_mounts" not in facts:
        return 0
    return _size("size_total", facts["ansible_mounts"]) / 1024**3


def storage_used_gb(facts):
    """Return used storage in GB"""
    if "ansible_mounts" not in facts:
        return 0
    return (
        _size("size_total", facts["ansible_mounts"])
        - _size("size_available", facts["ansible_mounts"])
    ) / 1024**3


def cpu_logical_processors(facts):
    """Return the number of CPU logical processors."""
    return int(facts.get("ansible_processor_vcpus", 0))


def cpu_name(proc):
    """Return CPU name"""
    items_count = len(proc)
    if items_count == 1:
        return proc[0]
    if items_count >= 3:
        return proc[2]
    return "Unknown"


def ip_addresses(facts):
    """Return IP addresses formatted for the tidal API"""
    return list(
        map(
            lambda ip: {"address": ip},
            facts["ansible_all_ipv4_addresses"] + facts["ansible_all_ipv6_addresses"],
        )
    )


class ShimHost:
    """Shim for ansible.inventory.host.Host"""

    def __init__(self, name):
        self._name = name

    def get_name(self):
        """Return host name"""
        return self._name


class ShimResult:
    """Shim for ansible.executor.task_result.TaskResult"""

    def __init__(self, event):
        self._result = event["event_data"].get("res", {})
        self._host = ShimHost(event["event_data"]["host"])


class ResultCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin.
    """

    def __init__(self, plugins, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._total_results = None
        self._plugins = plugins

    def v2_runner_on_unreachable(self, result):
        host = result._host  # pylint: disable=protected-access
        self._display.error(
            "{0}: {1}".format(
                host.get_name(),
                result._result["msg"],  # pylint: disable=protected-access
            ),
            wrap_text=False,
        )

    def v2_runner_on_failed(self, result, *args, **kwargs):
        del args, kwargs  # Unused
        host = result._host  # pylint: disable=protected-access
        self._display.error(
            "{0}: {1}".format(
                host.get_name(),
                result._result["msg"],  # pylint: disable=protected-access
            ),
            wrap_text=False,
        )

    def update_results(self, host, data: dict):
        if self._total_results is None:
            self._total_results = {}

        if host not in self._total_results:
            self._total_results[host] = data
            return

        # Ensure we append any custom fields, rather than overwriting them
        if "custom_fields" in data and "custom_fields" in self._total_results[host]:
            combined_custom_fields = {
                **self._total_results[host]["custom_fields"],
                **data["custom_fields"],
            }
            data["custom_fields"].update(combined_custom_fields)
            self._total_results[host].update(data)
            return

        self._total_results[host].update(data)

    def v2_runner_on_ok(self, result):
        self._plugins.ok_callback(self, result)
        facts = result._result.get("ansible_facts")  # pylint: disable=protected-access
        if facts is None:
            return

        host = result._host.get_name()
        self.update_results(
            host,
            {
                "host_name": facts["ansible_hostname"],
                "fqdn": facts["ansible_fqdn"],
                "ip_addresses": facts["ansible_all_ipv4_addresses"]
                + facts["ansible_all_ipv6_addresses"],
                "ram_allocated_gb": ram_allocated_gb(facts),
                "ram_used_gb": ram_used_gb(facts),
                "storage_allocated_gb": storage_allocated_gb(facts),
                "storage_used_gb": storage_used_gb(facts),
                "cpu_count": cpu_logical_processors(facts),
                "operating_system": facts["ansible_distribution"],
                "operating_system_version": facts["ansible_distribution_version"],
                "cpu_name": cpu_name(facts["ansible_processor"]),
            },
        )

    def _display_results(self, host, result):
        self._display.display(
            "%s : %s %s %s %s %s %s %s"
            % (
                hostcolor(host, result),
                colorize("ok", result["ok"], C.COLOR_OK),  # pylint: disable=no-member
                colorize(
                    "changed",
                    result["changed"],
                    C.COLOR_CHANGED,  # pylint: disable=no-member
                ),
                colorize(
                    "unreachable",
                    result["unreachable"],
                    C.COLOR_UNREACHABLE,  # pylint: disable=no-member
                ),
                colorize(
                    "failed",
                    result["failures"],
                    C.COLOR_ERROR,  # pylint: disable=no-member
                ),
                colorize(
                    "skipped",
                    result["skipped"],
                    C.COLOR_SKIP,  # pylint: disable=no-member
                ),
                colorize(
                    "rescued",
                    result["rescued"],
                    C.COLOR_OK,  # pylint: disable=no-member
                ),
                colorize(
                    "ignored",
                    result["ignored"],
                    C.COLOR_WARN,  # pylint: disable=no-member
                ),
            ),
            screen_only=True,
            stderr=True,
        )

    def v2_playbook_on_stats(self, stats):
        if self._total_results is not None:
            print(
                json.dumps(
                    {"servers": list(self._total_results.values())},
                    indent=4,
                    sort_keys=True,
                )
            )

        self._display.display("MACHINE STATS RECAP", stderr=True)

        hosts = sorted(stats.get("processed", {}).keys())
        for host in hosts:  # pylint: disable=invalid-name
            result = {
                "ok": stats.get("ok", {}).get(host, 0),
                "changed": stats.get("changed", {}).get(host, 0),
                "unreachable": stats.get("dark", {}).get(host, 0),
                "failures": stats.get("failures", {}).get(host, 0),
                "skipped": stats.get("skipped", {}).get(host, 0),
                "rescued": stats.get("rescued", {}).get(host, 0),
                "ignored": stats.get("ignored", {}).get(host, 0),
            }
            self._display_results(host, result)

        self._display.display("", screen_only=True, stderr=True)


class MeasurementsResultCallback(ResultCallback):
    """
    How to measure fields

    The fields that need to be tracked can be added in the fields_to_measure list.
    If it's a custom field, please add it to the custom_fields_to_measure list.
    """

    def v2_playbook_on_stats(self, stats):
        """Process JSON payload

        Go through each server in the results, and for the fields mentioned in the
        `fields_to_measure` or `custom_fields_to_measure`, add its measurements to the
        transformed data.
        """

        fields_to_measure = []
        custom_fields_to_measure = ["cpu_average", "cpu_peak", "cpu_utilization"]

        transformed_json_payload = []
        if self._total_results:
            for server in list(self._total_results.values()):
                for field in server:
                    # Add data (ram_used_gb) from fields_to_measure list to the transformed_json_payload list
                    if field in fields_to_measure:
                        server_dict = {}
                        server_dict["measurable_type"] = "server"
                        server_dict["field_name"] = field + "_timeseries"
                        server_dict["value"] = server[field]
                        server_dict["measurable"] = {"host_name": server["host_name"]}

                        transformed_json_payload.append(server_dict)

                    # Add custom fields data (cpu_average) from custom_fields_to_measure list to the transformed_json_payload list
                    elif field == "custom_fields":
                        for custom_field in server["custom_fields"]:
                            if custom_field in custom_fields_to_measure:
                                server_dict = {}
                                server_dict["measurable_type"] = "server"
                                server_dict["field_name"] = custom_field + "_timeseries"
                                server_dict["value"] = server["custom_fields"][
                                    custom_field
                                ]
                                server_dict["external_timestamp"] = server[
                                    "custom_fields"
                                ]["cpu_utilization_timestamp"]
                                server_dict["measurable"] = {
                                    "host_name": server["host_name"]
                                }

                                transformed_json_payload.append(server_dict)

        if self._total_results is not None:
            print(
                json.dumps(
                    {"measurements": list(transformed_json_payload)},
                    indent=4,
                    sort_keys=True,
                )
            )


class Application:  # pylint: disable=too-few-public-methods
    """Machine Stats application"""

    def __init__(
        self, *, sources: list = None, plugins: PluginManager, args: argparse.Namespace
    ):
        if sources is None:
            sources = []
        self._sources = sources
        self._plugins = plugins
        self.args = args

        self._playbook_tasks = []

        self._plugins.setup(self)

    def add_playbook_tasks(self, *args):
        for arg in args:
            if isinstance(arg, list):
                self._playbook_tasks.extend(arg)
            else:
                self._playbook_tasks.append(arg)

    def playbook_tasks(self):
        if not self._playbook_tasks:
            return None
        return self._playbook_tasks

    def _run_ansible(self, play_source, private_data_dir, passwords):
        """Run Ansible playbook and process events."""
        runner = ansible_runner.run(
            private_data_dir=private_data_dir,
            playbook=[play_source],
            passwords=passwords,
            forks=10,
            verbosity=3,
            quiet=True,
        )

        if self.args.measurement:
            results_callback = MeasurementsResultCallback(plugins=self._plugins)
        else:
            results_callback = ResultCallback(plugins=self._plugins)

        for event in runner.events:
            if event["event"] == "runner_on_ok":
                results_callback.v2_runner_on_ok(ShimResult(event))
            elif event["event"] == "runner_on_unreachable":
                results_callback.v2_runner_on_unreachable(ShimResult(event))
            elif event["event"] == "runner_on_failed":
                results_callback.v2_runner_on_failed(ShimResult(event))

        results_callback.v2_playbook_on_stats(runner.stats)

    def _copy_inventory_files(self, private_data_dir):
        # for each source in self._sources: copy it to private_data_dir/inventory
        for index, source in enumerate(self._sources):
            inventory_dir = os.path.join(private_data_dir, "inventory")
            os.makedirs(inventory_dir, exist_ok=True)
            dest_file = os.path.join(inventory_dir, f"hosts_{index}")
            shutil.copy(source, dest_file)

    def run(self):
        """Run the Application"""
        play_source = dict(
            name="Ansible Play",
            hosts="all",
            gather_facts="yes",
            tasks=self.playbook_tasks(),
        )

        private_data_dir = tempfile.mkdtemp()
        passwords = dict(vault_pass="secret")
        os.environ["ANSIBLE_LIBRARY"] = get_path("modules")

        self._copy_inventory_files(private_data_dir)

        self._run_ansible(play_source, private_data_dir, passwords)

        # Remove ansible tmpdir
        shutil.rmtree(private_data_dir)


def main():
    """Main"""
    load_config()
    plugins = PluginManager()
    parser = argparse.ArgumentParser(prog="machine_stats")
    parser.add_argument(
        "hosts",
        metavar="FILE",
        type=argparse.FileType("r"),
        help="inventory file (default 'hosts')",
        nargs="*",
    )

    parser.add_argument(
        "-v",
        "--version",
        help="print the machine stats version",
        action="store_true",)

    measurement_args = parser.add_argument_group("measurements arguments")
    measurement_args.add_argument(
        "-m",
        "--measurement",
        action="store_true",
        help="enable measurements",
    )

    plugins.add_arguments(parser)

    args = parser.parse_args()

    if args.version:
        print(f"machine_stats, version {__version__}")
        return

    if not args.hosts:
        try:
            with open("hosts", "r") as f:  # pylint: disable=invalid-name
                # append the fully qualified path
                args.hosts.append(f)
        except FileNotFoundError:
            pass

    sources = list(map(lambda f: f.name, args.hosts))

    app = Application(sources=sources, plugins=plugins, args=args)
    app.run()


if __name__ == "__main__":
    main()
