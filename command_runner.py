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


def get_auth_token():
    path = "/dna/system/api/v1/auth/token"
    url = SERVER + path
    hdr = {'content-type': 'application/json'}

    response = requests.post(url, auth=HTTPBasicAuth(USER, PASSWORD), headers=hdr, verify=False).json()
    token = (response['Token'])
    return(token)


def divide_list_into_chunks(l, n):
    # Function to split a list of entries into multiple lists with max length = 'n'
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_file_id_from_task(task_id):
    task_status = dnac.task.get_task_by_id(task_id)
    while "endTime" not in task_status['response']:
        time.sleep(5)
        print("Still Waiting...")
        task_status = dnac.task.get_task_by_id(task_id)
    return json.loads(task_status.response.progress)['fileId']


def get_file_contents(file_to_download):
    # Create the HTTP headers
    hdr = {
        'content-type': 'application/json',
        'X-Auth-Token': token
    }

    # Set the path and create the full URL for the GET
    path = f'/dna/intent/api/v1/file/{file_to_download}'
    url = SERVER + path

    # GET the file and convert the contents to JSON
    response = requests.get(url=url, headers=hdr, verify=False).json()

    # Loop through the response object printing each command from each device to the output file
    for switch in response:
        for command in cmd_list:
            with open('command_runner_output.txt', 'a') as file:
                if switch['commandResponses']['FAILURE'] != {}:
                    file.write(">" * 55 + "ERROR" + "<" * 55 + "\n\n")
                    file.write(switch['commandResponses']['FAILURE'][command])
                elif switch['commandResponses']['SUCCESS'] != {}:
                    file.write(switch['commandResponses']['SUCCESS'][command])
                else:
                    file.write(">" * 50 + "BLACKLISTED COMMAND" + "<" * 50 + "\n\n")
                    file.write(switch['commandResponses']['BLACKLISTED'][command])
        with open('command_runner_output.txt', 'a') as file:
            file.write("\n\n" + "=" * 100 + "\n\n")


if __name__ == "__main__":
    # Count the number of lines (commands) in the commands input file and print an error if empty
    command_count = len(open('commands.txt').readlines())
    if command_count == 0:
        print('commands.txt must contain at least one Cisco show command.')
        exit(1)

    # Create an empty list of commands
    cmd_list = []

    # Populate the list with commands from the input file
    with open('commands.txt', 'r') as cmds_file:
        for line in cmds_file:
            cmd_list.append(line.strip())

    # Create a DNACenterAPI Connection Object to be used for subsequent API calls
    dnac = api.DNACenterAPI(username=USER, password=PASSWORD, base_url=SERVER, version=VERSION, verify=False)

    # Get all devices according to below filters
    devices = dnac.devices.get_device_list(
        #id='18800ffa-cad6-45c0-865a-605043fab146,b9dab50b-9410-4cc6-9a7d-4ae5fc02b509,2e1942a4-d509-446b-9bdf-ccba61be9502,e55fed2d-2aa3-4c2c-aaaa-d18038d1878c,d1a9a24a-7a25-4eaf-bf90-18ee1b268411,d8189a4c-0596-4105-abd1-93f4a3ba50f8,07e7777b-b99e-4100-8dab-aafafbf2d142,3eb690b8-2ef7-4ba1-973e-4785959bb1e3,de9010ad-a223-4cae-ab55-82c3e40afcd8,6c4534d9-460b-4bee-b4e8-2a926fb7eee9,6b4f17af-586c-4076-a9ec-0f183c97a5cd,248f6002-2def-466e-acb9-5c00572ab279,9cb442cd-a680-4dcb-9e2d-3f1ef6f0d846,0ff393fa-f2a1-48c4-bf17-9507cfc1b66a,23d43e24-7a16-4ccc-a5f1-ec76565decbd,aefd0c14-c12d-4763-ae69-119a48b0dda9,f56473dd-4cf0-435e-9c9d-25c6cadcb834,60b761a3-982b-437d-a3ee-6f1fe5106d79,e6102c24-1738-4302-ae8c-da80e0100ae6,d303ef6e-bbe0-443c-b3ae-9eb38e489229',
        #hostname='GBVOXERCC9301.necgroup.lan',
        reachability_status='Reachable',
        family='Switches and Hubs',
        #management_ip_address='',
        #location_name='',
        #serial_number='',
        #location='',
        #type='',
        #series='',
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
    for list in list_of_device_lists_100_in_length:
        # Call the Command Runner API (asynchronous call) which will return a task ID while the task completes in the background
        tasks.append(dnac.command_runner.run_read_only_commands_on_devices(commands=cmd_list, deviceUuids=list)['response']['taskId'])

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

    # Get the Authentication Token
    token = get_auth_token()

    # Write a new header to the output file (overwriting any previous file contents)
    with open('command_runner_output.txt', 'w') as file:
        file.write("-" * 50 + "\n")
        file.write(" " * 15 + "Command Output\n")
        file.write("-" * 50 + "\n\n")

    # For each file ID, download the contents and populate the output file
    for file_id in list_of_file_ids:
        get_file_contents(file_id)

    print("Check file: command_runner_output.txt")
