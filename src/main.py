from fastapi import FastAPI
# from api.gptapi import router  # 라우터 임포트
from ai.image_generation.router import router as image_generation # Image Generation 라우터 
from config import Base, engine

app = FastAPI()
 
#app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Server, Open!"}

## Image Generation 라우터
app.include_router(image_generation)
@app.get("/image-generation")
def example():
    return 'Image Generation Server'
Base.metadata.create_all(bind=engine)
