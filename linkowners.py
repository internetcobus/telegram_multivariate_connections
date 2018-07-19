import json
import requests
import urllib
import time


TOKEN = "576806246:AAHSkZPQ-rrNDWMVmwvbrCfOzNMM-oqHDeQ"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

from linkowners_dbhelper import DBHelper

db = DBHelper()

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_json_from_text(text):
    js = json.loads(text)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def view_open_requests(owner):
    codesList = db.get_owner_requests(owner)
    if len(codesList) > 0:
        send_message("Your available request codes are:", owner)
        for x in codesList:
            send_message(x, owner)    
    else:
        send_message("You have no available request codes. Try /getcode", owner)

def get_instructions():
    message = "Please note: before you can create your connections you should have receieved a code from one of our existing users.\n\n"
    message += "Send /getcode to generate a unique code to link.\n"
    message += "Send /view to see your connections.\n"
    message += "Send /requests to see your available request codes.\n"
    message += "Or simply send your code to confirm your link."
    return message

def handle_updates(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        owner = update["message"]["chat"]["id"]
        first_name = update["message"]["chat"]["first_name"]
        last_name = ""
        full_name = ""
        #Last name is optional so user username instead
        if "last_name" in update["message"]["chat"]:
            last_name = update["message"]["chat"]["last_name"]
        if last_name == "":
            full_name = first_name
        else:
            full_name = first_name + " " + last_name

        #check if text has a ":\n". Usually when someone copy and paste code. 
        while text.find(':\n')!=-1:
            text = text.split(":\n",1)[1]

        if text == "/start":
            message = "Welcome to Multivariate Connections.\n\n"
            message += get_instructions()
            send_message(message, owner)
        elif text == "/help":
            message = get_instructions()
            send_message(message, owner)            
        elif text == "/getcode":
            result = db.add_linkUsers(owner, full_name)
            if result != 'success':
                send_message(result, owner)
            else:
                view_open_requests(owner)
        elif text == "/requests":
            view_open_requests(owner)
        elif text == "/view":
            result =  get_json_from_text(db.get_owner_connections(owner))
            if len(result) > 0:
                message = "Your connections are:"
                for connection in result:
                    message += ("\n" + connection["LinkOwnerName"] + " (" + connection["LinkConfirmedDate"] + ")")
                send_message(message, owner)
            else:
                send_message("You have no connections. Try /getcode and send your code to a colleague to confirm.", owner)
        elif len(text) == 8:
            result = db.confirm_code(text, owner, full_name)
            if result == "Error0":
                send_message("Code not recognised.", owner)
            elif result == "Error1":
               send_message("You cannot use your own code. Send it to a potential connections so that they can send it.", owner)
            else:
                send_message("Connection confirmed with " + result[1], owner)
                send_message(full_name + " is now connected to you.", result[0])
        else:
            send_message("Code not recognised.", owner)

            
def main():
    #test = db.get_all_data()
    #print(test)

    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
