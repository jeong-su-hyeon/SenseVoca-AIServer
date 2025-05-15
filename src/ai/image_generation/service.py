# [ image_generation/service.py ]
import os
import io
import httpx
import requests
from fastapi import HTTPException
from openai import OpenAI
from googleapiclient.http import MediaIoBaseUpload
from sqlalchemy.orm import Session
from datetime import datetime 
from ai.image_generation.config_image.cloud import drive_service
from ai.image_generation.config_image.dalle import API_KEY, DALLE_MODEL, STYLE_PROMPT, NEGATIVE_PROMPT, IMAGE_SIZE, LOCAL_IMAGE_DIRECTORY
from ai.image_generation.repository import repository_image_generation

client = OpenAI(api_key=API_KEY)

# [0] 서비스 실행
def service_image_generation(basic_word_id: int, word: str, association: str, association_eng: str, example_eng: str, db: Session):
    try:
        print("[DEBUG] 이미지 생성 SERVICE 시작")
        print(f" - 0) 프롬프트: {association_eng}")
        
        full_prompt = association_eng + STYLE_PROMPT + NEGATIVE_PROMPT
        fallback_prompt = example_eng + STYLE_PROMPT + NEGATIVE_PROMPT

        # [1] 이미지 생성 (URL 형태로 반환)
        dalle_image_url = generate_or_fallback(full_prompt, fallback_prompt)
        print(" - 1) 이미지 URL 생성 성공") 

        # byte로 이미지 다운로드
        response = requests.get(dalle_image_url)
        image_data = response.content
        
        # [2] 클라우드에 업로드 (구글 드라이브)
        cloud_image_url = upload_to_drive(basic_word_id, word, image_data)  
        print(f" - 2) 구글 드라이브에 업로드 성공 : 파일 ID={cloud_image_url}")

        # [-] 이미지를 로컬에 저장 저장 (나중에 삭제 🔴)
        # dalle_local_path = save_image(word, dalle_image_url)
        # print(" - debug) 이미지 로컬에 저장 성공")
        
        # [3] DB에 저장
        saved_image = repository_image_generation(basic_word_id, cloud_image_url, db)  # DB에 이미지 정보 저장
        print(" - 3) DB UPDATE 성공\n")
                
        return {
        "message": "[SERVICE] 이미지 생성 및 업로드 성공",
        "basic_word_id": basic_word_id,
        "word": word,
        "association": association,        
        "image_url": saved_image.image_url
        #"dalle_local_path": dalle_local_path, (나중에 삭제 🔴)
        }
    
    except Exception as e:
        print(f"[ERROR] 예외 발생: {e}")
        raise HTTPException(
            status_code=500,
            detail = {
                "message": "[SERVICE] 이미지 생성 및 업로드 실패",
                "error": str(e),
                "basic_word_id": basic_word_id,
                "word": word,
                "association": association
            }
        )

# [fallback 처리]
def generate_or_fallback(full_prompt: str, fallback_prompt: str)-> str:
    try:
        return generate_image(full_prompt)
    except HTTPException as e:
        if "content_policy_violation" in str(e.detail) or "blocked" in str(e.detail) or "invalid_request_error" in str(e.detail):
            print("[WARNING] 검열된 프롬프트 감지.. fallback_propmt로 재시도")
            return generate_image(fallback_prompt)
        else:
            raise e
        
# [1] DALLE 이미지 생성
def generate_image(prompt: str) -> str:    
    try:
        # 1. 이미지 생성 
        response = client.images.generate(
                model = DALLE_MODEL,
                prompt = prompt,       # 프롬프팅 문장
                n = 1,                      # 생성할 사진 개수
                size = IMAGE_SIZE,    # 생성할 사진 크기 
                response_format="url",
                quality='hd',
                style='vivid'
            )      

        # 2. 생성된 이미지 url     
        dalle_temp_url = response.data[0].url # DALLE가 생성한 첫번째 이미지 선택
        return dalle_temp_url
    
    except Exception as e:
        print(f"[ERROR] DALL·E 이미지 생성 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error code: 400 - {str(e)}"
        )

# [2] 클라우드에 업로드 (구글 드라이브)
def upload_to_drive(basic_word_id: int, word: str,image_data: bytes, folder_id: str = "13giaHuBBXbtValbua2RZ0wYBq_TdmVZA") -> str:
    try:
        file_name = f"{basic_word_id}_{word}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

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
        # print(f" - 공개 권한 부여 완료: 파일 ID = {file_id}")

        return file_id

    except Exception as e:
        print(f"[ERROR] 구글 드라이브 업로드 실패: {e}")
        raise HTTPException(status_code=500, detail=f"Google Drive upload failed: {e}")
    
# [-] 이미지를 로컬에 저장 (나중에 삭제 🔴)
def save_image(word: str, dalle_image_url: str) -> str:
    image_data = requests.get(dalle_image_url).content

    # 1. 저장 경로 지정
    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    dalle_local_path = os.path.join(LOCAL_IMAGE_DIRECTORY, f"dalle_{word}_{timestamp}.png")
    os.makedirs(os.path.dirname(dalle_local_path), exist_ok = True) # 저장 디렉토리 생성

    # 2. 이미지 저장
    with open(dalle_local_path, "wb") as f:
        f.write(image_data)     

    return dalle_local_path
    