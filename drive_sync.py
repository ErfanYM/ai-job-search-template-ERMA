"""Upload a PDF to the tracker's Google Drive folder, return a shareable link."""
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CONFIG_DIR = Path.home() / ".config" / "resume-bot"
CREDENTIALS_FILE = CONFIG_DIR / "gdrive_credentials.json"
TOKEN_FILE = CONFIG_DIR / "gdrive_token.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def get_drive_service():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return build("drive", "v3", credentials=creds)


def upload_pdf(local_path: str, folder_id: str) -> str:
    service = get_drive_service()
    filename = os.path.basename(local_path)
    file_metadata = {"name": filename, "parents": [folder_id]}
    media = MediaFileUpload(local_path, mimetype="application/pdf")
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    file_id = file["id"]
    service.permissions().create(
        fileId=file_id, body={"type": "anyone", "role": "reader"}
    ).execute()
    return f"https://drive.google.com/open?id={file_id}"


if __name__ == "__main__":
    import sys

    local_pdf = sys.argv[1] if len(sys.argv) > 1 else "resume.pdf"
    # Optional 2nd arg: destination folder id (overrides GDRIVE_FOLDER_ID).
    # Resume folder:       <RESUME_FOLDER_ID> (see SETUP.md)
    # Cover-letter folder:  <COVER_LETTER_FOLDER_ID> (see SETUP.md)
    folder = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("GDRIVE_FOLDER_ID")
    if not folder:
        raise SystemExit("no folder: pass a folder id as arg 2 or set GDRIVE_FOLDER_ID")
    link = upload_pdf(local_pdf, folder)
    print(link)
