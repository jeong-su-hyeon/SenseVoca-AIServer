from pydantic import BaseModel


# 요청 DTO: 단어 + 의미
class GetWordPhoneticsRequest(BaseModel):
    word: str
    meaning: str


# 응답 DTO: 발음 정보
class GetWordPhoneticsResponse(BaseModel):
    word: str
    phoneticUs: str
    phoneticUk: str
    phoneticAus: str


# 요청 DTO: 니모닉 예문 생성용 (관심사 추가)
class CreateMnemonicExampleRequest(BaseModel):
    word: str
    meaning: str
    interest: str


# 응답 DTO: 니모닉 예문 생성 결과
class CreateMnemonicExampleResponse(BaseModel):
    meaning: str
    association: str    # 니모닉 예문
    imageUrl: str       # AI 이미지 URL
    exampleEng: str     # 영어 예문
    exampleKor: str     # 한글 해석 예문