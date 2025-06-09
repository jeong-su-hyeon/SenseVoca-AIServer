import os, shutil
import json
from fastapi import APIRouter, status, HTTPException, UploadFile, File, Form
import azure.cognitiveservices.speech as speechsdk
from src.app.core.config import settings
from src.app.core.phoneme_feedback import PHONEME_FEEDBACK
from src.app.schemas.stt_dto import PronunciationResponse, OverallScore, PhonemeResult

# [0] STT 처리
async def stt_service(word: str, country: str, audio: UploadFile):
    try:
        # 1) 국가 코드 매핑
        country_map = {"us": "en-US", "uk": "en-GB", "aus": "en-AU"}            
        country_code = country_map.get(country)
        if not country_code:
            raise HTTPException(status_code=400, detail="지원하지 않는 국가 코드입니다.")

        # 2) 파일 저장
        os.makedirs("temp_uploads", exist_ok=True)
        temp_path = f"temp_uploads/{audio.filename}"
        try:
            with open(temp_path, "wb") as f:
                shutil.copyfileobj(audio.file, f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"오디오 파일 저장 실패: {e}")

        # 3) STT 발음 평가
        pronunciation_data = await evaluate_pronunciation(word, country_code, temp_path) 

        # 4) 결과 파싱
        pronunciation_result = await extract_pronunciation_data(pronunciation_data)

        return pronunciation_result

    except HTTPException as he:
        raise he  # 이미 status_code 있는 예외는 그대로 던짐
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"[서비스] 처리 중 알 수 없는 오류 발생: {str(e)}")
    finally:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


# [1] STT 발음 평가
async def evaluate_pronunciation(word: str, country_code: str, temp_path: str) -> dict:
    try:
        speech_key = settings.stt_api_key
        service_region = "koreacentral"

        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_config.speech_recognition_language = country_code
        audio_config = speechsdk.audio.AudioConfig(filename=temp_path)

        pron_config = speechsdk.PronunciationAssessmentConfig(
            reference_text=word,
            grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
            granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
            enable_miscue=True
        )

        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        pron_config.apply_to(recognizer)

        result = recognizer.recognize_once_async().get()

        if result.reason != speechsdk.ResultReason.RecognizedSpeech:
            raise Exception(f"STT 실패: {result.reason}, 상세: {result.text}")

        json_result = result.properties[speechsdk.PropertyId.SpeechServiceResponse_JsonResult]
        return json.loads(json_result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"[STT 평가 오류] {str(e)}")

# [2] 발음 결과 파싱
async def extract_pronunciation_data(pronunciation_data: dict) -> PronunciationResponse:
    try:
        nbest = pronunciation_data.get("NBest", [{}])[0]
        word_data = nbest["Words"][0]
        phonemes = word_data.get("Phonemes", [])

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
            word=word_data["Word"],
            overallScore=OverallScore(
                accuracy=nbest["PronunciationAssessment"]["AccuracyScore"],
                fluency=nbest["PronunciationAssessment"]["FluencyScore"],
                completeness=nbest["PronunciationAssessment"]["CompletenessScore"],
                total=nbest["PronunciationAssessment"]["PronScore"]
            ),
            phonemeResults=phoneme_results
        )
    except KeyError as ke:
        raise HTTPException(status_code=500, detail=f"[데이터 파싱 실패] 필드 누락: {ke}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"[데이터 파싱 실패] {str(e)}")
