openAI_key = ""

############ [수현] image_generation 테스트 config
# [config.py]
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# MySQL 연결 정보
DATABASE_URL = "mysql+pymysql://root:1234@localhost:3306/wb40"

# SQLAlchemy 연결
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

