def setup(app):
    process_stats = app.args.process_stats
    if process_stats:
        app.add_playbook_tasks(
            dict(
                action=dict(
                    module="proc_stats", args=dict(process_stats=process_stats)
                ),
            )
        )


def add_arguments(parser):
    parser.add_argument(
        "--process-stats",
        action="store_true",
        help="turn on collecting stats on running processes",
    )


def ok_callback(parent, result):
    host = result._host.get_name()
    process_stats = result._result.get("ansible_proc_stats")
    if process_stats is not None:
        parent.update_results(
            host,
            {"process_stats": process_stats},
        )
