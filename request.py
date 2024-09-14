import requests
import os
import time
import json
from colorama import Fore, Style
import uuid
import threading
import random
import datetime

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
        "User-Agent": "DuolingoMobile/16.4.3",
        "Accept": "application/json",
        "X-Amzn-Trace-Id": "User=0",
        "Content-Type": "application/json",
        "Content-Length": "113",
        "Accept-Encoding": "gzip, deflate, br"
    }
    login_requests_body = {"identifier": my_mail_id, "password": my_mail_pass}
    login_request_json = json.dumps(login_requests_body)
    login_response = requests.post(url_login,
                                   data=login_request_json,
                                   headers=headers)
    if login_response.status_code == 200:
        print("login success")
        response_data = login_response.json()
        user_id = response_data['id']
        auth = login_response.headers.get('jwt')
        master_header = {
            "Authorization": f"Bearer {auth}",
            "User-Agent": "Duodroid/5.128.3",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip, deflate",
        }
        return user_id, master_header
    else:
        print("failed", login_response.status_code, login_response.text)


def gifts(error_event, user_id, master_header):
    get_friends_url = "https://android-api-cf.duolingo.com/2017-06-30/friends/users/1435537403/followers?pageSize=500"
    get_friends_response = requests.get(get_friends_url, headers=master_header)
    if get_friends_response.status_code == 200:
        data = get_friends_response.json()
        if "users" in data["followers"]:
            friends_userIds = [
                user["userId"] for user in data["followers"]["users"]
            ]
            gift_list = ["xp_boost_15_gift", "streak_freeze_gift"]
            for _ in range(4):
                for gift_user_id in friends_userIds:
                    for gift in gift_list:
                        gift_url = "https://android-api-cf.duolingo.com/2017-06-30/batch?fields=responses%7Bbody%2Cstatus%2Cheaders%7D"
                        gift_payload = {
                            "requests": [{
                                "body":
                                f'{{"id":"{gift}","isFree": true,"via":"drawer"}}',
                                "bodyContentType": "application/json",
                                "method": "POST",
                                "url": rf"/2017-06-30/users/{user_id}/gifts/{gift_user_id}?fields=id%2CpurchaseDate%2CpurchasePrice%2Cquantity%2CsubscriptionInfo%7Bcurrency%2CexpectedExpiration%2CisFreeTrialPeriod%2CperiodLength%2Cprice%2CproductId%2Crenewer%2Crenewing%2CvendorPurchaseId%7D%2CwagerDay%2CexpectedExpirationDate%2CpurchaseId%2CpurchasedByUserId%2CremainingEffectDurationInSeconds%2CexpirationEpochTime%2CfamilyPlanInfo%7BownerId%2CsecondaryMembers%2CinviteToken%2CpendingInvites%7BfromUserId%2CtoUserId%2Cstatus%2CsubscriptionItemType%7D%7D",
                            }],
                            "includeHeaders":
                            False
                        }
                        
                        gift_response = requests.post(url=gift_url,
                                                      headers=master_header,
                                                      json=gift_payload)
                        if gift_response.status_code == 200:
                            print(
                                f"Successfully gifted {Fore.YELLOW}{gift}{Style.RESET_ALL} for {Fore.CYAN}{gift_user_id}{Style.RESET_ALL}"
                            )   
                            # print(gift_response.text)
                        else:
                            print(
                                f"Request error for Gifitng: {gift_response.status_code}"
                            )
                            kill_thread(error_event)
        else:
            print("Unexpected JSON structure.")
            return []


def sub_request(error_event, user_id, master_header):
    while True:
        prem_url = f"https://android-api-cf.duolingo.com/2017-06-30/users/{user_id}/shop-items"
        request_data_prem_json = {
            "itemName": "immersive_subscription",
            "productId": "com.duolingo.immersive_free_trial_subscription"
        }
        request_data_json_updated = json.dumps(request_data_prem_json)
        response = requests.post(prem_url,
                                 data=request_data_json_updated,
                                 headers=master_header)
        if (response.status_code == 200):
            print(
                f"Successfully bought {Fore.YELLOW}Super{Style.RESET_ALL} for {Fore.CYAN}{user_id}{Style.RESET_ALL}"
            )
            time.sleep(300)
        else:
            print(f"Request error for Subscription: {response.status_code}")
            error_event.set()
            kill_thread(error_event)


