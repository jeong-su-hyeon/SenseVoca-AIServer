import os
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# 현재 파일 경로 기준에서 api 폴더로 이동
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))  
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'src', 'app', 'core', 'sensevoca-d80e99dbaf02.json')

print("[DEBUG] SERVICE_ACCOUNT_FILE:", SERVICE_ACCOUNT_FILE)
print("[DEBUG] File Exists?", os.path.exists(SERVICE_ACCOUNT_FILE))

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)