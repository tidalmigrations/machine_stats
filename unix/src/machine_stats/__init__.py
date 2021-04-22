"""
Script to prepare JSON output for tidal sync servers from the list of hosts
"""

import argparse
import json
import shutil

import ansible.constants as C
from ansible import context
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.inventory.manager import InventoryManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from ansible.utils.color import colorize, hostcolor
from ansible.vars.manager import VariableManager


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._total_results = None

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

    def v2_runner_on_ok(self, result):
        facts = result._result["ansible_facts"]  # pylint: disable=protected-access

        if self._total_results is None:
            self._total_results = {"servers": []}

        self._total_results["servers"].append(
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
            }
        )

    def v2_playbook_on_stats(self, stats):
        if self._total_results is not None:
            print(json.dumps(self._total_results, indent=4, sort_keys=True))

        self._display.banner("MACHINE STATS RECAP")

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


class Application:  # pylint: disable=too-few-public-methods
    """Machine Stats application"""

    def __init__(self, *, sources: list = None):
        if sources is None:
            sources = list()
        self._sources = sources

    def run(self):
        """Run the Application"""

        # Since the API is constructed for CLI it expects certain options to
        # always be set in the context object
        context.CLIARGS = ImmutableDict(
            connection="smart",
            module_path=["/to/mymodules", "/usr/share/ansible"],
            forks=10,
            become=None,
            become_method=None,
            become_user=None,
            check=False,
            diff=False,
            verbosity=0,
        )

        # Initialize needed objects
        loader = DataLoader()  # Takes care of finding and reading yaml, json and
        # ini files
        passwords = dict(vault_pass="secret")

        # Instantiate our ResultCallback for handling results as they come in
        results_callback = ResultCallback()

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
        play_source = dict(name="Ansible Play", hosts="all", gather_facts="yes")

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
    parser = argparse.ArgumentParser(prog="machine_stats")
    parser.add_argument(
        "hosts",
        metavar="FILE",
        type=argparse.FileType("r"),
        help="inventory file (default 'hosts')",
        nargs="*",
    )
    args = parser.parse_args()
    if not args.hosts:
        try:
            with open("hosts", "r") as f:  # pylint: disable=invalid-name
                args.hosts.append(f)
        except FileNotFoundError:
            pass

    sources = list(map(lambda f: f.name, args.hosts))
    app = Application(sources=sources)
    app.run()


if __name__ == "__main__":
    main()
