import argparse


def setup(app):
    timeout = app.args.cpu_utilization_timeout
    only_value = app.args.cpu_utilization_only_value
    if timeout > 0:
        app.add_playbook_tasks(
            dict(
                action=dict(
                    module="cpu_utilization",
                    args=dict(timeout=timeout, only_value=only_value),
                ),
            )
        )


def add_arguments(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--cpu-utilization-timeout",
        metavar="SECONDS",
        type=int,
        default=30,
        help="timeout sampling for CPU utilization",
    )
    parser.add_argument(
        "--cpu-utilization-only-value",
        action="store_true",
        help="calculate only CPU utilization value and not peak and average values",
    )


def ok_callback(parent, result):
    host = result._host.get_name()
    cpu_sampling_timeout = result._result.get("timeout")
    cpu_util = result._result.get("ansible_cpu_utilization")

    if cpu_util is not None:
        if "value" in cpu_util:
            parent.update_results(
                host,
                {
                    "custom_fields": {
                        "cpu_sampling_timeout": cpu_sampling_timeout,
                        "cpu_utilization": cpu_util["value"],
                        "cpu_utilization_timestamp": cpu_util["rtc_date"] + " " + cpu_util["rtc_time"]
                    }
                },
            )
        else:
            parent.update_results(
                host,
                {
                    "custom_fields": {
                        "cpu_sampling_timeout": cpu_sampling_timeout,
                        "cpu_average": cpu_util["average"],
                        "cpu_peak": cpu_util["peak"],
                        "cpu_utilization_timestamp": cpu_util["rtc_date"] + " " + cpu_util["rtc_time"]
                    }
                },
            )
