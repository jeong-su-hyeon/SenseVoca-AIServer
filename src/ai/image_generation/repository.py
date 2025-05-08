# [ image_generation/repository.py ]
from sqlalchemy.orm import Session
from ai.image_generation.model import ImageGeneration

def repository_image_generation(word: str, association: str, cloud_image_url: str, db: Session) -> ImageGeneration:
    print("[DEBUG] repository_image_generation 실행")

    image = ImageGeneration(word=word, 
                            association=association, 
                            image_url=cloud_image_url)
    db.add(image)
    db.commit()
    db.refresh(image)

    return image
