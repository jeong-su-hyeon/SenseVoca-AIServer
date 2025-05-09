# [ image_generation/router.py ]
import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config import SessionLocal
from ai.image_generation.model import WordInfo, BasicWord
from ai.image_generation.dto import ImageGenerationRequest, ImageGenerationRequestTest
from ai.image_generation.service.dalle import service_dalle
from ai.image_generation.service.sd import service_sd
from ai.image_generation.service.test_dalle import service_test_dalle
from ai.image_generation.service.test_sd import service_test_sd

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 기본 제공 단어장 이미지 생성
@router.post("/basic/image-generation")
def router_image_generation(db: Session = Depends(get_db)):
    print("[DEBUG] router_image_generation 실행")
    results = []

    # DB에서 전체 데이터 가져오기
    all_words = (db.query(BasicWord, WordInfo)
                .join(WordInfo, BasicWord.word_id == WordInfo.word_id)
                .all())

    # 범위 조절 🔶
    START_INDEX = 0
    END_INDEX = 5

    for i, (basic_word_obj, word_info_obj) in enumerate(all_words):
        if i < START_INDEX :
            continue
        if i >= END_INDEX :
            break

        basic_word_id = basic_word_obj.basic_word_id
        association_eng = basic_word_obj.association_eng
        #prompt_text = association.split(":")[-1].strip()

        word = word_info_obj.word

        print(f"[DEBUG] i={i}, basic_word_id={basic_word_id}, 단어:{word}")

        try:
            # [1] DALLE 이미지 생성
            dalle_result = service_dalle(word, association_eng)
            dalle_local_path = dalle_result["dalle_local_path"]  # (나중에 수정 🔴)

            # [2] SD 이미지 생성
            sd_result = service_sd(basic_word_id, word, association_eng, dalle_local_path, db)

            results.append({
                "word_id": basic_word_id,
                "word": word,
                "result": "이미지 생성 및 업로드 성공",
                "image_url": sd_result["image_url"]
            })
            

        except Exception as e:
            print(f"[ERROR] basic_word_id {basic_word_id} 처리 실패 : {e}")
            results.append({
                "word_id": basic_word_id,
                "word": word,
                "result": "이미지 생성 및 업로드 실패",
                "error": str(e)
            })



# -------------------------------------------------
# (나중에 삭제 🔴)
# DALLE -> SD 이미지 생성
@router.post("/test/image-generation")
def router_test_image_generation(request: ImageGenerationRequestTest, db: Session = Depends(get_db)):
    print("[DEBUG] router_test_image_generation 실행")
    
    # [1] DALLE - 1차 이미지 생성
    dalle_result = service_test_dalle(request)           # 이미지 결과 
    word = dalle_result["word"]                     # 단어
    association = dalle_result["association"]       # 프롬프트 문장
    dalle_local_path = dalle_result["dalle_local_path"]     # 1차 이미지 경로

    # [2] SD - 2차 이미지 생성 (최종)
    sd_result = service_test_sd(word, association, dalle_local_path, db) # 이미지 결과 (1차 경로 전달 -> 결과 생성)

    return {
        "dalle": dalle_result,
        "sd": sd_result
    }

# SD만 테스트
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
