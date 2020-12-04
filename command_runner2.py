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

command_count = len(open('commands.txt').readlines())

if command_count == 0:
    print('commands.txt must contain at least one Cisco show command.')
    exit(0)

cmd_list = []

with open('commands.txt', 'r') as cmds_file:
    for line in cmds_file:
        cmd_list.append(line.strip())

# Create a DNACenterAPI Connection Object to be used for subsequent API calls
dnac = api.DNACenterAPI(username=USER, password=PASSWORD, base_url=SERVER, version=VERSION, verify=False)

# Add custom command to run here:
#show_cmd.extend(["show ip int b | inc Vlan", "show run int lo0"])

# Create a list of all devices to run the commands(s) on, by UUID
device_list = [
    "0da7fb1e-b9c4-41ac-af1e-5628dc00dee5",
    "66be433c-1c08-4f30-a023-82a84d460520"
    # Add more device UUIDs above this line in quotes with a comma at the end
    # TODO: Take the output from device.get_device_list() and use this as the list of UUIDs
]

# Call the Command Runner API (asynchronous call) which will return a task ID while the task completes in the background
task_id = dnac.command_runner.run_read_only_commands_on_devices(commands=cmd_list, deviceUuids=device_list)['response']['taskId']

# Set the value of task_status to be "CLI Runner request creation" to force the below while loop to iterate at least once
task_status = "CLI Runner request creation"
print("Waiting for task to complete.", end="")

# While the task status equals "CLI Runner request creation", check and evaluate the task status, then wait a while
while task_status == "CLI Runner request creation":
    task_status = dnac.task.get_task_by_id(task_id)['response']['progress']
    if task_status == "CLI Runner request creation":
        print(".", end="")
        time.sleep(0.1)
    else:
        print("")
        break

my_file_id = json.loads(task_status)['fileId']

#######################################################################################################################

token = get_auth_token()

hdr = {
        'content-type': 'application/json',
        'X-Auth-Token': token
    }

path = f'/dna/intent/api/v1/file/{my_file_id}'
url = SERVER + path

response = requests.get(url=url, headers=hdr, verify=False).json()
for switch in response:
    for command in cmd_list:
        print(switch['commandResponses']['SUCCESS'][command])
    print("=" * 100)


# Write a new header to the output file (overwrite previous file contents)
# with open('command_output.txt', 'w') as file:
#     file.write("Command Output\n")
#     file.write("--------------\n")


#
# # with open('command_output.txt', 'a') as file:
# #     file.write(file_contents)
#     file.write("\n\n################################################################################\n\n")
