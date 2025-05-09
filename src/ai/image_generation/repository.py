# [ image_generation/repository.py ]
from sqlalchemy.orm import Session
from ai.image_generation.model import ImageGeneration, BasicWord

# 기본 제공 단어장 basic_word 테이블 image_url 칼럼 UPDATE
def repository_image_generation(basic_word_id:int, cloud_image_url: str, db) -> BasicWord:
    print(f"[DEBUG] repository_image_generation 실행: id={basic_word_id}")

    # [1] 해당 row 가져오기
    basic_word = db.query(BasicWord).filter(BasicWord.basic_word_id == basic_word_id).first()

    if not basic_word:
        raise Exception(f"테이블에 존재하지 않는 {basic_word_id}입니다.")
    
    # [2] 테이블 UPDATE
    basic_word.image_url = cloud_image_url
    
    db.commit()
    db.refresh(basic_word)

    return basic_word


# 테스트용 (나중에 삭제 🔴)
def repository_test_image_generation(word: str, association: str, cloud_image_url: str, db: Session) -> ImageGeneration:
    print("[DEBUG] repository_test_image_generation 실행")

    image = ImageGeneration(word=word, 
                            association=association, 
                            image_url=cloud_image_url)
    db.add(image)
    db.commit()
    db.refresh(image)

    return image
