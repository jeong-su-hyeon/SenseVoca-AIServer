# [ image_generation/router.py ]
import os
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from config import SessionLocal
from ai.image_generation.model import WordInfo, BasicWord
from ai.image_generation.service import service_image_generation

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 기본 제공 단어장 이미지 생성
@router.post("/api/ai/basic/image-generation")
def router_image_generation(response: Response, db: Session = Depends(get_db)):
    print("[DEBUG] 이미지 생성 ROUTER 실행")
    results = []

    # DB에서 전체 데이터 가져오기
    all_words = (db.query(BasicWord, WordInfo)
                .join(WordInfo, BasicWord.word_id == WordInfo.word_id)
                .all())

    # 범위 조절 🔶
    START_INDEX = 10
    END_INDEX = 20

    for i, (basic_word_obj, word_info_obj) in enumerate(all_words):
        if i < START_INDEX :
            continue
        if i >= END_INDEX :
            break

        basic_word_id = basic_word_obj.basic_word_id
        word = word_info_obj.word
        association = basic_word_obj.association
        association_eng = basic_word_obj.association_eng
        example_eng = basic_word_obj.example_eng

        print(f">> ROUTER i={i}, basic_word_id={basic_word_id}, 단어:{word}")

        try:
            # [SERVICE] 
            dalle_result = service_image_generation(basic_word_id, word, association, association_eng, example_eng, db)
            #dalle_local_path = dalle_result["dalle_local_path"]  # (나중에 삭제 🔴)
            cloud_image_url = dalle_result["image_url"]

            results.append({
                "result": "[ROUTER] 이미지 생성 및 업로드 성공",
                "basic_word_id": basic_word_id,
                "word": word,
                "association": association,
                "image_url": cloud_image_url
            })
            

        except Exception as e:
            print(f"[ERROR] basic_word_id {basic_word_id} 처리 실패 : {e}")
            results.append({
                "result": "[ROUTER] 이미지 생성 및 업로드 실패",
                "basic_word_id": basic_word_id,
                "word": word,
                "association": association,                
                "error": str(e)
            })

    success_count = sum(1 for r in results if "실패" not in r["result"])
    if success_count < len(results):
        response.status_code = status.HTTP_207_MULTI_STATUS
    else:
        response.status_code = status.HTTP_200_OK
    return {
        "message": "기본 단어 이미지 생성 처리 결과",
        "total": len(results),
        "success": success_count,
        "fail": len(results) - success_count,
        "results": results
    }
