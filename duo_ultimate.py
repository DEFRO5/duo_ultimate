import requests
import os
import time
import json
from colorama import Fore, Style
import uuid
import threading

my_mail_id = os.environ['mail_id']
my_mail_pass = os.environ['mail_pass']

def kill_thread(error_event):
    if error_event.is_set():
        print("Error detected. Restarting login")
        error_event.clear()
        login()

def login():
        url_login = "https://android-api-cf.duolingo.com/2017-06-30/login?fields=id"
        headers = {
            "User-Agent": "Duodroid/5.141.7 Dalvik/2.1.0 (Linux; U; Android 9; SM-G973N Build/PQ3A.190705.06121522)",
            "Accept": "application/json",
            "X-Amzn-Trace-Id": "User=0",
            "Content-Type": "application/json",
            "Content-Length": "113",
            "Accept-Encoding": "gzip, deflate, br"
        }
        login_requests_body = {
            "identifier": my_mail_id,
            "password": my_mail_pass
        }
        login_request_json = json.dumps(login_requests_body)
        login_response = requests.post(url_login, data=login_request_json, headers=headers)
        if login_response.status_code == 200:
            print("login success")
            response_data = login_response.json()
            user_id = response_data['id']
            auth = login_response.headers.get('jwt')
            return user_id, auth
        else:
            print("failed", login_response.status_code, login_response.text)



def sub_request(error_event, user_id, auth):
    while True:
        prem_url = f"https://www.duolingo.com/2017-06-30/users/{user_id}/shop-items"
        headers = {
            "Authorization": f"Bearer {auth}",
            "User-Agent":  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Accept-Language": "en-US,en;q=0.7",
            "Origin": "https://www.duolingo.com",
            "Referer": "https://www.duolingo.com/lesson"
        }
        request_data_prem_json = {
            "itemName": "immersive_subscription",
            "productId": "com.duolingo.immersive_free_trial_subscription"
        }
        request_data_json_updated = json.dumps(request_data_prem_json)
        response = requests.post(prem_url,data=request_data_json_updated, headers=headers)
        if (response.status_code == 200):
            print(f"Successfully bought {Fore.YELLOW}Super{Style.RESET_ALL} for {Fore.CYAN}{user_id}{Style.RESET_ALL}")
            delay_seconds = 72 * 60 * 60
            correct_time = delay_seconds + 300
            time.sleep(correct_time)
        else:
            print(f"Request error: {response.status_code}")
            error_event.set()
            kill_thread(error_event)


def perk_request(error_event, user_id, auth):
    item_id = ["general_xp_boost", "streak_freeze", "society_streak_freeze"]
    perk_url = "https://android-api-cf.duolingo.com/2017-06-30/batch?fields=responses%7Bbody%2Cstatus%2Cheaders%7D"
    perk_headers = {
        "Cookie": "wuuid=b91f4ddf-d4f4-4ef8-b47c-04f5531e85db",
        "Authorization": f"Bearer {auth}",
        "User-Agent": "Duodroid/5.128.3 Dalvik/2.1.0 (Linux; U; Android 13; RMX3360 Build/TQ3C.230901.001.B1)",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate",
    }
    for id in item_id:
        perk_data = {
            "requests": [{
                "body": rf'{{"id": "{id}", "isFree": true, "purchasePrice":0,"currencyType":"XGM", "consumed": true}}',
                "bodyContentType": "application.json",
                "method": "POST",
                "url": rf"/2017-06-30/users/{user_id}/shop-items?fields=id%2CpurchaseDate%2CpurchasePrice%2Cquantity%2CsubscriptionInfo%7Bcurrency%2CexpectedExpiration%2CisFreeTrialPeriod%2CperiodLength%2Cprice%2CproductId%2Crenewer%2Crenewing%2CvendorPurchaseId%7D%2CwagerDay%2CexpectedExpirationDate%2CpurchaseId%2CremainingEffectDurationInSeconds%2CexpirationEpochTime%2CfamilyPlanInfo%7BownerId%2CsecondaryMembers%2CinviteToken%2CpendingInvites%7BfromUserId%2CtoUserId%2Cstatus%7D%7D",
            }],
            "includeHeaders": False
        }
        perk_request_json = json.dumps(perk_data)
        perk_response = requests.post(perk_url, data=perk_request_json, headers=perk_headers)
        if perk_response.status_code == 200:
            print(f"Successfully bought {Fore.YELLOW}{id}{Style.RESET_ALL} for {Fore.CYAN}{user_id}{Style.RESET_ALL}")
        else:
            print("Failed with code:", perk_response.status_code)
            error_event.set()
            kill_thread(error_event)
    time.sleep(60)

def gem_buy(error_event, user_id, auth):
    generated_uuid = uuid.uuid4()
    formatted_uuid = str(generated_uuid).replace('-', '_')
    gem_url = f'https://android-api-cf.duolingo.com/2017-06-30/users/{user_id}/rewards/SHOP_REWARDED_VIDEO-{formatted_uuid}-CURRENCY_BUNDLE-GEMS'
    gem_headers = {
        "Cookie": "wuuid=b91f4ddf-d4f4-4ef8-b47c-04f5531e85db",
        "Authorization": f"Bearer {auth}",
        "User-Agent": "Duodroid/5.128.3 Dalvik/2.1.0 (Linux; U; Android 13; RMX3360 Build/TQ3C.230901.001.B1)",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate",
    }
    gem_data = {"consumed": True}
    gem_data_json = json.dumps(gem_data)
    while True:
     gem_response = requests.patch(gem_url, data=gem_data_json, headers=gem_headers)
     if gem_response.status_code == 200:
        print( f"Successfully credited {Fore.YELLOW} gem {Style.RESET_ALL} for {Fore.CYAN}{user_id}{Style.RESET_ALL}")
     else:
        print("Failed with code", gem_response.status_code)
        error_event.set()
        kill_thread(error_event)


if __name__ == "__main__":
    error_event = threading.Event()
    user_id, auth = login()
    subsciption_thread = threading.Thread(target=sub_request,args=(error_event, user_id, auth, ))
    perk_thread = threading.Thread(target=perk_request,args=(error_event, user_id, auth, ))
    gem_thread = threading.Thread(target=gem_buy,args=(error_event, user_id, auth, ))
    subsciption_thread.start()
    perk_thread.start()
    gem_thread.start()
