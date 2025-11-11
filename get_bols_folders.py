# HOW THIS WORKS
# 1. Run get_parent_folders
# 2. Read the output of it and add it to the folders list. It's a manual process because you only want folders for certain guys. Also, the other properties like truck and name have to be set manually
# 3. Run get_bol_folders for each folder you identified in step 2.

import httpx
from dotenv import load_dotenv
import os

load_dotenv()
BASE_URL = "https://graph.microsoft.com/v1.0"
headers = {"Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}"}
inbox = "your inbox id"


def get_parent_folders():
    url = f"{BASE_URL}/me/mailFolders/{inbox}/childFolders?$top=100&$orderBy=displayName asc"
    while url:
        resp = httpx.get(url, headers=headers)
        resp.raise_for_status()
        json = resp.json()
        for folder in json["value"]:
            print(folder["displayName"] + " " + folder["id"])
        url = json["@odata.nextLink"]


def get_bol_folders(folder_id):
    url = f"{BASE_URL}/me/mailFolders/{folder_id}/childFolders"
    resp = httpx.get(url, headers=headers)
    resp.raise_for_status()
    json = resp.json()
    for folder in json["value"]:
        if "bol" in folder["displayName"].lower().strip():
            print(folder["displayName"])
            return folder["id"]
    raise KeyError("No bol folder found")


get_parent_folders()

folders = [
    {
        "name": "john doe",
        "folder": "123456",
        "truck": [1],
        "bolFolder": "",
    },
]
for folder in folders:
    folder["bolFolder"] = get_bol_folders(folder["folder"])

print(folders)
