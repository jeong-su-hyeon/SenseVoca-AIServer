# [image_generation/config/cloud.py]
import os
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/drive.file']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 경로
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'sensevoca-d80e99dbaf02.json')

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)
