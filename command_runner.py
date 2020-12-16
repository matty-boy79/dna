import time
import json
import urllib3
import requests
import variables
from dnacentersdk import api
from requests.auth import HTTPBasicAuth

# Set Constants
SERVER = variables.DNAC_SERVER
USER = variables.DNAC_USER
PASSWORD = variables.DNAC_PASSWORD
VERSION = variables.DNAC_VERSION

# Disable warnings about untrusted certs
urllib3.disable_warnings()

# Create a global DNACenterAPI Connection Object to be used for subsequent API calls
dnac = api.DNACenterAPI(username=USER, password=PASSWORD, base_url=SERVER, version=VERSION, verify=False)


def get_auth_token():
    path = "/dna/system/api/v1/auth/token"
    url = SERVER + path
    hdr = {'content-type': 'application/json'}

    response = requests.post(url, auth=HTTPBasicAuth(USER, PASSWORD), headers=hdr, verify=False).json()
    token = (response['Token'])
    return token


def read_commands_file():
    # Count the number of lines (commands) in the commands input file and print an error if empty
    command_count = len(open('commands.txt').readlines())
    if command_count == 0:
        print('commands.txt must contain at least one Cisco show command.')
        exit(1)

    # Create an empty list to store the commands read from the input file
    list_of_commands = []

    # Populate the list with commands from the input file
    with open('commands.txt', 'r') as cmds_file:
        for line in cmds_file:
            list_of_commands.append(line.strip())

    return list_of_commands


def divide_list_into_chunks(my_list, n):
    # Function to split a list of entries into multiple lists with max length = 'n'
    # looping till length l
    for i in range(0, len(my_list), n):
        yield my_list[i:i + n]


def get_file_id_from_task(task_id):
    task_status = dnac.task.get_task_by_id(task_id)
    while "endTime" not in task_status['response']:
        time.sleep(5)
        print("Still Waiting...")
        task_status = dnac.task.get_task_by_id(task_id)
    return json.loads(task_status.response.progress)['fileId']


def get_file_contents(command_list, file_to_download, auth_token):
    # Create the HTTP headers
    hdr = {
        'content-type': 'application/json',
        'X-Auth-Token': auth_token
    }

    # Set the path and create the full URL for the GET
    path = f'/dna/intent/api/v1/file/{file_to_download}'
    url = SERVER + path

    # GET the file and convert the contents to JSON
    response = requests.get(url=url, headers=hdr, verify=False).json()

    # Loop through the response object printing each command from each device to the output file
    for switch in response:
        hostname = dnac.devices.get_device_by_id(switch['deviceUuid']).response.hostname.strip(".necgroup.lan")
        with open('command_runner_output.txt', 'a') as file:
            file.write(hostname + "#")
        for command in command_list:
            with open('command_runner_output.txt', 'a') as file:
                if switch['commandResponses']['FAILURE'] != {}:
                    file.write(">" * 55 + "ERROR" + "<" * 55 + "\n\n")
                    file.write(switch['commandResponses']['FAILURE'][command])
                elif switch['commandResponses']['SUCCESS'] != {}:
                    file.write(switch['commandResponses']['SUCCESS'][command])
                else:
                    file.write(">" * 45 + "BLACKLISTED COMMAND" + "<" * 45 + "\n\n")
                    file.write(switch['commandResponses']['BLACKLISTED'][command])
        with open('command_runner_output.txt', 'a') as file:
            file.write("\n\n" + "=" * 100 + "\n\n")


def main():
    # Read the commands.txt file and add all found commands to a list object
    cmd_list = read_commands_file()

    # Get all devices according to below filters
    devices = dnac.devices.get_device_list(
        reachability_status='Reachable',
        family='Switches and Hubs',
        #series='Cisco Catalyst 9300 Series Switches',
        #id='0da7fb1e-b9c4-41ac-af1e-5628dc00dee5',
        #hostname='GBVOXERCC9301.necgroup.lan',
        #management_ip_address='',
        #serial_number='',
        #type='',
    )

    # Create an empty device list and zeroise the device counter
    device_list = []
    count = 0

    # Loop through each device adding its UUID to the device_list and incrementing the counter
    for device in devices.response:
        device_list.append(device.id)
        print(device.id, device.hostname)
        count += 1

    # Split the list of devices into a list of lists where each list is a maximum of 'list_length' (probably 100)
    list_length = 100
    list_of_device_lists_100_in_length = list(divide_list_into_chunks(device_list, list_length))

    # Print a message to user and ask for permission to continue
    print("=" * 100)
    user_response = input(f"The filter has resulted in {count} devices. Do you want to continue?: ")
    if 'y' not in user_response:
        exit(0)

    # Create an empty list of tasks IDs
    tasks = []

    # For each list of device lists, execute the commands on the list of devices and populate the tasks list
    # with the task ID(s)
    for list_of_uuids in list_of_device_lists_100_in_length:
        # Call the Command Runner API (asynchronous call) which will return a task ID
        # while the task completes in the background
        tasks.append(dnac.command_runner.run_read_only_commands_on_devices(
            commands=cmd_list,
            deviceUuids=list_of_uuids)['response']['taskId'])

    # Print a list of tasks
    for task in tasks:
        print(f'Task ID: {task}')

    # Print message to users
    print("Waiting for commands to be executed on all switches. This could take a few minutes....")

    # Create an empty list of file IDs
    list_of_file_ids = []

    # Populate the list of file IDs with each file ID that is generated from the command runner calls
    for task in tasks:
        list_of_file_ids.append(get_file_id_from_task(task))

    # Print out each file ID for reference (can use this to pull using Postman if required)
    for file in list_of_file_ids:
        print(f'File ID: {file}')

    ####################################################################################
    # I can't get the SDK to work properly when downloading files from DNAC.
    # So coding this part manually using the standard requests library.
    ####################################################################################

    # Write a new header to the output file (overwriting any previous file contents)
    with open('command_runner_output.txt', 'w') as file:
        file.write("-" * 50 + "\n")
        file.write(" " * 15 + "Command Output\n")
        file.write("-" * 50 + "\n\n")

    # Get the Authentication Token
    token = get_auth_token()

    # For each file ID, download the contents and populate the output file
    for file_id in list_of_file_ids:
        get_file_contents(cmd_list, file_id, token)

    print("Check file: command_runner_output.txt")


if __name__ == "__main__":
    main()
