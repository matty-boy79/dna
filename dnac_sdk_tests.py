import variables
import urllib3
from dnacentersdk import api

urllib3.disable_warnings()

SERVER = variables.DNAC_SERVER
USER = variables.DNAC_USER
PASSWORD = variables.DNAC_PASSWORD
VERSION = variables.DNAC_VERSION

dnac = api.DNACenterAPI(username=USER, password=PASSWORD, base_url=SERVER, version=VERSION, verify=False)

devices = dnac.devices.get_device_list(
   reachability_status='Reachable',
   family='Unified AP'
)

count = 0
for device in devices.response:
    print(device.id + "  " + device.hostname)
    count += 1

print(f'Count: {count}')
