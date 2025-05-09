# [ image_generation/dto.py ]
from pydantic import BaseModel 



# 기본 제공 단어장 이미지 생성 요청
class ImageGenerationRequest(BaseModel):
    word_id: int

# 테스트용
class ImageGenerationRequestTest(BaseModel):
    word: str 
    association: str