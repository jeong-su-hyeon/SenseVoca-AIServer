# [ txt2img/config.py ]
import os

# [1] API 키
DALLE_API = "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"

# [2] 이미지 저장 경로
DALLE_IMAGE_DIRECTORY = os.path.join("ai", "image_generation", "saved_images", "dalle")

# [3] 설정
# 모델
DALLE_MODEL = "dall-e-2"

# 프롬프트 문장 
DALLE_STYLE_PROMPT = ", cartoon"
DALLE_NEGATIVE_PROMPT = """, without grayscale or monochrome tones. Avoid bad anatomy, distorted hands or fingers (like six fingers or wrong nails). 
                        Exclude skin imperfections such as acne, blemishes, age spots. No watermarks, no text, no signatures. 
                        Do not include nudity or inappropriate content."""

# 이미지 크기
DALLE_IMAGE_SIZE = "256x256"

