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
task_status = "CLI Runner request creation"
print("Waiting for task to complete.", end="")


task_status = dnac.task.get_task_by_id(tasks[0])
while "endTime" not in task_status['response']:
    print(".")
    time.sleep(3)
    task_status = dnac.task.get_task_by_id(tasks[0])

file_id = json.loads(task_status.response.progress)['fileId']



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
