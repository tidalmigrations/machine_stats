def setup(app):
    timeout = app.args.cpu_utilization_timeout
    if timeout > 0:
        app.add_playbook_tasks(
            dict(
                action=dict(module="cpu_utilization", args=dict(timeout=timeout)),
            )
        )


def add_arguments(parser):
    parser.add_argument(
        "--cpu-utilization-timeout",
        metavar="SECONDS",
        type=int,
        default=30,
        help="timeout sampling for CPU utilization",
    )


def ok_callback(parent, result):
    host = result._host.get_name()
    cpu_sampling_timeout = result._result.get("timeout")
    cpu_util = result._result.get("ansible_cpu_utilization")
    if cpu_util is not None:
        parent.update_results(
            host,
            {
                "custom_fields": {
                    "cpu_sampling_timeout": cpu_sampling_timeout,
                    "cpu_average": cpu_util["average"],
                    "cpu_peak": cpu_util["peak"],
                }
            },
        )
