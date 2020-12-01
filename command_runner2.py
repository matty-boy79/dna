import time
import json
import urllib3
import variables
from dnacentersdk import api

# Set Constant variables
SERVER = variables.DNAC_SERVER
USER = variables.DNAC_USER
PASSWORD = variables.DNAC_PASSWORD
VERSION = variables.DNAC_VERSION

# Disable warnings about untrusted certs
urllib3.disable_warnings()

# Create a DNACenterAPI Connection Object to be used for subsequent API calls
dnac = api.DNACenterAPI(username=USER, password=PASSWORD, base_url=SERVER, version=VERSION, verify=False)

# Create a list of commands to run, starting with "show run | inc hostname" <-- MANDATORY
show_cmd = ["show run | inc hostname"] # DO NOT CHANGE THIS LINE

# Add custom command to run here:
show_cmd.append("show ip int b | inc Vlan")

# Create a list of all devices to run the commands(s) on, by UUID
devices = [
    "0da7fb1e-b9c4-41ac-af1e-5628dc00dee5",
    # Add more device UUIDs above this line in quotes with a comma at the end
    # TODO: Take the output from device.get_device_list() and use this as the list of UUIDs
]

# Call the Command Runner API (asynchronous call) which will return a task ID while the task completes in teh background
task_id = dnac.command_runner.run_read_only_commands_on_devices(commands=show_cmd, deviceUuids=devices)['response']['taskId']

# Set the value of task_status to be "CLI Runner request creation" to force the loop to iterate at least once
task_status = "CLI Runner request creation"
print("Waiting for task to complete.", end="")

# While the task status equals "CLI Runner request creation", check and evaluate the status, then wait a while
while task_status == "CLI Runner request creation":
    task_status = dnac.task.get_task_by_id(task_id)['response']['progress']
    if task_status == "CLI Runner request creation":
        print(".", end="")
        time.sleep(0.1)
    else:
        print("")
        my_file_id = json.loads(task_status)['fileId']
        break

# # Write a new header to the output file (overwrite whatever was there before)
# with open('command_output.txt', 'w') as file:
#     file.write("Command Output\n")
#     file.write("--------------\n")

# Download the file from DNAC and store it in a dict object
file_str = dnac.file.download_a_file_by_fileid(file_id=my_file_id).data.decode()
file_json_all = json.loads(file_str)
file_json = file_json_all[0]['commandResponses']['SUCCESS'][show_cmd[1]]
print(file_json)

# file_contents_json = json.loads(file_contents)
# #file_contents_clean = file_contents_json[0]['commandResponses']['SUCCESS'][show_cmd[1]]
# file_contents_clean = file_contents_json[0]['commandResponses']['SUCCESS']
# file_contents_str = json.dumps(file_contents_clean)
# matt = file_contents_str.replace('\\n', '\n').replace('\\', '')
# mattLine = matt.splitlines()
#
# # Remove the first line of garbage
# del mattLine[0]
#
# # Remove the last line of garbage
# del mattLine[len(mattLine)-1]
#
# # Print all remaining lines
# for line in mattLine:
#     print(line)
#
#
# Download the file from DNAC and format the contents appropriately
# file_contents = str(dnac.file.download_a_file_by_fileid(file_id=my_file_id).data).replace('\\n', '\n').replace('\\', '')
# print(file_contents)
# print("*" * 100)
# matt = file_contents.split('\n')[1:]
# print(matt)

# with open('command_output.txt', 'a') as file:
#     file.write(file_contents)
#     file.write("\n\n################################################################################\n\n")
