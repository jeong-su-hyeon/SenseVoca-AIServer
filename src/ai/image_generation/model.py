# [ image_generation/model.py ]
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from config import Base

# 테스트옹
class ImageGeneration(Base):
    __tablename__ = "image_generation"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    word: Mapped[str] = mapped_column(String(100), nullable=False)
    association: Mapped[str] = mapped_column(String(1024))
    image_url: Mapped[str] = mapped_column(Text) 

# 단어 공통 정보 (word_info)
class WordInfo(Base):
    __tablename__ = "word_info"

    word_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    word: Mapped[str] = mapped_column(String(100), nullable=False)
    phonetic_us: Mapped[str] = mapped_column(String(100), nullable=False)
    phonetic_uk: Mapped[str] = mapped_column(String(100), nullable=False)
    phonetic_aus: Mapped[str] = mapped_column(String(100), nullable=False)

# 기본 제공 단어장 - 단어 상세 정보 (basic_word)
class BasicWord(Base):
    __tablename__ = "basic_word"

    basic_word_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("word_info.word_id"), nullable=False)
    meaning: Mapped[str] = mapped_column(String(255), nullable=False)
    association: Mapped[str] = mapped_column(String(1024), nullable=False)
    association_eng: Mapped[str] = mapped_column(String(1024), nullable=False)
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    example_eng: Mapped[str] = mapped_column(Text, nullable=False)
    example_kor: Mapped[str] = mapped_column(Text, nullable=False)
