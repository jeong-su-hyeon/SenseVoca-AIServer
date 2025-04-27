# [ img2img/service.py ]
import base64
from datetime import datetime
import os
import requests
from sqlalchemy.orm import Session
from ai.image_generation.img2img.config import SD_API, SD_STYLE_PROMPT, SD_CONTROLNET, SD_PAYLOAD_BASE, SD_IMAGE_DIRECTORY
from ai.image_generation.img2img.repository import repository_image_generation
    
# [0] 서비스 실행
def service_sd(image_word: str, image_prompt: str, dalle_image_url: str, db: Session):
    try:
        print("[DEBUG] service_sd 실행")

        # [1] 이미지 설정
        payload = setup_image(image_prompt, dalle_image_url) # dict

        # [2] SD WebUI API 요청 <-> 응답(이미지 생성 결과)
        final_image = request_api(f"{SD_API}/sdapi/v1/img2img", payload) # bytes
       
        # [3] 이미지 저장
        final_path = save_image(image_word, final_image) # str

        # [4] DB에 저장
        saved_image = repository_image_generation(image_word, image_prompt, final_path, db) # Object
        print(" - DB 저장 성공")
        
        return {
            "message": "SD 이미지 저장 성공",
            "image_id": saved_image.image_id,
            "image_word": saved_image.image_word,
            "image_prompt": saved_image.image_prompt,
            "image_url": saved_image.image_url,
        }

    except Exception as e:
        print(f"[ERROR] 예외 발생 : {e}")
        return {
            "message": "SD 이미지 저장 실패",
            "error": str(e),
            "image_word": image_word,
            "image_prompt": image_prompt,
        }

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
        json_response.raise_for_status                       # 요청 실패 시 예외 발생

        # print(" - SD 응답 원문:", response.text) 
        if "images" in json_response:
            json_response["images"][0] = "<이미지 base64 생략>"
            print(" - 응답 내용:", json_response)

        # 2. 응답 처리
        image_b64 = json_response.json()["images"][0] 
        final_image = base64.b64decode(image_b64) # base64 -> 바이트 디코딩

        print(" - SD WebUI 요청 성공")
        return final_image
    
    except requests.RequestException as e:
        print(f"[ERROR] SD WebUI 요청 실패 : {e}")
        raise

# [3] 이미지 저장
def save_image(image_word: str, final_image: bytes) -> str:
    # 1. 저장 경로 지정
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_path = os.path.join(SD_IMAGE_DIRECTORY, f"sd_{image_word}_{timestamp}.png")
    os.makedirs(os.path.dirname(final_path), exist_ok=True) # 저장 디렉토리 생성

    # 2. 이미지 저장
    with open(final_path, "wb") as f: 
        f.write(final_image)
        
    print(" - SD 이미지 저장 성공")
    return final_path

