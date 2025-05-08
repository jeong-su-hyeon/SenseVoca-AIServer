# [ image_generation/router.py ]
import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config import SessionLocal
from ai.image_generation.dto import ImageGenerationRequest
from ai.image_generation.service.dalle import service_dalle
from ai.image_generation.service.sd import service_sd
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
    dalle_result = service_dalle(request)           # 이미지 결과 
    word = dalle_result["word"]                     # 단어
    association = dalle_result["association"]       # 프롬프트 문장
    dalle_local_path = dalle_result["dalle_local_path"]     # 1차 이미지 경로

    # [2] SD - 2차 이미지 생성 (최종)
    sd_result = service_sd(word, association, dalle_local_path, db) # 이미지 결과 (1차 경로 전달 -> 결과 생성)

    return {
        "dalle": dalle_result,
        "sd": sd_result
    }

# 테스트용
@router.post("/image-generation/sd-test")
def router_test(db: Session = Depends(get_db)):
    print("[DEBUG] router_test 실행")

    file_path = "C:\\Users\\user\\Desktop\\2025-1\\Capstone\\Fast API\\SenseVoca_AIServer(github)\\src\\ai\\image_generation\\saved_images\\dalle"
    file_name = "dalle_apple_250507_212116.png"
    dalle_local_path = os.path.join(file_path, file_name)

    sd_result = service_sd("word", "prompt", dalle_local_path, db) # 이미지 결과 (1차 경로 전달 -> 결과 생성)
    return {
        "sd": sd_result
    }
