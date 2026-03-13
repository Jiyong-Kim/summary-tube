import logging

from dotenv import load_dotenv
import google.generativeai as genai
from googleapiclient.discovery import build

from utils.db import get_code

# 비용 절감을 위한 입력 텍스트 길이 제한 (약 15,000자)
# MAX_INPUT_LENGTH = 15000

def summarize_with_gemini(text: str) -> str | None:
    """
    주어진 텍스트를 Gemini API를 사용하여 요약합니다.
    필요 시 API 키를 확인하고 Gemini 클라이언트를 설정합니다.
    """
    # if len(text) > MAX_INPUT_LENGTH:
    #     logging.info(f"스크립트 길이({len(text)}자)가 과도하여 비용 절감을 위해 앞부분 {MAX_INPUT_LENGTH}자만 사용합니다.")
    #     text = text[:MAX_INPUT_LENGTH]

    logging.info(f"스크립트 길이({len(text)}자)")
    try:
        api_key = get_code("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다!")

        genai.configure(api_key=api_key)
        # 유료 사용시에는 아래 모델 고려 / Batch 동작 고려. ( 비용 절감 )
        # model = genai.GenerativeModel("gemini-2.5-flash-lite") 
        model = genai.GenerativeModel("gemini-3.1-flash-lite-preview") 
        prompt = f"""다음 내용을 Blogger형식에 맞춰 정리하세요. 
            서론, 인사말, '이 글은 ~' 등의 설명은 절대 금지.
            <h1>부터 시작하는 HTML 본문 내용만 출력.
            댓글유도퀴즈 금지.
            
            내용 :
            {text}"""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"AI 요약 오류: {e}")
        return None
