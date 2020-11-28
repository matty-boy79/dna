from dnac_auth import get_auth_token
from get_site_health import get_site_health
from get_devices import get_devices

token = get_auth_token()

while True:
    print("\n###############################################")
    print("1 - Get List of Health Scores for each site")
    print("2 - Get List of Devices")
    print("3 - Command Runner")
    print("9 - EXIT")
    print("###############################################")

    choice = input("\nWhat do you want to do? ")

    if choice == "1":
        get_site_health(token)
    elif choice == "2":
        get_devices(token)
    elif choice == "3":
        get_command_runner(token)
    else:
        exit()
