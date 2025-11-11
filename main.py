import httpx
import os
import time
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://graph.microsoft.com/v1.0"
# example data
folders = [
    {
        "name": "john doe",
        "folder": "123456",
        "truck": [1],
        "bol_folder": "7890",
    }
]

headers = {"Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}"}


def get_messages(folder_id):
    url = f"{BASE_URL}/me/mailFolders/{folder_id}/messages?$filter=hasAttachments eq true and receivedDateTime lt 2024-06-06T00:00:00Z&$select=id,subject,hasAttachments,receivedDateTime,webLink,from&$top=100"
    while url:
        resp = httpx.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        for msg in data.get("value", []):
            yield msg
        url = data.get("@odata.nextLink")  # pagination


def get_attachments(message_id):
    url = f"{BASE_URL}/me/messages/{message_id}/attachments"
    resp = httpx.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get("value", [])


def download_attachment(attachment, save_dir, message_id):
    url = f"{BASE_URL}/me/messages/{message_id}/attachments/{attachment['id']}/$value"
    resp = httpx.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.content

    if not data:
        return
    file_path = os.path.join(save_dir, f"{message_id[0:20]}_{attachment['name']}")
    with open(file_path, "wb") as f:
        f.write(data)


allowed_types = [
    "application/pdf",
    "application/octet-streamimage/png",
    "application/octet-streamimage/jpg",
    "application/octet-stream",
    "image/jpeg",
    "image/png",
    "image/heic",
    "image/heif",
    "binary/octet-stream",
]


def main():
    for folder in folders:
        save_dir = f"./attachments/truck {folder['truck'][0]} {folder['name']}"
        os.makedirs(save_dir, exist_ok=True)

        for msg in get_messages(folder["bol_folder"]):
            email_domain = (
                msg["from"]["emailAddress"]["address"].strip().lower().split("@")[1]
                if "@" in msg["from"]["emailAddress"]["address"]
                else ""
            )
            if email_domain == "relaypayments.com":
                continue

            attachments = get_attachments(msg["id"])
            for att in attachments:
                print(
                    f"{folder['name']} attachment downloaded for {msg['subject']} {msg['webLink']}"
                )

                if att["isInline"] is True:
                    continue

                if (
                    att["@odata.type"] == "#microsoft.graph.fileAttachment"
                    and att["contentType"] in allowed_types
                ):
                    time.sleep(0.05)
                    download_attachment(att, save_dir, msg["id"])
                else:
                    # for future improvement/debugging
                    print(att["contentType"])

        print(f"{folder['name']} DONE")


if __name__ == "__main__":
    main()
