# [ img2img/model.py ]
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from config import Base

# DB 테이블 매핑
class ImageGeneration(Base):
    __tablename__ = "image_generation"

    image_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    image_prompt: Mapped[str] = mapped_column(String(225), nullable=False)
    image_url: Mapped[str] = mapped_column(String(1024), nullable=False)