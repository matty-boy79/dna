'''
Returns an authorisation token, valid for 30 mins
Token must be used as an 'X-Auth-Token' HTTP Header for all API calls to Cisco DNA Center
'''
import urllib3
import requests
import variables
from requests.auth import HTTPBasicAuth
urllib3.disable_warnings()

SERVER = variables.DNAC_SERVER
USER = variables.DNAC_USER
PASSWORD = variables.DNAC_PASSWORD

######################################
PATH = "/dna/system/api/v1/auth/token"
######################################

def get_auth_token():
    url = SERVER + PATH
    hdr = {'content-type': 'application/json'}

    # response = requests.post(url, auth=HTTPBasicAuth(USER, PASSWORD), headers=hdr, verify=False).json()
    # token = (response['Token'])
    # return(token)

    return(requests.post(url, auth=HTTPBasicAuth(USER, PASSWORD), headers=hdr, verify=False).json()['Token'])


if __name__ == "__main__":
    print(get_auth_token())
