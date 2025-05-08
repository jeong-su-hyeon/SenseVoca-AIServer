# [ image_generation/service/sd.py ]
import base64
from datetime import datetime
import os
import requests
from googleapiclient.http import MediaIoBaseUpload
import io
from sqlalchemy.orm import Session
from fastapi import HTTPException
from ai.image_generation.config.sd import SD_API, SD_STYLE_PROMPT, SD_CONTROLNET, SD_PAYLOAD_BASE, SD_IMAGE_DIRECTORY
from ai.image_generation.repository import repository_image_generation
from ai.image_generation.config.cloud import drive_service


# [0] 서비스 실행
def service_sd(word: str, association: str, dalle_local_url: str, db: Session):
    try:
        print("[DEBUG] service_sd 실행")

        # [1] 이미지 설정
        payload = setup_image(association, dalle_local_url) # dict

        # [2] SD WebUI API 요청 <-> 응답(이미지 생성 결과)
        sd_image_result = request_api(f"{SD_API}/sdapi/v1/img2img", payload) # bytes
       
        # [-] 이미지를 로컬에 저장
        save_image(word, sd_image_result) # str

        # [3] 클라우드에 업로드 (구글 드라이브)
        cloud_image_url = upload_to_drive(sd_image_result, word)  # 클라우드로 바로 업로드

        # [4] DB에 저장
        saved_image = repository_image_generation(word, association, cloud_image_url, db)  # DB에 이미지 정보 저장
        print(" - DB 저장 성공")
        
        return {
            "message": "SD 이미지 저장 성공",
            "id": saved_image.id,
            "word": saved_image.word,
            "association": saved_image.association,
            "image_url": saved_image.image_url,
        }

    except Exception as e:
        print(f"[ERROR] 예외 발생 : {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "SD 이미지 저장 실패",
                "error": str(e),
                "word": word,
                "association": association
            }
        )

# [1] 이미지 설정
def setup_image(image_prompt: str, dalle_image_url: str) -> dict:
    # 1. 원본 이미지 열기
    with open(dalle_image_url, "rb") as image_file:
        image_bytes = image_file.read() # 이미지 파일 byte로 변환
        image_base64 = base64.b64encode(image_bytes).decode("utf-8") # byte -> base64 인코딩 -> utf-8 문자열로 변환 

    # 2. 이미지 기본 설정
    payload = {
        ** SD_PAYLOAD_BASE,
        "prompt": image_prompt + SD_STYLE_PROMPT,
        "init_images": [f"data:image/png;base64, {image_base64}"],

        "alwayson_scripts": {
            "ControlNet": {
                "args": [ { ** SD_CONTROLNET, "input_image": f"data:image/png;base64, {image_base64}" } ]
            }
        }
    }

    return payload

# [2] SD WebUI API 요청
def request_api(url: str, payload: dict) -> bytes:
    try:
        # 1. 요청
        json_response = requests.post(url, json=payload)     # SD WebUI의 /img2img API 호출 json
        json_response.raise_for_status()                       # 요청 실패 시 예외 발생

        # print(" - SD 응답 원문:", response.text) 
        if "images" in json_response:
            json_response["images"][0] = "<이미지 base64 생략>"
            print(" - 응답 내용:", json_response)

        # 2. 응답 처리
        image_b64 = json_response.json()["images"][0] 
        sd_image_result = base64.b64decode(image_b64) # base64 -> 바이트 디코딩

        print(" - SD WebUI 요청 성공")
        return sd_image_result
    
    except requests.RequestException as e:
        print(f"[ERROR] SD WebUI 요청 실패 : {e}")        
        raise HTTPException(status_code=500)

# [3] 클라우드에 업로드 (구글 드라이브)
def upload_to_drive(image_data: bytes, image_word: str, folder_id: str = "13giaHuBBXbtValbua2RZ0wYBq_TdmVZA") -> str:
    try:
        file_name = f"sd_{image_word}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

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
        print(f" - 구글 드라이브에 파일 업로드 완료: 파일 ID = {file_id}")

        # 공개 권한 부여
        drive_service.permissions().create(
            fileId=file_id,
            body={
                'type': 'anyone',
                'role': 'reader'
            }
        ).execute()
        print(f" - 공개 권한 부여 완료: 파일 ID = {file_id}")

        return file_id

    except Exception as e:
        print(f"[ERROR] 구글 드라이브 업로드 실패: {e}")
        raise HTTPException(status_code=500, detail=f"Google Drive upload failed: {e}")

# [-] 이미지를 로컬에 저장
def save_image(word: str, sd_image_result: bytes) -> str:
    # 1. 저장 경로 지정
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sd_local_path = os.path.join(SD_IMAGE_DIRECTORY, f"sd_{word}_{timestamp}.png")
    os.makedirs(os.path.dirname(sd_local_path), exist_ok=True) # 저장 디렉토리 생성

    # 2. 이미지 저장
    with open(sd_local_path, "wb") as f: 
        f.write(sd_image_result)
        
    print(" - SD 이미지 저장 성공")
    return sd_local_path

