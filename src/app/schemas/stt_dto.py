# schemas/stt_dto.py
from pydantic import BaseModel
from typing import List,Optional

# 발음 평가 결과 - 전체 점수
class OverallScore(BaseModel):
    accuracy: float
    fluency: float
    completeness: float
    total: float    

# 발음 평가 결과 - 음소 단위 점수
class PhonemeResult(BaseModel):
    symbol: str
    score: float
    feedback: str

# 응답 DTO: 발음 평가 전체 결과
class PronunciationResponse(BaseModel):
    word: str
    overallScore: OverallScore
    phonemeResults: List[PhonemeResult]

