import ansible_runner

def run():
    r = ansible_runner.run(private_data_dir='./src/machine_stats/modules/raw',
                       host_pattern='all',
                       module='raw',
                       module_args="lsb_release -si")

    # r = ansible_runner.run(private_data_dir='./ansible', playbook='playbook-ubuntu.yml')
