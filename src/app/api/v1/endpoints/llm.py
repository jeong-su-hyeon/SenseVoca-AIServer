from fastapi import APIRouter, status, HTTPException
from src.app.schemas.llm_dto import (
    GetWordPhoneticsRequest,
    GetWordPhoneticsResponse,
    CreateMnemonicExampleRequest,
    CreateMnemonicExampleResponse
)
from src.app.services.llm_service import (
    get_word_phonetics,
    generate_mnemonic_example,
    get_word_phonetics_workaround,
    generate_mnemonic_workaround
)

router = APIRouter(prefix="/ai")

@router.post(
    "/word-phonetics",
    response_model=GetWordPhoneticsResponse,
    tags=["LLM"],
    status_code=status.HTTP_200_OK,
    summary="단어 발음 정보 조회",
    description="입력된 단어와 뜻을 바탕으로 미국, 영국, 호주식 발음을 반환"
)
async def fetch_word_phonetics(request: GetWordPhoneticsRequest):
    try:
        return await get_word_phonetics_workaround(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post(
    "/generate-mnemonic",
    response_model=CreateMnemonicExampleResponse,
    tags=["LLM"],
    status_code=status.HTTP_200_OK,
    summary="니모닉 예문 생성",
    description="단어, 뜻, 관심사를 기반으로 llm을을 통해 연상 예문, 영어 예문, 한글 해석, 이미지 URL을 생성"
)
async def fetch_mnemonic_example(request: CreateMnemonicExampleRequest):
    try:
        return await generate_mnemonic_workaround(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))