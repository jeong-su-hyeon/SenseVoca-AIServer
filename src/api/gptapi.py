import time
import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
import json

router = APIRouter(prefix="/ai")

# 요청 데이터 모델
class InputData1(BaseModel):
    title: str
    count: int

class InputData2(BaseModel):
    content: str

class InputData3(BaseModel):
    title: str
    topic: str
    content: str

class InputData4(BaseModel):
    doctype: str
    content: str

# 🕒 시간을 사람이 읽을 수 있는 형식으로 변환하는 함수
def format_time(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# 주제 추천 및 설명
@router.post("/content1-summary", status_code=200)
async def get_content_summary(data: InputData1):
    """ 주제 추천 및 설명 """
    start_time = time.time()  # 요청 시간 기록

    try:
        if not data.title.strip():
            raise HTTPException(status_code=400, detail="입력된 주제가 없습니다.")
        if not data.count:
            raise HTTPException(status_code=400, detail="입력된 개수가 없습니다.")

        formatted_start_time = format_time(start_time)
        print(f"[요청 수신] {data.title}, {data.count} | 요청 시간: {formatted_start_time}")

        # OpenAI API 호출을 비동기 실행
        result = await run_in_threadpool(call_openai_api1, data.title, data.count)

        # 결과 JSON 변환
        try:
            result_json = json.loads(result)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="OpenAI 응답이 JSON 형식이 아닙니다.")

        end_time = time.time()  # 응답 시간 기록
        formatted_end_time = format_time(end_time)
        elapsed_time = end_time - start_time

        print(f"[응답 전송] 처리 완료 | 응답 시간: {formatted_end_time} | 실행 시간: {elapsed_time:.3f}초")
        print(f"전송된 데이터: {result_json}\n\n")
        
        return result_json

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# 스크랩글 정리 및 요약
@router.post("/content2-summary", status_code=200)
async def get_content2_summary(data: InputData2):
    """ 스크랩글 정리 및 요약 """
    start_time = time.time()
    
    try:
        if not data.content.strip():
            raise HTTPException(status_code=400, detail="입력된 내용이 없습니다.")

        formatted_start_time = format_time(start_time)
        print(f"[요청 수신] {data.content[:30]}... | 요청 시간: {formatted_start_time}")

        result = await run_in_threadpool(call_openai_api2, data.content)

        try:
            result_json = json.loads(result)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="OpenAI 응답이 JSON 형식이 아닙니다.")

        end_time = time.time()
        formatted_end_time = format_time(end_time)
        elapsed_time = end_time - start_time

        print(f"[응답 전송] 처리 완료 | 응답 시간: {formatted_end_time} | 실행 시간: {elapsed_time:.3f}초")
        print(f"전송된 데이터: {result_json}\n\n")
        return result_json

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# AI 컨텐츠 정리 요약
@router.post("/content3-summary", status_code=200)
async def get_content3_summary(data: InputData3):
    """ AI 컨텐츠 정리 요약 """
    start_time = time.time()

    try:
        if not data.content.strip():
            raise HTTPException(status_code=400, detail="입력된 내용이 없습니다.")

        formatted_start_time = format_time(start_time)
        print(f"[요청 수신] {data.topic} | 요청 시간: {formatted_start_time}")
        print(f"수신된 요청 데이터: {data.content}\n\n")

        result = await run_in_threadpool(call_openai_api3, data.title, data.topic, data.content)

        try:
            result_json = json.loads(result)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="OpenAI 응답이 JSON 형식이 아닙니다.")

        end_time = time.time()
        formatted_end_time = format_time(end_time)
        elapsed_time = end_time - start_time

        print(f"[응답 전송] 처리 완료 | 응답 시간: {formatted_end_time} | 실행 시간: {elapsed_time:.3f}초")
        print(f"전송된 데이터: {result_json}\n\n")

        return result_json

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# 문서화 (논문, 블로그, 노트)
@router.post("/content4-summary", status_code=200)
async def get_content4_summary(data: InputData4):
    """ 문서화 """
    start_time = time.time()

    try:
        if not data.content.strip():
            raise HTTPException(status_code=400, detail="입력된 내용이 없습니다.")

        formatted_start_time = format_time(start_time)
        print(f"[요청 수신] {data.doctype} | 요청 시간: {formatted_start_time}")
        print(f"수신된 요청 데이터: {data.content}\n\n")
        
        if data.doctype == "보고서":
            result = await run_in_threadpool(call_openai_api4, data.content)
        elif data.doctype == "블로그":
            result = await run_in_threadpool(call_openai_api5, data.content)
        elif data.doctype == "노트필기":
            result = await run_in_threadpool(call_openai_api6, data.content)

        try:
            result_json = json.loads(result)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="OpenAI 응답이 JSON 형식이 아닙니다.")

        end_time = time.time()
        formatted_end_time = format_time(end_time)
        elapsed_time = end_time - start_time

        print(f"[응답 전송] 처리 완료 | 응답 시간: {formatted_end_time} | 실행 시간: {elapsed_time:.3f}초")
        print(f"전송된 데이터: {result_json}\n\n")

        return result_json

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
