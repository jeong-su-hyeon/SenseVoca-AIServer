# [ img2img/config_sd.py ]
import os 

# [1] API 키
SD_API = "" # 코랩 실행했을 때 받는 WebUI 접속 링크

# [2] 이미지 저장 경로 
SD_IMAGE_DIRECTORY = os.path.join("ai", "image_generation", "saved_images", "sd")

# [3] 모델 및 프롬프트 설정 
# Seed & Denoising Strength
SEED = -1 #🔶
DENOISING_STRENGTH = 0.4 #🔶
# Checkpoint Model
SD_CHECKPOINT_MODEL1 = "v1-5-pruned-emaonly [6ce0161689]" # BASIC
SD_CHECKPOINT_MODEL2 = "cuteAnime_v10 [ee7048d4e1]"       # cuteAnime_v10
SD_CHECKPOINT = SD_CHECKPOINT_MODEL2 #🔶
# LoRA Model 
SD_LORA_MODEL1 = "<lora:J_illustration:1>"                # J_illustration
SD_LORA_MODEL2 = "<lora:20240106-1704552714107-0020_1:1>" # Children's illustration
SD_LORA = SD_LORA_MODEL1 #🔶
# ControlNet 컨트롤 모드 
SD_CONTROL_BALANCED = "Balanced"
SD_CONTROL_PROMPT = "My prompt is more important"
SD_CONTROL_CONTROLNET = "ControlNet is more important" 
SD_CONTROL_MODE = SD_CONTROL_CONTROLNET #🔶
# 프롬프트
SD_STYLE_PROMPT = ", cartoon, Children's Book Style" + SD_LORA
SD_NEGATIVE_PROMPT = """(worst quality, low qualilty, norma lquality:1.9), 
                        lowers, normal quality, ((monochrome)), ((grayscale)), skin spots, 
                        acnes, skin blemishes, age spot, nipples, watermark, signature, text, (bad finger), 
                        bad anatomy, bad hadns, (six fingers), nail"""

# [4] ControlNet 및 PayLoad 세부 설정
# ControlNet 적용 
SD_CONTROLNET = {
    "model": "control_canny-fp16 [e3fe7712]",
    "module": "canny",
    "weight": 1.0,
    "guidance": 1.0, # (가중치)
    "control_mode": SD_CONTROL_MODE
}

# 이미지 기본 설정
SD_PAYLOAD_BASE = {
    "prompt": SD_STYLE_PROMPT,
    "negative_prompt": SD_NEGATIVE_PROMPT,
    "seed": SEED, 
    "denoising_strength": DENOISING_STRENGTH,    
    "override_settings": {
        "sd_model_checkpoint": SD_CHECKPOINT
    },
    "steps": 20,
    "width": 512,
    "height": 512
}

