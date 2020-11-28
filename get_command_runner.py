import urllib3
import requests
import variables
import json
from dnac_auth import get_auth_token
import time
urllib3.disable_warnings()

SERVER = variables.DNAC_SERVER

##########################################
PATH = "/dna/intent/api/v1/network-device-poller/cli/read-request"
##########################################

# TODO: Refactor Code in general terms to clean it up
# TODO: Do a get devices for all reachable swithes and run command(s) on those

def get_command_runner(auth_token):
    url = SERVER + PATH
    hdr = {
        'content-type': 'application/json',
        'X-Auth-Token': auth_token
    }

    post_dict = {
        "commands": [
            "show run | incl hostname",
            "show template"
        ],
        "deviceUuids": [
            "9836efe3-616c-48b9-814c-afc81457e419",
            "748ddbe9-dd83-4147-9472-29e19e735216",
            "2e9b31f8-ece9-45af-99b6-e11229a787eb"
        ],
        "name": "THIS IS THE NAME",
        "timeout": 0
    }

    post_json = json.dumps(post_dict)

    response = requests.post(url=url, headers=hdr, verify=False, data=post_json)
    task_id = response.json()['response']['taskId']
    print(f'Task ID: {task_id}')

    path = f'/dna/intent/api/v1/task/{task_id}'
    url = SERVER + path

    a = 0
    while a < 10:
        a += 1
        response = requests.get(url, headers=hdr, verify=False)
        progress = response.json()['response']['progress']
        print(f'Progress Report #{a}: {progress}')
        if progress == "CLI Runner request creation":
            time.sleep(1)
        else:
            file_id = json.loads(progress)['fileId']
            print(f'File ID: {file_id}')
            break

    path = f'/dna/intent/api/v1/file/{file_id}'
    url = SERVER + path
    response = requests.get(url=url, headers=hdr, verify=False)

    with open('command_output.txt', 'w') as file:
        file.write("Command Output\n")
        file.write("--------------\n")

    for device in response.json():
        output = str(device['commandResponses']['SUCCESS']).replace('\\n', '\n')
        print(output)
        print('\n###############################################################################\n')

        with open('command_output.txt', 'a') as file:
            file.write(output)
            file.write("\n\n################################################################################\n\n")

if __name__ == "__main__":
    token = get_auth_token()
    get_command_runner(token)
