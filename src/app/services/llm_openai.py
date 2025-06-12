from openai import AsyncOpenAI
from src.app.core.config import settings
from src.app.prompts.phonetic_prompt import phonetic_prompt
from src.app.prompts.mnemonic_prompt import mnemonic_prompt

client = AsyncOpenAI(api_key=settings.openai_api_key)

async def request_openai_phonetics(word: str, meaning: str) -> str:
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": phonetic_prompt()},
                {"role": "user", "content": f"단어: {word}\n뜻: {meaning}"}
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise ValueError(f"OpenAI API 호출 오류 (발음): {str(e)}")


async def request_openai_mnemonic(word: str, meaning: str, interest: str) -> str:
    try:
        print("🟦 [OpenAI 요청 시작]")
        print(f"   - 단어: {word}, 뜻: {meaning}, 관심사: {interest}")
        
        response = await client.chat.completions.create(
            model="o4-mini",
            messages=[
                {"role": "system", "content": mnemonic_prompt()},
                {"role": "user", "content": f"단어: {word}\n뜻: {meaning}\n관심사: {interest}"}
            ],
            reasoning_effort="medium"
        )
        result = response.choices[0].message.content
        print("🟩 [OpenAI 응답 완료]")
        print(result)
        return result
    
    except Exception as e:
        print("🟥 [OpenAI 호출 중 예외 발생]")
        print(f"예외: {str(e)}")
        raise ValueError(f"OpenAI API 호출 오류 (니모닉): {str(e)}")