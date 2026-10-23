from __future__ import print_function
import os, json, pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]


def main():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Assumes credentials.json is in the same directory
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("drive", "v3", credentials=creds)
    results = (
        service.files()
        .list(pageSize=1000, fields="files(id, name, mimeType)")
        .execute()
    )
    items = results.get("files", [])

    manifest = {"evidenceNodes": []}
    for item in items:
        manifest["evidenceNodes"].append(
            {"name": item["name"], "id": item["id"], "mimeType": item["mimeType"]}
        )

    with open("cloud_id_manifest_full.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("Successfully generated cloud_id_manifest_full.json")


if __name__ == "__main__":
    main()
