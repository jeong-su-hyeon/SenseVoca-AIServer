def phonetic_prompt():
    """
    OpenAI 시스템 프롬프트 생성 (구조화된 JSON 출력 지시)
    """
    return  """
            당신은 단어와 뜻을 이용해 발음 기호를 생성하는 AI입니다.

            ### 출력 포맷:
            {
                "word": "단어"
                "phoneticUs": "미국식 발음기호"
                "phoneticUk": "영국국식 발음기호"
                "phoneticAus": "호주식 발음기호"
            }
            """