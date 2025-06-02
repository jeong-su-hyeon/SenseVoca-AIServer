import os, shutil
import json
from fastapi import APIRouter, status, HTTPException, UploadFile, File, Form
import azure.cognitiveservices.speech as speechsdk
from src.app.core.config import settings
from src.app.core.phoneme_feedback import PHONEME_FEEDBACK
from src.app.schemas.stt_dto import PronunciationResponse, OverallScore, PhonemeResult

# [0] STT 처리
async def stt_service(word: str, country: str, audio: str):
    try:
        # 1) 국가 코드 매핑
        country_map = {
            "us": "en-US",
            "uk": "en-GB",
            "aus": "en-AU"
        }            
        country_code = country_map.get(country)
        if not country_code:
            raise HTTPException(status_code=400, detail="지원하지 않는 국가 코드입니다.")
        
        # 2) 로컬에 임시 저장
        os.makedirs("temp_uploads", exist_ok=True)
        temp_path = f"temp_uploads/{audio.filename}"
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)

        # 3) STT 발음 평가
        pronunciation_data = await evaluate_pronunciation(word, country_code, temp_path) 
        
        # 4) 발음 결과 파싱
        pronunciation_result = await extract_pronunciation_data(pronunciation_data)     

        return pronunciation_result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"[서비스] 처리 중 오류 발생: {str(e)}")

    finally: 
        # 5) 로컬 파일 삭제
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

# [1] STT 발음 평가
async def evaluate_pronunciation(word: str, country_code: str, temp_path: str) -> dict:
    # +) API 키 및 지역 설정
    speech_key = settings.stt_api_key
    service_region = "koreacentral"

    # +) STT 구성
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_recognition_language = country_code        
    audio_config = speechsdk.audio.AudioConfig(filename=temp_path) 

    # 1) 발음 평가 설정
    pron_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=word,                                                        # 발음할 단어 
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,  # 점수 체계 0~100점으로 평가
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,           # 음소 단위
        enable_miscue=True                                                          # 누락, 오발음 등 감지
    )

    # 2) 발음 인식기 구성 및 발음 평가
    recognizer = speechsdk. SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    pron_config.apply_to(recognizer) # 발음 평가 처리
    result = recognizer.recognize_once_async().get() # 발음 결과 객체

    # 3) JSON 결과 리턴
    json_result = result.properties[speechsdk.PropertyId.SpeechServiceResponse_JsonResult]

    return json.loads(json_result)

# [2] 발음 결과 파싱
async def extract_pronunciation_data(pronunciation_data: dict) -> PronunciationResponse:
    # 1) dict(JSON) 결과 파싱
    nbest = pronunciation_data.get("NBest", [{}])[0]      # 가장 정확한 발음 후보
    word_data = nbest["Words"][0]                         # 분석된 첫 번째 단어 
    phonemes = word_data.get("Phonemes", [])              # 그 단어의 음소별 점수 정보

    # 음소별로 저장할 점수 리스트 (symbol, score, feeback)
    phoneme_results = []

    for p in phonemes:
        symbol = p["Phoneme"]
        score = p["PronunciationAssessment"]["AccuracyScore"]

        if score >= 90:
            feedback = "Excellent"
        elif 80 <= score < 90:
            feedback = "Good"
        else:
            feedback = PHONEME_FEEDBACK.get(symbol, "-")

        phoneme_results.append(PhonemeResult(symbol=symbol, score=score, feedback=feedback))

    return PronunciationResponse(
        word = word_data["Word"],
        overallScore = OverallScore(
            accuracy = nbest["PronunciationAssessment"]["AccuracyScore"],
            fluency = nbest["PronunciationAssessment"]["FluencyScore"],
            completeness = nbest["PronunciationAssessment"]["CompletenessScore"],
            total = nbest["PronunciationAssessment"]["PronScore"]),
        phonemeResults = phoneme_results
        )