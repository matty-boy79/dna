import urllib3
import requests
import variables
#from dnac_auth import get_auth_token
urllib3.disable_warnings()

SERVER = variables.DNAC_SERVER

######################################
PATH = "/dna/intent/api/v1/site-health"
######################################


def get_site_health(auth_token):
    url = SERVER + PATH
    hdr = {
        'content-type': 'application/json',
        'X-Auth-Token': auth_token
    }

    response = requests.get(url, headers=hdr, verify=False)
    health = (response.json())

    print('{0:20}{1}'.format('Site', 'Health'))
    print('{0:20}{1}'.format('====', '======'))

    for site in health['response']:
        if "All Buildings" not in site['siteName'] and "All Sites" not in site['siteName']:
            print('{0:20}{1}'.format(site['siteName'], site['healthyNetworkDevicePercentage']))


if __name__ == "__main__":
    token = get_auth_token()
    get_site_health(token)
