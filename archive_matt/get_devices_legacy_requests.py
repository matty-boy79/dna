import urllib3
import requests
import variables
import json
from dnac_auth import get_auth_token
urllib3.disable_warnings()

SERVER = variables.DNAC_SERVER

##########################################
PATH = "/dna/intent/api/v1/network-device"
#PATH = "/dna/intent/api/v1/network-device/count"
##########################################


def get_devices(auth_token):
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
    devices = (response.json())

    for device in devices['response']:
        name = device['hostname'].strip('.necgroup.lan')
        ip = device['managementIpAddress']
        id = device['id']
        print('{0:20}{1:17}{2}'.format(name, ip, id))





if __name__ == "__main__":
    token = get_auth_token()
    get_devices(token)
