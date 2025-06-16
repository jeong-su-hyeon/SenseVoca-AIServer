import json
import asyncio
from fastapi import HTTPException
from src.app.schemas.llm_dto import (
    GetWordPhoneticsRequest,
    GetWordPhoneticsResponse,
    CreateMnemonicExampleRequest,
    CreateMnemonicExampleResponse,
    RegenerateMnemonicExampleRequest,
    RegenerateMnemonicExampleResponse
)
from src.app.services.llm_openai import request_openai_phonetics, request_openai_mnemonic, request_openai_regenerate_mnemonic
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
    ai_response = None
    for attempt in range(2):
        try:
            print(f"🟦 [AI 예문 생성 요청 - 시도 {attempt+1}]")
            ai_response = await request_openai_mnemonic(
                word=request.word,
                meaning=request.meaning,
                interest=request.interest
            )
            print("🟩 [AI 응답 수신]")
            print(ai_response)
            break  # 성공했으면 반복 종료
        except Exception as e:
            print(f"🟥 [AI 호출 예외 - 시도 {attempt+1}] {str(e)}")
            if attempt == 1:
                raise HTTPException(status_code=500, detail="OpenAI API 호출 오류 (2회 실패)")

    try:
        data = json.loads(ai_response)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"OpenAI 응답 파싱 실패: {ai_response}")

    image_prompt = data.pop("imagePrompt", None)
    if not image_prompt:
        raise HTTPException(status_code=500, detail="OpenAI 응답에 imagePrompt가 없습니다.")

    image_url = None
    for attempt in range(2):
        try:
            print(f"🟦 [이미지 생성 요청 - 시도 {attempt+1}]")
            image_url = generate_image_from_prompt(request.word, image_prompt)
            print("🟩 [이미지 생성 성공]")
            print(f"Image URL: {image_url}")
            break
        except Exception as e:
            print(f"🟥 [이미지 생성 실패 - 시도 {attempt+1}] {str(e)}")
            if attempt == 1:
                raise HTTPException(status_code=500, detail="이미지 생성 실패 (2회 실패)")
            await asyncio.sleep(1)  # 약간 대기

    return CreateMnemonicExampleResponse(
        meaning=data.get("meaning", ""),
        association=data.get("association", ""),
        exampleEng=data.get("exampleEng", ""),
        exampleKor=data.get("exampleKor", ""),
        imageUrl=image_url
    )

async def regenerate_mnemonic_example(request: RegenerateMnemonicExampleRequest) -> RegenerateMnemonicExampleResponse:
    ai_response = None
    for attempt in range(2):
        try:
            print(f"🟦 [AI 예문 생성 요청 - 시도 {attempt+1}]")
            ai_response = await request_openai_regenerate_mnemonic(
                word=request.word,
                meaning=request.meaning,
                association=request.association
            )
            print("🟩 [AI 응답 수신]")
            print(ai_response)
            break  # 성공했으면 반복 종료
        except Exception as e:
            print(f"🟥 [AI 호출 예외 - 시도 {attempt+1}] {str(e)}")
            if attempt == 1:
                raise HTTPException(status_code=500, detail="OpenAI API 호출 오류 (2회 실패)")

    try:
        data = json.loads(ai_response)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"OpenAI 응답 파싱 실패: {ai_response}")

    image_prompt = data.pop("imagePrompt", None)
    if not image_prompt:
        raise HTTPException(status_code=500, detail="OpenAI 응답에 imagePrompt가 없습니다.")

    image_url = None
    for attempt in range(2):
        try:
            print(f"🟦 [이미지 생성 요청 - 시도 {attempt+1}]")
            image_url = generate_image_from_prompt(request.word, image_prompt)
            print("🟩 [이미지 생성 성공]")
            print(f"Image URL: {image_url}")
            break
        except Exception as e:
            print(f"🟥 [이미지 생성 실패 - 시도 {attempt+1}] {str(e)}")
            if attempt == 1:
                raise HTTPException(status_code=500, detail="이미지 생성 실패 (2회 실패)")
            await asyncio.sleep(1)  # 약간 대기

    return RegenerateMnemonicExampleResponse(
        association=data.get("association", ""),
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