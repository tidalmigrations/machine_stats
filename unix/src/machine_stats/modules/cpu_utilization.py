#!/usr/bin/python

ANSIBLE_METADATA = {"metadata_version": "1.1"}

from time import sleep

from ansible.module_utils.basic import AnsibleModule


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        timeout=dict(type="int", required=False, default=30),
        only_value=dict(type="bool", required=False, default=False),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(changed=False, timeout=0, ansible_cpu_utilization=None)

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # if timeout is specified to 0, that means that the module is disabled
    # or
    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications

    if module.params["timeout"] == 0 or module.check_mode:
        return module.exit_json(**result)

    # get CPU utilization values
    try:
        if module.params["only_value"]:
            value, rtc_date, rtc_time = cpu_utilization_value(module.params["timeout"])
            result["ansible_cpu_utilization"] = dict(
                value=value, rtc_date=rtc_date, rtc_time=rtc_time
            )
        else:
            average, peak, rtc_date, rtc_time = cpu_utilization(
                module.params["timeout"]
            )
            result["ansible_cpu_utilization"] = dict(
                average=average, peak=peak, rtc_date=rtc_date, rtc_time=rtc_time
            )
    except Exception as e:
        return module.fail_json(msg=str(e), **result)

    # manipulate or modify the state as needed
    result["timeout"] = module.params["timeout"]

    return module.exit_json(**result)


def get_perf():
    with open("/proc/stat") as f:
        fields = [float(column) for column in f.readline().strip().split()[1:]]
        idle, total = fields[3], sum(fields)
        return idle, total


def get_date_time():
    with open("/proc/driver/rtc") as t:
        rtc_time_line = t.readline().strip().split()
        rtc_date_line = t.readline().strip().split()

        rtc_time = rtc_time_line[2]
        rtc_date = rtc_date_line[2]

        return rtc_date, rtc_time


def cpu_utilization(timeout=1):
    """
    Calculate CPU utilization over a given timeout period.
    :param timeout: Duration in seconds to monitor CPU utilization.
    :return: Tuple containing average utilization, peak utilization,
                RTC date, and RTC time.

    The default value is 1, which causes the function to run 1 time.
    So if timeout is less than 1, return zeros.

    """
    last_idle = last_total = total_runs = 0
    cpu_stats = []

    if timeout < 1:
        return 0, 0, 0, 0

    while total_runs < timeout:
        idle, total = get_perf()
        idle_delta, total_delta = idle - last_idle, total - last_total
        last_idle, last_total = idle, total
        if total_delta == 0:
            utilisation = 0.0
        else:
            utilisation = 100.0 * (1.0 - idle_delta / total_delta)
        cpu_stats.append(utilisation)
        total_runs += 1
        sleep(1)

    rtc_date, rtc_time = get_date_time()

    average = sum(cpu_stats) / len(cpu_stats)
    peak = max(cpu_stats)

    return average, peak, rtc_date, rtc_time


def cpu_utilization_value(timeout):
    """
    Calculate CPU utilization over a given timeout period.
    :param timeout: Duration in seconds to monitor CPU utilization.
    :return: Tuple containing utilization, RTC date, and RTC time.
    """
    last_idle, last_total = get_perf()
    rtc_date, rtc_time = get_date_time()

    sleep(timeout)
    idle, total = get_perf()
    idle_delta, total_delta = idle - last_idle, total - last_total
    if total_delta == 0:
        utilization = 0.0
    else:
        utilization = 100.0 * (1.0 - idle_delta / total_delta)

    return utilization, rtc_date, rtc_time


def main():
    run_module()


if __name__ == "__main__":
    main()
