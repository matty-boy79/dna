from requests.auth import HTTPBasicAuth
from colorama import Fore
from colorama import Style
import requests
import urllib3
import json

urllib3.disable_warnings()

SERVER = "https://100.64.0.101"
USER = "admin"
PASSWORD = "Cisco123"


def main():
    print(Fore.YELLOW + "~" * 50)
    print(Fore.RED + "|" + " " * 48 + "|")
    print("|" + Fore.CYAN + "      MATT'S AWESOME DNAC API CALLER THINGY     " + Fore.RED + "|")
    print(Fore.RED + "|" + " " * 48 + "|")
    print(Fore.YELLOW + "~" * 50)
    print(Style.RESET_ALL)

    token = get_auth_token()

    while True:
        print("#" * 56)
        print("1 - Get List of Health Scores for each site")
        print("2 - Get List of Devices")
        print("3 - Get Details of one Device by ID in JSON format")
        print("4 - Get Details of one Device by hostname in JSON format")
        print("9 - EXIT")
        print("#" * 56)

        choice = input("\nWhat do you want to do? ")

        if choice == "1":
            get_site_health(token)
        elif choice == "2":
            get_devices(token)
        elif choice == "3":
            get_device_details_by_id(token)
        elif choice == "4":
            get_device_details_by_name(token)
        else:
            exit()


def get_auth_token():
    path = "/dna/system/api/v1/auth/token"
    url = SERVER + path
    hdr = {'content-type': 'application/json'}
    response = requests.post(url, auth=HTTPBasicAuth(USER, PASSWORD), headers=hdr, verify=False)
    auth_token = (response.json()['Token'])
    return auth_token


def pprint(json_to_print):
    nicely_formatted_json_data = json.dumps(json_to_print, indent=4)
    print(nicely_formatted_json_data)


def get_site_health(auth_token):
    hdr = {
        'content-type': 'application/json',
        'X-Auth-Token': auth_token
    }

    path = "/dna/intent/api/v1/site-health"
    url = SERVER + path
    response = requests.get(url, headers=hdr, verify=False)
    health = (response.json())

    print('')
    print('{0:20}{1}'.format('Site', 'Health'))
    print('{0:20}{1}'.format('====', '======'))

    for site in health['response']:
        if "All Buildings" not in site['siteName'] and "All Sites" not in site['siteName']:
            print('{0:20}{1}'.format(site['siteName'], site['healthyNetworkDevicePercentage']))

    path = "/dna/intent/api/v1/network-health"
    url = SERVER + path
    response = requests.get(url, headers=hdr, verify=False)
    overall_health = (response.json())

    overall_health_score = overall_health['response'][0]['healthScore']
    health_score_str = str(overall_health_score)
    print("\nOverall Health Score: " + Fore.RED + health_score_str + Style.RESET_ALL + " out of 100")


def get_devices(auth_token, get_all_devices=True):
    path = "/dna/intent/api/v1/network-device"
    url = SERVER + path
    hdr = {
        'content-type': 'application/json',
        'X-Auth-Token': auth_token
    }

    response = requests.get(url, headers=hdr, verify=False)
    devices = (response.json())

    if get_all_devices:
        print('')
        print('{0:20}{1:20}{2}'.format('Hostname', 'IP', 'ID'))
        print('{0:20}{1:20}{2}'.format('========', '========', '========'))
        for device in devices['response']:
            name = device['hostname'].strip('.necgroup.lan')
            ip = device['managementIpAddress']
            uuid = device['id']
            print('{0:20}{1:20}{2}'.format(name, ip, uuid))

    else:
        return devices


def get_device_details_by_id(auth_token):
    uuid = input("Enter the ID: ")
    path = "/dna/intent/api/v1/network-device/{}".format(uuid)
    url = SERVER + path
    hdr = {
        'content-type': 'application/json',
        'X-Auth-Token': auth_token
    }

    response = requests.get(url, headers=hdr, verify=False)
    device_details = (response.json()['response'])
    pprint(device_details)


def get_device_details_by_name(auth_token):
    device_name = input("Enter the name: ").strip('.necgroup.lan')
    device_name = device_name.upper()
    devices = get_devices(auth_token, False)

    device_found = False

    print(device_name)

    for device in devices['response']:
        name = device['hostname'].strip('.necgroup.lan')
        if name == device_name:
            pprint(device)
            device_found = True

    if not device_found:
        print("Device not found")


if __name__ == "__main__":
    main()
