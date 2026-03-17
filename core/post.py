import json
import os
import logging

from dotenv import load_dotenv

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from utils import db

# 상수
SCOPES = ["https://www.googleapis.com/auth/blogger"]

def get_flow_from_db():
    # 1. DB에서 JSON 문자열을 가져옵니다.
    secret_json_str = db.get_code("GOOGLE_CLIENT_SECRET")
    
    if not secret_json_str:
        raise ValueError("DB에 GOOGLE_CLIENT_SECRET 설정이 없습니다!")
    
    # 2. 문자열을 딕셔너리로 변환
    client_config = json.loads(secret_json_str)
    
    # 3. 파일 대신 딕셔너리를 사용하여 Flow 생성
    flow = InstalledAppFlow.from_client_config(
        client_config, 
        SCOPES
    )
    return flow

def get_blog_service():
    """인증된 Blogger API 서비스 객체 반환"""
    creds = None
    
    token_data = db.get_code("GOOGLE_BLOGGER_TOKEN")
    if token_data:
        # DB에 저장된 문자열을 딕셔너리로 변환
        creds_info = json.loads(token_data)
        creds = Credentials.from_authorized_user_info(creds_info, SCOPES)

    # 2. 토큰이 없거나 만료된 경우 처리
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = get_flow_from_db()
            creds = flow.run_local_server(port=0)
        
        # 3. 새로 받아온 토큰을 DB에 저장 (json 문자열로 변환하여 저장)
        db.update_code("GOOGLE_BLOGGER_TOKEN", creds.to_json())
            
    return build("blogger", "v3", credentials=creds)

def post_to_blog(title, content, source_url):
    try:
        service = get_blog_service()
        
        # DB에서 블로그 ID 조회, 없으면 기본값 사용
        blog_id = db.get_code("GOOGLE_BLOGGER_ID") 
        
        
        #formatted_content = f"{content}<br><hr><p>출처: <a href='{source_url}'>{source_url}</a></p>"
        
        post_body = {
            "kind": "blogger#post",
            "title": title,
            "content": content,
            "labels": ["유튜브요약"]
        }
        result = service.posts().insert(blogId=blog_id, body=post_body).execute()
        logging.info(f"게시 성공! ID: {result['id']}")
        return True
    except HttpError as err:
        logging.error(f"API 요청 오류: {err.resp.status} - {err.content}")
        return False
    except Exception as e:
        logging.error(f"블로그 게시 오류: {e}")
        return False