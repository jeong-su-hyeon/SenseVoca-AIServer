# [ image_generation/dto.py ]
from pydantic import BaseModel 

# DTO 요청 (Request)
class ImageGenerationRequest(BaseModel):
    word: str 
    association: str

    