import urllib3
import requests
import variables
import json
from dnac_auth import get_auth_token
urllib3.disable_warnings()

SERVER = variables.DNAC_SERVER

##########################################
PATH = "/dna/intent/api/v1/network-device/count"
##########################################


def get_device_count(auth_token):
    url = SERVER + PATH
    hdr = {
        'content-type': 'application/json',
        'X-Auth-Token': auth_token
    }

    query_string_params = {
        #'platformId': 'C9300-48P',
        'reachabilityStatus': 'reachable',
        'family': 'Switch.*'
    }

    response = requests.get(url, headers=hdr, verify=False, params=query_string_params)
    count = (response.json())

    print(f'Devices: {count["response"]}')

if __name__ == "__main__":
    token = get_auth_token()
    get_device_count(token)
