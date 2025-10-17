#######################################################################################
# Yourname: Kacha Thanaphitak
# Your student ID: 66070244
# Your GitHub Repo: https://github.com/Achakach/IPA2024-Final

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

import requests
import json
import time
import os
import netconf_final
from requests_toolbelt.multipart.encoder import MultipartEncoder
from dotenv import load_dotenv

load_dotenv()

MY_STUDENT_ID = "66070244"
WEBEX_ROOM_ID = "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vMTUyYmVkYTAtNmYwNy0xMWYwLWIwY2EtMmIwZWNiYzM3ODFj"
#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.

ACCESS_TOKEN = os.environ.get("WEBEX_ACCESS_TOKEN")
if not ACCESS_TOKEN:
    raise Exception("WEBEX_ACCESS_TOKEN not found. Make sure you have a .env file with the token.")
#######################################################################################
# 3. Prepare parameters get the latest message for messages API.


while True:
    time.sleep(1)
    getParameters = {"roomId": WEBEX_ROOM_ID, "max": 1}
    getHTTPHeader = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
# 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
    
    # Send a GET request to the Webex Teams messages API.
    # - Use the GetParameters to get only the latest message.
    # - Store the message in the "r" variable.

    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=getParameters,
        headers=getHTTPHeader,
    )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code == 200:
            print(f"Warning: Incorrect reply from Webex Teams API. Status code: {r.status_code}")
            continue

    # get the JSON formatted returned data
    json_data = r.json()
    if not json_data.get("items"):
            continue
    # check if there are any messages in the "items" array
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")

    # store the array of messages
    messages = json_data["items"]
    
    # store the text of the first message in the array
    message = messages[0]["text"]
    print("Received message: " + message)

    # check if the text of the message starts with the magic character "/" followed by your studentID and a space and followed by a command name
    #  e.g.  "/66070123 create"
    if message.startswith(f"/{MY_STUDENT_ID} "):

        # extract the command
        parts = message.split()
        command = parts[1] if len(parts) > 1 else None
        print(f"Executing command: {command}")

# 5. Complete the logic for each command

        if command == "create":
            responseMessage = netconf_final.create(MY_STUDENT_ID)    
        elif command == "delete":
            responseMessage = netconf_final.delete(MY_STUDENT_ID)
        elif command == "enable":
            responseMessage = netconf_final.enable(MY_STUDENT_ID)
        elif command == "disable":
            responseMessage = netconf_final.disable(MY_STUDENT_ID)
        elif command == "status":
            responseMessage = netconf_final.status(MY_STUDENT_ID)
        elif command == "gigabit_status":
            responseMessage = netconf_final.gigabit_status(MY_STUDENT_ID)
        elif command == "showrun":
            responseMessage = netconf_final.showrun(MY_STUDENT_ID)
        else:
            responseMessage = "Error: No command or unknown command"
        
# 6. Complete the code to post the message to the Webex Teams room.

        # The Webex Teams POST JSON data for command showrun
        # - "roomId" is is ID of the selected room
        # - "text": is always "show running config"
        # - "files": is a tuple of filename, fileobject, and filetype.

        # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
        
        # Prepare postData and HTTPHeaders for command showrun
        # Need to attach file if responseMessage is 'ok'; 
        # Read Send a Message with Attachments Local File Attachments
        # https://developer.webex.com/docs/basics for more detail

        if command == "showrun" and responseMessage == 'ok':
            filename = "66070244_show_running_config.txt"
            fileobject = open(filename, "rb")
            filetype = "text/plain"
            postData = {
                "roomId": WEBEX_ROOM_ID,
                "text": "show running config",
                "files": (filename, fileobject, filetype),
            }
            postData = MultipartEncoder(postData)
            HTTPHeaders = {
            "Authorization": ACCESS_TOKEN,
            "Content-Type": postData.content_type,
            }
        # other commands only send text, or no attached file.
        else:
            postData = {"roomId": WEBEX_ROOM_ID, "text": responseMessage}
            postData = json.dumps(postData)

            # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
            HTTPHeaders = {"Authorization": ACCESS_TOKEN, "Content-Type": "application/json"}

        # Post the call to the Webex Teams message API.
        r = requests.post(
            "https://webexapis.com/v1/messages",
            data=postData,
            headers=HTTPHeaders,
        )
        if not r.status_code == 200:
            raise Exception(
                "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
            )
