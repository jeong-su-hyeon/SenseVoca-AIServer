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
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": mnemonic_prompt()},
                {"role": "user", "content": f"단어: {word}\n뜻: {meaning}\n관심사: {interest}"}
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise ValueError(f"OpenAI API 호출 오류 (니모닉): {str(e)}")