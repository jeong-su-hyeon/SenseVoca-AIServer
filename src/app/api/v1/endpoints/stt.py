import os, shutil
from fastapi import APIRouter, status, HTTPException, UploadFile, File, Form
from src.app.schemas.stt_dto import PronunciationResponse
from src.app.services.stt_service import stt_service
router = APIRouter()

router = APIRouter(prefix="/ai")

@router.post(
    "/evaluate-pronunciation",
    response_model=PronunciationResponse,
    tags=["STT"],
    status_code=status.HTTP_200_OK,
    summary="발음 평가 결과",
    description="영단어와 국가 코드, 사용자의 발음을 받아와 발음 평가를 진행한다."
)
async def fetch_word_pronunciation(
    word: str = Form(...),
    country: str = Form(...),
    audio: UploadFile = File(...)):
    try: 
        return await stt_service(word, country, audio)             
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"[라우터] 잘못된 요청 값: {ve}")
    except IOError as ioe:
        raise HTTPException(status_code=500, detail=f"[라우터] 파일 처리 오류: {ioe}")
    except Exception as e:
        traceback.print_exc()  # 서버 콘솔 로그에 전체 스택 추적 출력
        raise HTTPException(status_code=500, detail=f"[라우터] 발음 평가 실패: {str(e)}")
