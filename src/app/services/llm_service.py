import json
from fastapi import HTTPException
from src.app.schemas.llm_dto import (
    GetWordPhoneticsRequest,
    GetWordPhoneticsResponse,
    CreateMnemonicExampleRequest,
    CreateMnemonicExampleResponse
)
from src.app.services.llm_openai import request_openai_phonetics, request_openai_mnemonic
from src.app.services.image_service import generate_image_from_prompt


# 발음 조회 - OpenAI 기반
async def get_word_phonetics(request: GetWordPhoneticsRequest) -> GetWordPhoneticsResponse:
    try:
        ai_response = await request_openai_phonetics(request.word, request.meaning)
        data = json.loads(ai_response)
        return GetWordPhoneticsResponse(
            word=request.word,
            phoneticUs=data.get("phoneticUs", ""),
            phoneticUk=data.get("phoneticUk", ""),
            phoneticAus=data.get("phoneticAus", "")
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"OpenAI 응답 파싱 실패: {ai_response}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API 호출 실패: {str(e)}")


# 니모닉 생성 - OpenAI + 이미지 생성 포함
async def generate_mnemonic_example(request: CreateMnemonicExampleRequest) -> CreateMnemonicExampleResponse:
    try:
        ai_response = await request_openai_mnemonic(
            word=request.word,
            meaning=request.meaning,
            interest=request.interest
        )
        data = json.loads(ai_response)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"OpenAI 응답 파싱 실패: {ai_response}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API 호출 오류: {str(e)}")

    # 이미지 프롬프트 처리
    image_prompt = data.pop("imagePrompt", None)
    if not image_prompt:
        raise HTTPException(status_code=500, detail="OpenAI 응답에 imagePrompt가 없습니다.")

    try:
        image_url = generate_image_from_prompt(request.word, image_prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 생성 실패: {str(e)}")

    return CreateMnemonicExampleResponse(
        meaning=data.get("meaning", ""),
        association=data.get("association", ""),
        exampleEng=data.get("exampleEng", ""),
        exampleKor=data.get("exampleKor", ""),
        imageUrl=image_url
    )


# 발음 조회 - 임시 고정값
async def get_word_phonetics_workaround(_: GetWordPhoneticsRequest) -> GetWordPhoneticsResponse:
    return GetWordPhoneticsResponse(
        word="bath",
        phoneticUs="[bæθ]",
        phoneticUk="[bɑːθ]",
        phoneticAus="[baːθ]"
    )

# 니모닉 생성 - 임시 고정값
async def generate_mnemonic_workaround(_: CreateMnemonicExampleRequest) -> CreateMnemonicExampleResponse:
    return CreateMnemonicExampleResponse(
        meaning="[명] 목욕, 욕조 / [동] 목욕하다",
        association="욕조에 빠뜨려서 기억해! bath는 욕조에서 목욕하는 거야!",
        exampleEng="I take a bath every night before bed.",
        exampleKor="나는 매일 밤 자기 전에 목욕을 한다.",
        imageUrl="https://dummyimage.com/600x400/000/fff&text=bath+mnemonic"
    )