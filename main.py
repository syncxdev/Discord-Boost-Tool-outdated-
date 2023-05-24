import requests
import time
import fade
import json
from colorama import Fore, Style, init

LICENSE_KEY = "1234"
CAPMONSTER_API_KEY = "your_capmonster_api_key"

def check_license():
    entered_license = input("Enter your license key: ")
    if entered_license != LICENSE_KEY:
        print("Invalid license key. Exiting...")
        exit()

def load_tokens():
    with open("tokens.txt", "r") as file:
        return [line.strip() for line in file.readlines()]

def save_tokens(tokens):
    with open("tokens.txt", "w") as file:
        file.write("\n".join(tokens))

def remove_duplicates(file):
    with open(file, "r") as file:
        lines_seen = set()
        unique_lines = []
        for line in file:
            if line not in lines_seen:
                unique_lines.append(line)
                lines_seen.add(line)
    with open(file, "w") as file:
        file.writelines(unique_lines)

def join_server(invite, token, headers):
    join_payload = {
        "captcha_key": "",
        "gift_code_sku_id": None
    }
    join_url = f"https://discord.com/api/v9/invites/{invite}"
    response = requests.post(join_url, headers=headers, json=join_payload)
    return response

def boost_server(invite, token, headers):
    boost_url = f"https://discord.com/api/v9/guilds/premium/subscription-slots"
    response = requests.get(boost_url, headers=headers)
    if response.status_code == 200:
        slots = response.json()
        if len(slots) > 0:
            for slot in slots:
                slot_id = slot["id"]
                payload = {"user_premium_guild_subscription_slot_ids": [slot_id]}
                boost_response = requests.put(f"https://discord.com/api/v9/guilds/{slot_id}/premium/subscriptions", headers=headers, json=payload)
                if boost_response.status_code == 201:
                    print(f"Boosted server with token: {token}")
                    return True
                else:
                    print(f"Failed to boost server with token: {token}")
        else:
            print("No available subscription slots.")
    else:
        print("Failed to fetch subscription slots.")

    return False

def boost(invite, tokens):
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-GB",
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/channels/@me",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.1.9 Chrome/83.0.4103.122 Electron/9.4.4 Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-context-properties": "eyJsb2NhdGlvbiI6IlVzZXIgUHJvZmlsZSJ9",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjAuMS45Iiwib3NfdmVyc2lvbiI6IjEwLjAuMTc3NjMiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6OTM1NTQsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9",
        "te": "trailers",
        "cookie": "__dcfduid=23a63d20476c11ec9811c1e6024b99d9; __sdcfduid=23a63d21476c11ec9811c1e6024b99d9e7175a1ac31a8c5e4152455c5056eff033528243e185c5a85202515edb6d57b0; locale=en-GB"
    }
    for token in tokens:
        token = token.strip()
        headers["authorization"] = token

        join_response = join_server(invite, token, headers)
        if join_response.status_code == 200:
            if "captcha_sitekey" in join_response.text:
                captcha_sitekey = join_response.json()["captcha_sitekey"]
                task_payload = {
                    "clientKey": CAPMONSTER_API_KEY,
                    "task": {
                        "type": "HCaptchaTaskProxyless",
                        "websiteURL": "https://discord.com/channels/@me",
                        "websiteKey": captcha_sitekey
                    }
                }
                create_task_url = "https://api.capmonster.cloud/createTask"
                create_task_response = requests.post(create_task_url, json=task_payload)
                if create_task_response.status_code == 200:
                    task_id = create_task_response.json()["taskId"]
                    get_results_payload = {
                        "clientKey": CAPMONSTER_API_KEY,
                        "taskId": task_id
                    }
                    get_results_url = "https://api.capmonster.cloud/getTaskResult"
                    status = "processing"
                    while status == "processing":
                        time.sleep(1)
                        get_results_response = requests.post(get_results_url, json=get_results_payload)
                        if get_results_response.status_code == 200:
                            results = get_results_response.json()
                            status = results["status"]
                            if status == "ready":
                                solution = results["solution"]["gRecaptchaResponse"]
                                headers["captcha_key"] = solution
                                join_response = join_server(invite, token, headers)
                                if join_response.status_code == 200:
                                    print(f"Joined server with token: {token}")
                                    boost_result = boost_server(invite, token, headers)
                                    if boost_result:
                                        remove_duplicates("tokens.txt")
                                        tokens.remove(token)
                                        save_tokens(tokens)
                                        return
                                break
                        else:
                            print("Failed to get task results.")
                            break
                else:
                    print("Failed to create task.")
            else:
                print(f"Joined server with token: {token}")
                boost_result = boost_server(invite, token, headers)
                if boost_result:
                    remove_duplicates("tokens.txt")
                    tokens.remove(token)
                    save_tokens(tokens)
                    return
        else:
            print(f"{Fore.RED}Failed to join server with token: {token}{Style.RESET_ALL}")

def print_banner(BoostsAmmount: int, license_status: str):
    banner1 = f'''{Fore.LIGHTBLUE_EX}
     ▄▀▀▀▀▄  ▄▀▀▄ ▀▀▄  ▄▀▀▄ ▀▄  ▄▀▄▄▄▄   ▄▀▀▄  ▄▀▄ 
    █ █   ▐ █   ▀▄ ▄▀ █  █ █ █ █ █    ▌ █    █   █ 
       ▀▄   ▐     █   ▐  █  ▀█ ▐ █      ▐     ▀▄▀  
    ▀▄   █        █     █   █    █           ▄▀ █  
     █▀▀▀       ▄▀    ▄▀   █    ▄▀▄▄▄▄▀     █  ▄▀  
     ▐          █     █    ▐   █     ▐    ▄▀  ▄▀   
                ▐     ▐        ▐         █    ▐    
                            
            
            Made by ! [Leͥgeͣnͫd] Mii🌟
            Discord: https://discord.gg/Nyq3fNtQWT

                    Boosts Available: {BoostsAmmount}
                    LICENSE_KEY: {license_status}
    '''



    print(banner1)


def main():
    init(autoreset=True)
    check_license()
    print_banner(5, "active")  # Replace '5' with the actual number of available boosts
    tokens = load_tokens()
    invite = input("Enter the server invite: ")
    boost(invite, tokens)


if __name__ == "__main__":
    main()
