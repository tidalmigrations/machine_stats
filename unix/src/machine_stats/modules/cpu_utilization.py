#!/usr/bin/python

ANSIBLE_METADATA = {"metadata_version": "1.1"}

from time import sleep

from ansible.module_utils.basic import AnsibleModule


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(timeout=dict(type="int", required=False, default=30))

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
    if module.params["timeout"] == 0:
        module.exit_json(**result)

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # get CPU utilization values
    try:
        average, peak = cpu_utilization(module.params["timeout"])
    except Exception as e:
        module.fail_json(msg=str(e), **result)

    # manipulate or modify the state as needed
    result["timeout"] = module.params["timeout"]
    result["ansible_cpu_utilization"] = dict(average=average, peak=peak)

    module.exit_json(**result)


def cpu_utilization(timeout):
    last_idle = last_total = total_runs = 0
    cpu_stats = []

    while total_runs < timeout:
        with open("/proc/stat") as f:
            fields = [float(column) for column in f.readline().strip().split()[1:]]
        idle, total = fields[3], sum(fields)
        idle_delta, total_delta = idle - last_idle, total - last_total
        last_idle, last_total = idle, total
        utilisation = 100.0 * (1.0 - idle_delta / total_delta)
        cpu_stats.append(utilisation)
        total_runs += 1
        sleep(1)

    average = sum(cpu_stats) / len(cpu_stats)
    peak = max(cpu_stats)

    return average, peak


def main():
    run_module()


if __name__ == "__main__":
    main()
