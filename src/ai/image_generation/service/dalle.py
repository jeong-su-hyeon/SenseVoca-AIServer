# [ image_generation/service/dalle.py ]
import os
import requests
from fastapi import HTTPException
import httpx
from openai import OpenAI
from datetime import datetime 
from datetime import datetime
from ai.image_generation.config.dalle import DALLE_API, DALLE_MODEL, DALLE_STYLE_PROMPT, DALLE_NEGATIVE_PROMPT, DALLE_IMAGE_SIZE, DALLE_IMAGE_DIRECTORY

# DALLE API key
no_proxy_client = httpx.Client(proxies=None)
client = OpenAI(api_key=DALLE_API, http_client=no_proxy_client)

# [0] 서비스 실행
def service_dalle(word: str, association_eng: str):
    try:
        print("[DEBUG] service_dalle 시작")
        print(f" - 프롬프트: {association_eng}")
        
        word = word
        association_eng = association_eng
        full_prompt = association_eng + DALLE_STYLE_PROMPT + DALLE_NEGATIVE_PROMPT

        # [1] 이미지 생성 (URL 형태로 반환)
        dalle_image_url = generate_image(full_prompt)

        # [-] 이미지를 로컬에 저장 저장 (나중에 삭제 🔴)
        dalle_local_path = save_image(word, dalle_image_url)

        return {
        "message": "DALLE 이미지 생성 및 저장 성공",
        "word": word,
        "association": association_eng,
        "dalle_local_path": dalle_local_path
        }
    
    except Exception as e:
        print(f"[ERROR] 예외 발생: {e}")
        raise HTTPException(
            status_code=500,
            detail = {
                "message": "DALLE 이미지 생성 및 저장 실패",
                "error": str(e),
                "word": word,
                "association": association_eng
            }
        )

# [1] DALLE 이미지 생성
def generate_image(full_prompt: str) -> str:
    # 1. 이미지 생성 
    response = client.images.generate(
            model = DALLE_MODEL,
            prompt = full_prompt,       # 프롬프팅 문장
            n = 1,                      # 생성할 사진 개수
            size = DALLE_IMAGE_SIZE,    # 생성할 사진 크기 
            response_format="url"
        )

    print(" - DALLE 이미지 생성 성공")   

    # 2. 생성된 이미지 url     
    dalle_temp_url = response.data[0].url # DALLE가 생성한 첫번째 이미지 선택
    return dalle_temp_url

# [-] 이미지를 로컬에 저장 (나중에 삭제 🔴)
def save_image(word: str, dalle_image_url: str) -> str:
    image_data = requests.get(dalle_image_url).content

    # 1. 저장 경로 지정
    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    dalle_local_path = os.path.join(DALLE_IMAGE_DIRECTORY, f"dalle_{word}_{timestamp}.png")
    os.makedirs(os.path.dirname(dalle_local_path), exist_ok = True) # 저장 디렉토리 생성

    # 2. 이미지 저장
    with open(dalle_local_path, "wb") as f:
        f.write(image_data) 

    print(" - DALLE 이미지 저장 성공")   

    return dalle_local_path