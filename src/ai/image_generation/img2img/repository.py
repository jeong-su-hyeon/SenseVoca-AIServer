# [ img2img/repository.py ]
from sqlalchemy.orm import Session
from ai.image_generation.img2img.model import ImageGeneration

def repository_image_generation(image_word: str, image_prompt: str, final_path: str, db: Session) -> ImageGeneration:
    print("[DEBUG] repository_image_generation 실행")

    image = ImageGeneration(image_word=image_word, image_prompt=image_prompt, image_url=final_path)
    db.add(image)
    db.commit()
    db.refresh(image)

    return image
