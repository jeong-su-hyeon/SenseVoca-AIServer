# [ image_generation/model.py ]
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from config import Base

# DB 테이블 매핑
class ImageGeneration(Base):
    __tablename__ = "image_generation"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    word: Mapped[str] = mapped_column(String(100), nullable=False)
    association: Mapped[str] = mapped_column(String(1024))
    image_url: Mapped[str] = mapped_column(Text) 