# [ txt2img/router.py ]
import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config import SessionLocal
from ai.image_generation.txt2img.dto import ImageGenerationRequest
from ai.image_generation.txt2img.service import service_dalle
from ai.image_generation.img2img.service import service_sd
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/image-generation")
def router_image_generation(request: ImageGenerationRequest, db: Session = Depends(get_db)):
    print("[DEBUG] router_image_generation 실행")
    
    # [1] DALLE - 1차 이미지 생성
    dalle_result = service_dalle(request)          # 이미지 결과 
    image_word = dalle_result["image_word"]        # 단어
    image_prompt = dalle_result["image_prompt"]    # 프롬프트 문장
    dalle_image_url = dalle_result["image_url"]    # 1차 이미지 경로

    # [2] SD - 2차 이미지 생성 (최종)
    sd_result = service_sd(image_word, image_prompt, dalle_image_url, db) # 이미지 결과 (1차 경로 전달 -> 결과 생성)

    return {
        "dalle": dalle_result,
        "sd": sd_result
    }

@router.post("/image-generation/sd-test")
def router_test(db: Session = Depends(get_db)):
    print("[DEBUG] router_test 실행")

    file_path = "C:\\Users\\user\\Desktop\\2025-1\\Capstone\\Fast API\\image-generation-test\\ai\\image_generation\\saved_images\\dalle"
    file_name = "dalle_naughty_250424_155841.png"
    dalle_image_url = os.path.join(file_path, file_name)

    sd_result = service_sd("word", "prompt", dalle_image_url, db) # 이미지 결과 (1차 경로 전달 -> 결과 생성)
    return {
        "sd": sd_result
    }
