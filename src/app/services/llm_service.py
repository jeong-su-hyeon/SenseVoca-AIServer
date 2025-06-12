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
        print("🟦 [AI 예문 생성 시작]")
        print(f"요청 데이터: {request.dict()}")
        ai_response = await request_openai_mnemonic(
            word=request.word,
            meaning=request.meaning,
            interest=request.interest
        )

        print("🟩 [AI 응답 수신]")
        print(ai_response)

        data = json.loads(ai_response)

    except json.JSONDecodeError:
        print("🟥 [JSON 파싱 실패]")
        print(ai_response)
        raise HTTPException(status_code=500, detail=f"OpenAI 응답 파싱 실패: {ai_response}")

    except Exception as e:
        print("🟥 [AI 호출 예외]")
        print(str(e))
        raise HTTPException(status_code=500, detail=f"OpenAI API 호출 오류: {str(e)}")

    # 이미지 생성용 프롬프트 추출
    image_prompt = data.pop("imagePrompt", None)
    if not image_prompt:
        print("🟥 [imagePrompt 없음]")
        raise HTTPException(status_code=500, detail="OpenAI 응답에 imagePrompt가 없습니다.")

    try:
        print("🟦 [이미지 생성 요청]")
        image_url = generate_image_from_prompt(request.word, image_prompt)
        print("🟩 [이미지 생성 성공]")
        print(f"Image URL: {image_url}")
    except Exception as e:
        print("🟥 [이미지 생성 실패]")
        print(str(e))
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