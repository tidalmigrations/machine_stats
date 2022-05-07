"""
Remote servers (or hosts) are referred as `servers` in this file
to avoid possible confusion with the `hosts` file.
"""

import ansible_runner
import json

def run():
    """run()
    Run Ansible Playbook and print results

    Run the Ansible Playbook `master-playbook.yml` for all the 
    servers in the `hosts` file. Get the output and process it
    before showing the results back to the user.
    """
    # Get a list of all the servers from `hosts` file
    servers_list = get_servers()

    # Run the Ansible Playbook for all the servers
    app_run_data = ansible_runner.run(private_data_dir='./src/machine_stats/modules/raw',
                           quiet=True,
                        #    json_mode=True,
                           playbook='master-playbook.yml')

    raw_output_all_servers = filter_data_for_all_servers(app_run_data,servers_list)

    # clear memory
    app_run_data.clear()

    unprocessed_output = process_data_for_each_server(raw_output_all_servers, servers_list)

    # TODO: Pass the unprocessed_output we are getting through a validation layer
    
    print(json.dumps(unprocessed_output, sort_keys=True, indent=4))


def get_servers():
    """get_servers
    get a list of servers from `hosts` file

    This method fetches the inventory/hosts file and gets
    the tuple of hosts.
    While returning it is converted to a list.
    """
    inventory = ansible_runner.get_inventory(inventories=['./src/machine_stats/modules/raw/inventory'],
                                     action='list',
                                     quiet=True,
                                     response_format='json')
    return list(inventory[0]['_meta']['hostvars'].keys())


def filter_data_for_all_servers(app_run_data, servers_list):

    # Stores only necessary events received from ansible runner and
    # divides them for each server
    servers_events = {}

    for server in servers_list:
        servers_events[server] = []

    # From all the events for all the servers, 
    for task in app_run_data.events:
        try:
            if(task['event_data']['host'] and task['event_data']['res']['msg']):
                servers_events[task['event_data']['host']].append(task)
        except KeyError:
            # KeyError is passed because playbook_on_task_start event
            # does not contain the `task['event_data']['host']` key
            pass
    
    return servers_events

def process_data_for_each_server(servers_events, servers_list):

    """
    TODO: Finish writing this function
    - read server_events dict for each server
    - fetch the value of each field (i.e., cpu_name, cpu_count)
      - some fields doesn't have a command to get the values (i.e., cpu average/peak)
      - values of some fields need to be processed before they can be used. i.e., 
        - convert fields from bytes/MB to GB
        - to get storage_used we will subtract storage_free from storage allocated
    - Add the results in servers_dictionary and return the results
    """

    # Stores the unprocessed (machine stats-like) output
    servers_dictionary = {"servers": []}

    for server_events in servers_events:
            for server in server_events:
                # TODO: read description above
                pass
    
    return servers_dictionary
