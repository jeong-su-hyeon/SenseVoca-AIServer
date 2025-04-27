# [ txt2img/service.py ]
from openai import OpenAI
import os
import requests
from datetime import datetime 
from datetime import datetime
from ai.image_generation.txt2img.dto import ImageGenerationRequest
from ai.image_generation.txt2img.config_dalle import DALLE_API, DALLE_MODEL, DALLE_STYLE_PROMPT, DALLE_NEGATIVE_PROMPT, DALLE_IMAGE_SIZE, DALLE_IMAGE_DIRECTORY

# DALLE API key
client = OpenAI(api_key = DALLE_API)

# [0] 서비스 실행
def service_dalle(request: ImageGenerationRequest):
    try:
        print("[DEBUG] service_dalle 시작")
        print(f" - 프롬프트: {request.image_prompt}")
        
        image_word = request.image_word
        image_prompt = request.image_prompt
        full_prompt = image_prompt + DALLE_STYLE_PROMPT + DALLE_NEGATIVE_PROMPT

        # [1] 이미지 생성
        temp_url = generate_image(full_prompt)

        # [2] 이미지 저장
        image_url = save_image(image_word, temp_url)

        return {
        "message": "DALLE 이미지 생성 성공",
        "image_word": image_word,
        "image_prompt": image_prompt,
        "image_url": image_url
        }
    
    except Exception as e:
        print(f"[ERROR] 예외 발생: {e}")
        return {
            "message": "DALLE 이미지 생성 실패",
            "error": str(e),
            "image_word": request.image_word,
            "image_prompt": request.image_prompt
        }

# [1] 이미지 생성
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
    temp_url = response.data[0].url # DALLE가 생성한 첫번째 이미지 선택
    return temp_url

# [2] 이미지 저장
def save_image(image_word: str, temp_url: str) -> str:
    image_data = requests.get(temp_url).content

    # 1. 저장 경로 지정
    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    image_url = os.path.join(DALLE_IMAGE_DIRECTORY, f"dalle_{image_word}_{timestamp}.png")
    os.makedirs(os.path.dirname(image_url), exist_ok = True) # 저장 디렉토리 생성

    # 2. 이미지 저장
    with open(image_url, "wb") as f:
        f.write(image_data) 

    print(" - DALLE 이미지 저장 성공")   

    return image_url