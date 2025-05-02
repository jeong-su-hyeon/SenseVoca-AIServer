# [ txt2img/dto.py ]
from pydantic import BaseModel 

# DTO 요청 (Request)
class ImageGenerationRequest(BaseModel):
    image_word: str 
    image_prompt: str

    