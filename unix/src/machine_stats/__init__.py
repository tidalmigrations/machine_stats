"""
Script to prepare JSON output for tidal sync servers from the list of hosts
"""

import argparse
import json
import os
import shutil
from functools import partial

from ansible.utils.path import unfrackpath

# Setting default configuration parameters
default_config = {
    "ANSIBLE_HOST_KEY_CHECKING": "False",
    "ANSIBLE_GATHER_TIMEOUT": "180",
}
for k, v in default_config.items():
    os.environ[k] = v

# Loading config file must be prior to importing most of the ansible.* packages
def find_config_file():
    """Find configuration file"""

    potential_paths = []
    cfg_files = [
        "machine_stats.cfg",
        "machine-stats.cfg",
        "machinestats.cfg",
    ]

    # Look for config file in the current working directory
    try:
        cwd = os.getcwd()
        for cfg_file in cfg_files:
            cwd_cfg = os.path.join(cwd, cfg_file)
            potential_paths.append(cwd_cfg)
    except OSError:
        # If we can't access cwd, we'll simply skip it as a possible config source
        pass

    # Per user location
    for cfg_file in cfg_files:
        potential_paths.append(unfrackpath("~/." + cfg_file, follow=False))

    for path in potential_paths:
        if os.path.exists(path) and os.access(path, os.R_OK):
            break
    else:
        path = None

    return path


# Do nothing if ANSIBLE_CONFIG environment variable was already set.
if "ANSIBLE_CONFIG" in os.environ:
    pass
else:
    cfg_file = find_config_file()
    if cfg_file is not None:
        os.environ["ANSIBLE_CONFIG"] = cfg_file

import ansible.constants as C
from ansible import context
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.inventory.manager import InventoryManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from ansible.utils.color import colorize, hostcolor
from ansible.utils.display import Display
from ansible.vars.manager import VariableManager
from pluginbase import PluginBase

# For easier usage calculate the path relative to here.
here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)

display = Display()


class PluginManager(object):
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
                    return None
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
    return _size("size_total", facts["ansible_mounts"]) / 1024 ** 3


def storage_used_gb(facts):
    """Return used storage in GB"""
    if "ansible_mounts" not in facts:
        return 0
    return (
        _size("size_total", facts["ansible_mounts"])
        - _size("size_available", facts["ansible_mounts"])
    ) / 1024 ** 3


def cpu_count(facts):
    """Return the number of CPUs"""
    return max(
        [
            int(facts.get("ansible_processor_count", 0)),
            int(facts.get("ansible_processor_vcpus", 0)),
        ]
    )


def cpu_name(proc):
    """Return CPU name"""
    items_count = len(proc)
    if items_count == 1:
        return proc[0]
    if items_count >= 3:
        return proc[2]
    return "Unknown"


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
        else:
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
                "cpu_count": cpu_count(facts),
                "operating_system": facts["ansible_distribution"],
                "operating_system_version": facts["ansible_distribution_version"],
                "cpu_name": cpu_name(facts["ansible_processor"]),
            },
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

        hosts = sorted(stats.processed.keys())
        for h in hosts:  # pylint: disable=invalid-name
            t = stats.summarize(h)  # pylint: disable=invalid-name

            self._display.display(
                u"%s : %s %s %s %s %s %s %s"
                % (
                    hostcolor(h, t),
                    colorize(u"ok", t["ok"], C.COLOR_OK),  # pylint: disable=no-member
                    colorize(
                        u"changed",
                        t["changed"],
                        C.COLOR_CHANGED,  # pylint: disable=no-member
                    ),
                    colorize(
                        u"unreachable",
                        t["unreachable"],
                        C.COLOR_UNREACHABLE,  # pylint: disable=no-member
                    ),
                    colorize(
                        u"failed",
                        t["failures"],
                        C.COLOR_ERROR,  # pylint: disable=no-member
                    ),
                    colorize(
                        u"skipped",
                        t["skipped"],
                        C.COLOR_SKIP,  # pylint: disable=no-member
                    ),
                    colorize(
                        u"rescued",
                        t["rescued"],
                        C.COLOR_OK,  # pylint: disable=no-member
                    ),
                    colorize(
                        u"ignored",
                        t["ignored"],
                        C.COLOR_WARN,  # pylint: disable=no-member
                    ),
                ),
                screen_only=True,
                stderr=True,
            )

        self._display.display("", screen_only=True, stderr=True)


