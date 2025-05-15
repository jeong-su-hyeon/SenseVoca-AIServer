# [ image_generation/config/dalle.py ]
import os
from api.image_generation import HIDE_API_KEY

# [1] API 키
API_KEY = HIDE_API_KEY

# [2] 이미지 저장 경로
LOCAL_IMAGE_DIRECTORY = os.path.join("ai", "image_generation", "saved_images", "dalle")

# [3] 설정
# 모델
DALLE_MODEL = "dall-e-3"

# 프롬프트 문장 
STYLE_PROMPT = ", children’s book style, children's book illustration, flat colors, thin line art, minimal details, cute cartoon style, soft lighting, clear lines, friendly expression, clear color"
NEGATIVE_PROMPT = """, no grayscale, no monochrome, no detailed muscles, no abs, no violent themes, no weapons, no realistic anatomy, 
no intense shadows, no text, no watermarks, no nudity, no creepy or unsettling faces, avoid excessive details, no photo style, no shirtless, no nudity, not creepy face, no grey scale"""


# 이미지 크기
IMAGE_SIZE = "1024x1024"

