import time
import json
import urllib3
import requests
import variables
from dnacentersdk import api
from dnac_auth import get_auth_token

# Set Constant variables
SERVER = variables.DNAC_SERVER
USER = variables.DNAC_USER
PASSWORD = variables.DNAC_PASSWORD
VERSION = variables.DNAC_VERSION

# Disable warnings about untrusted certs
urllib3.disable_warnings()


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


    # Count the number of lines (commands) in the commands input file and print an error if empty
command_count = len(open('commands.txt').readlines())
if command_count == 0:
    print('commands.txt must contain at least one Cisco show command.')
    exit(1)

# Create an empty list
cmd_list = []

# Populate the list with commands from the input file
with open('commands.txt', 'r') as cmds_file:
    for line in cmds_file:
        cmd_list.append(line.strip())

# Create a DNACenterAPI Connection Object to be used for subsequent API calls
dnac = api.DNACenterAPI(username=USER, password=PASSWORD, base_url=SERVER, version=VERSION, verify=False)

# Get all devices according to below filters
devices = dnac.devices.get_device_list(
    #id='c7a37bf1-15d7-46c6-a0c0-59ff33f48d5b',
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

# Create an empty list and reset device counter
device_list = []
count = 0

# Loop through each device adding its UUID to the device_list and incrementing the counter
for device in devices.response:
    device_list.append(device.id)
    print(device.id, device.hostname)
    count += 1

list_of_device_lists_100_in_length = list(divide_chunks(device_list, 100))

print("=" * 100)
user_response = input(f"The filter has resulted in {count} devices. Do you want to continue?: ")
if 'y' not in user_response:
    exit(0)

tasks = []

for list in list_of_device_lists_100_in_length:
    # Call the Command Runner API (asynchronous call) which will return a task ID while the task completes in the background
    tasks.append(dnac.command_runner.run_read_only_commands_on_devices(commands=cmd_list, deviceUuids=list)['response']['taskId'])



############################
for task in tasks:
    print(task)

#exit()
############################



# Set the value of task_status to be "CLI Runner request creation" to force the while loop to iterate at least once
#task_status = "CLI Runner request creation"
print("Waiting for task to complete.", end="")



'''
# While the task status equals "CLI Runner request creation", check and evaluate the task status, then wait a while
while task_status == "CLI Runner request creation":
    task_status = dnac.task.get_task_by_id(tasks[0])['response']['progress']
    if task_status == "CLI Runner request creation":
        print(".", end="")
        time.sleep(1)
    else:
        print("")
        break
'''

# While the task status equals "CLI Runner request creation", check and evaluate the task status, then wait a while
while "endTime" not in task_status:
    task_status = dnac.task.get_task_by_id(tasks[0])['response']['progress']
    if task_status == "CLI Runner request creation":
        print(".", end="")
        time.sleep(1)
    else:
        print("")
        break


file_id = json.loads(task_status)['fileId']

####################################################################################
# I can't get the SDK to work properly when downloading files from DNAC.
# So coding this part manually using the standard requests library.
####################################################################################

# Get the Authentication Token
token = get_auth_token()

# Create the HTTP headers
hdr = {
        'content-type': 'application/json',
        'X-Auth-Token': token
    }

# Set the path and create the full URL for the GET
path = f'/dna/intent/api/v1/file/{file_id}'
url = SERVER + path

# GET the file and convert the contents to JSON
response = requests.get(url=url, headers=hdr, verify=False).json()

# Write a new header to the output file (overwrite previous file contents)
with open('command_runner_output.txt', 'w') as file:
    file.write("-" * 50 + "\n")
    file.write(" " * 15 + "Command Output\n")
    file.write("-" * 50 + "\n\n")

# Loop through the response object printing each command from each device to the output file
for switch in response:
    for command in cmd_list:
        with open('command_runner_output.txt', 'a') as file:
            file.write(switch['commandResponses']['SUCCESS'][command])
    with open('command_runner_output.txt', 'a') as file:
        file.write("\n\n" + "=" * 150 + "\n\n")

print("Check file: command_runner_output.txt")