def quests(error_event, user_id, master_header):
    for year in range(2007, 2024 + 1):
        for month in range(1, 13):
            day = random.randint(1, 28)
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            microsecond = random.randint(0, 999999)
            timestamp = datetime.datetime(year, month, day, hour, minute,
                                          second, microsecond)
            timestamp = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

            quests_url = f"https://goals-api.duolingo.com/users/{user_id}/progress/batch"
            quests_data = {
                "metric_updates": [{
                    "metric": "QUESTS",
                    "quantity": 999
                }],
                "timestamp": f"{timestamp}",
                "timezone": "Asia/Kolkata",
            }
            quests_response = requests.post(url=quests_url,
                                            json=quests_data,
                                            headers=master_header)
            if quests_response.status_code == 200:
                print(
                    f"Successfully completed{Fore.YELLOW} Quests {Style.RESET_ALL} for {Fore.CYAN}{timestamp}{Style.RESET_ALL}"
                )
            else:
                print(
                    f"Quests credit failed with code: {quests_response.status_code}"
                )
                kill_thread(error_event)


def perk_request(error_event, user_id, master_header):
    while True:
        item_id = [
            "general_xp_boost", "streak_freeze", "society_streak_freeze",
            "duo_streak_freeze", "xp_boost_stackable",
        ]
        perk_url = "https://android-api-cf.duolingo.com/2017-06-30/batch?fields=responses%7Bbody%2Cstatus%2Cheaders%7D"
        for id in item_id:
            perk_data = {
                "requests": [{
                    "body":
                    rf'{{"id": "{id}", "isFree": true, "purchasePrice":0,"currencyType":"XGM", "consumed": true}}',
                    "bodyContentType":
                    "application.json",
                    "method":
                    "POST",
                    "url":
                    rf"/2017-06-30/users/{user_id}/shop-items?fields=id%2CpurchaseDate%2CpurchasePrice%2Cquantity%2CsubscriptionInfo%7Bcurrency%2CexpectedExpiration%2CisFreeTrialPeriod%2CperiodLength%2Cprice%2CproductId%2Crenewer%2Crenewing%2CvendorPurchaseId%7D%2CwagerDay%2CexpectedExpirationDate%2CpurchaseId%2CremainingEffectDurationInSeconds%2CexpirationEpochTime%2CfamilyPlanInfo%7BownerId%2CsecondaryMembers%2CinviteToken%2CpendingInvites%7BfromUserId%2CtoUserId%2Cstatus%7D%7D",
                }],
                "includeHeaders":
                False
            }
            perk_request_json = json.dumps(perk_data)
            perk_response = requests.post(perk_url,
                                          data=perk_request_json,
                                          headers=master_header)
            if perk_response.status_code == 200:
                print(
                    f"Successfully bought {Fore.YELLOW}{id}{Style.RESET_ALL} for {Fore.CYAN}{user_id}{Style.RESET_ALL}"
                )
            else:
                print("Items purchase failed with code:",
                      perk_response.status_code)
                error_event.set()
                kill_thread(error_event)
                time.sleep(1)


def gem_buy(error_event, user_id, master_header):
    while True:
        generated_uuid = uuid.uuid4()
        formatted_uuid = str(generated_uuid).replace('-', '_')
        gem_url = f'https://android-api-cf.duolingo.com/2017-06-30/users/{user_id}/rewards/INCENTIVIZED_CONTACT_SYNC_GEMS-{formatted_uuid}-CURRENCY_BUNDLE-GEMS'
        gem_data = {"consumed": True}
        gem_response = requests.patch(gem_url,
                                      json=gem_data,
                                      headers=master_header)
        if gem_response.status_code == 200:
            print(
                f"Successfully credited {Fore.YELLOW} gem {Style.RESET_ALL} for {Fore.CYAN}{user_id}{Style.RESET_ALL}"
            )
        else:
            print("Gem credit failed with code:", gem_response.status_code)
            error_event.set()
            kill_thread(error_event)


def main():
    error_event = threading.Event()
    user_id, master_header = login()
    subsciption_thread = threading.Thread(target=sub_request,
                                          args=(
                                              error_event,
                                              user_id,
                                              master_header,
                                          ))
    perk_thread = threading.Thread(target=perk_request,
                                   args=(
                                       error_event,
                                       user_id,
                                       master_header,
                                   ))
    gem_thread = threading.Thread(target=gem_buy,
                                  args=(
                                      error_event,
                                      user_id,
                                      master_header,
                                  ))

    quests_thread = threading.Thread(target=quests,
                                     args=(
                                         error_event,
                                         user_id,
                                         master_header,
                                     ))
    gift_thread = threading.Thread(target=gifts,
                                   args=(
                                       error_event,
                                       user_id,
                                       master_header,
                                   ))
    quest_input = input("Do you want to unlock quests badge(Y/n): ")
    if quest_input in ("Y", "y"):
        quests_thread.start()
    gift_input = input("Do you want to send XP_Boost gifts to others(Y/n): ")
    if gift_input in ("Y", "y"):
        gift_thread.start()
    subsciption_thread.start()
    perk_thread.start()
    gem_thread.start()