class MeasurementsResultCallback(ResultCallback):
    def v2_playbook_on_stats(self, stats):
        """How to measure fields

        The fields that need to be tracked can be added in the fields_to_measure list.
        If it's a custom field, please add it to the custom_fields_to_measure list.
        """

        fields_to_measure = []
        custom_fields_to_measure = ["cpu_average", "cpu_peak", "cpu_utilization"]

        """Process JSON payload

        Go through each server in the results, and for the fields mentioned in the 
        `fields_to_measure` or `custom_fields_to_measure`, add its measurements to the
        transformed data.
        """

        transformed_json_payload = []
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
                            server_dict["value"] = server["custom_fields"][custom_field]
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
            sources = list()
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

    def run(self):
        """Run the Application"""

        # Since the API is constructed for CLI it expects certain options to
        # always be set in the context object
        context.CLIARGS = ImmutableDict(
            connection="smart",
            module_path=[get_path("./modules"), "/usr/share/ansible"],
            forks=10,
            become=None,
            become_method=None,
            become_user=None,
            check=False,
            diff=False,
            verbosity=3,
        )

        # Initialize needed objects
        loader = DataLoader()  # Takes care of finding and reading yaml, json and
        # ini files
        passwords = dict(vault_pass="secret")

        # Instantiate our ResultCallback for handling results as they come in
        if self.args.measurement:
            results_callback = MeasurementsResultCallback(plugins=self._plugins)
        else:
            results_callback = ResultCallback(plugins=self._plugins)

        # Create inventory, use path to host config file as source or hosts in a
        # comma separated string
        inventory = InventoryManager(loader=loader, sources=self._sources)

        # Variable manager takes care of merging all the different sources to give
        # you a unified view of variables available in each context
        variable_manager = VariableManager(loader=loader, inventory=inventory)

        # Instantiate task queue manager, which takes care of forking and setting
        # up all objects to iterate over host list and tasks
        # IMPORTANT: This also adds library dirs paths to the module loader
        # IMPORTANT: and so it must be initialized before calling `Play.load()`.
        tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            passwords=passwords,
            stdout_callback=results_callback,  # Use our custom callback instead of
            # the ``default`` callback plugin,
            # which prints to stdout
        )

        # Create data structure that represents our play, including tasks, this is
        # basically what our YAML loader does internally.
        play_source = dict(
            name="Ansible Play",
            hosts="all",
            gather_facts="yes",
            tasks=self.playbook_tasks(),
        )

        # Create play object, playbook objects use .load instead of init or new
        # methods, this will also automatically create the task objects from the
        # info provided in play_source
        play = Play().load(
            play_source, variable_manager=variable_manager, loader=loader
        )

        # Actually run it
        try:
            tqm.load_callbacks()
            tqm.run(play)
            tqm.send_callback(
                "v2_playbook_on_stats",
                tqm._stats,  # pylint: disable=protected-access
            )
        finally:
            # We always need to cleanup child procs and the structures we use to
            # communicate with them
            tqm.cleanup()
            if loader:
                loader.cleanup_all_tmp_files()

            # Remove ansible tmpdir
            shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)  # pylint: disable=no-member

            if tqm is not None:
                tqm.cleanup()


def main():
    """Main"""
    plugins = PluginManager()
    parser = argparse.ArgumentParser(prog="machine_stats")
    parser.add_argument(
        "hosts",
        metavar="FILE",
        type=argparse.FileType("r"),
        help="inventory file (default 'hosts')",
        nargs="*",
    )

    measurement_args = parser.add_argument_group("measurements arguments")
    measurement_args.add_argument(
        "-m",
        "--measurement",
        action="store_true",
        help="enable measurements",
    )

    plugins.add_arguments(parser)

    args = parser.parse_args()
    if not args.hosts:
        try:
            with open("hosts", "r") as f:  # pylint: disable=invalid-name
                args.hosts.append(f)
        except FileNotFoundError:
            pass

    sources = list(map(lambda f: f.name, args.hosts))
    app = Application(sources=sources, plugins=plugins, args=args)
    app.run()


if __name__ == "__main__":
    main()
