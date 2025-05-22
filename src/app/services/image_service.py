import io
import requests
from openai import OpenAI
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime 
from src.app.core.cloud import drive_service
from src.app.core.config import settings

client = OpenAI(api_key=settings.dalle_api_key)

def generate_image_from_prompt(word: str, image_prompt: str):        
    # [0] 이미지 프롬프트 설정 
    STYLE_PROMPT = """, children’s book style, children's book illustration, flat colors, thin line art, minimal details, 
                        cute cartoon style, soft lighting, clear lines, friendly expression, clear color"""
    NEGATIVE_PROMPT = """, no grayscale, no monochrome, no detailed muscles, no abs, no violent themes, 
                        no weapons, no realistic anatomy, no intense shadows, no text, no watermarks, no nudity, no creepy or unsettling faces, 
                        avoid excessive details, no photo style, no shirtless, no nudity, not creepy face, no grey scale, 
                        Don't create color charts, other charts that aren't related to sentences """
    full_prompt = image_prompt + STYLE_PROMPT + NEGATIVE_PROMPT

    # [1] 이미지 생성 (임시 URL로 반환)
    dalle_image_url = generate_image(full_prompt)

    # byte로 이미지 다운로드
    response = requests.get(dalle_image_url)
    image_data = response.content
        
    # [2] 클라우드에 업로드 (구글 드라이브)
    cloud_image_url = upload_to_drive(word, image_data)  

    return cloud_image_url
        
# [1] DALLE 이미지 생성
def generate_image(full_prompt: str) -> str:        
    # 1) 이미지 생성 
    response = client.images.generate(
        model = "dall-e-3",
        prompt = full_prompt,       # 프롬프팅 문장
        n = 1,                      # 생성할 사진 개수
        size = "1024x1024",         # 생성할 사진 크기 
        response_format="url",
        quality='hd',
        style='vivid'
    )      

    # 2) 생성된 이미지 임시 URL     
    dalle_temp_url = response.data[0].url # DALLE가 생성한 첫번째 이미지 선택
    return dalle_temp_url

# [2] 클라우드에 업로드 (구글 드라이브)
def upload_to_drive(word: str, image_data: bytes, folder_id: str = "13giaHuBBXbtValbua2RZ0wYBq_TdmVZA") -> str:
    file_name = f"{word}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

    file_metadata = {
        'name': file_name,
        'parents': [folder_id]  # 내 드라이브 폴더 ID
    }

    media = MediaIoBaseUpload(io.BytesIO(image_data), mimetype='image/png')

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    file_id = file.get('id')        

    # 공개 권한 부여
    drive_service.permissions().create(
        fileId=file_id,
        body={
        'type': 'anyone',
        'role': 'reader'
        }
    ).execute()

    return file_id
    