import os, shutil
from fastapi import APIRouter, status, HTTPException, UploadFile, File, Form
from src.app.schemas.stt_dto import PronunciationRequest, PronunciationResponse, OverallScore, PhonemeResult
from src.app.services.stt_service import stt_service, evaluate_pronunciation, extract_pronunciation_data

router = APIRouter()

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
    except Exception as e:
        raise HTTPException(status_code=500, detail="[라우터] 발음 평가 실패 : " + str(e))


# 🔴 나중에 삭제
@router.post(
    "/evaluate-pronunciation/local-audio",
    response_model=PronunciationResponse,
    tags=["STT"],
    status_code=status.HTTP_200_OK,
    summary="발음 평가 결과",
    description="영단어와 국가 코드, 사용자의 발음을 받아와 발음 평가를 진행한다."
)
async def fetch_word_pronunciation_local_audio(request: PronunciationRequest):
    try: 
        # 평가할 발음의 국가
        country_map = {
            "us": "en-US",
            "uk": "en-GB",
            "aus": "en-AU"
        }
        
        country_code = country_map.get(request.country)
        if not country_code:
            raise HTTPException(status_code=400, detail="지원하지 않는 국가 코드입니다.")

        pronunciation_data = await evaluate_pronunciation(request.word, country_code)     # [1] STT 발음 평가
        pronunciation_result = await extract_pronunciation_data(pronunciation_data)  # [2] 발음 결과 파싱
        return pronunciation_result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="[라우터] 발음 평가 실패 : " + str(e))


