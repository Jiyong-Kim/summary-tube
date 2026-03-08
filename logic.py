import os
import json
import logging
import datetime
import re
import markdown
import asyncio
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
import google.generativeai as genai
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from youtube_transcript_api import YouTubeTranscriptApi
from telegram import Bot

# 환경설정
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# API 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))

# 상수
BLOG_ID = "8117610145577153361"
SCOPES = ["https://www.googleapis.com/auth/blogger"]

def get_blog_service():
    """인증된 Blogger API 서비스 객체 반환"""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
            
    return build("blogger", "v3", credentials=creds)

def get_today_videos_from_list():
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    today_video_urls = []

    with open("channels.json", "r", encoding="utf-8") as f:
        channels = json.load(f)

    for channel in channels:
        res = youtube.channels().list(id=channel["channel_id"], part="contentDetails").execute()
        if not res.get("items"): continue
        uploads_id = res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        playlist_res = youtube.playlistItems().list(playlistId=uploads_id, part="snippet", maxResults=10).execute()
        for item in playlist_res.get("items", []):
            if item["snippet"]["publishedAt"][:10] >= yesterday:
                v_id = item["snippet"]["resourceId"]["videoId"]
                today_video_urls.append(f"https://www.youtube.com/watch?v={v_id}")
    return today_video_urls

def get_transcript(video_id):
    try:
        return " ".join([t['text'] for t in YouTubeTranscriptApi.get_transcript(video_id, languages=["ko", "en"])])
    except Exception as e:
        logging.error(f"스크립트 추출 오류 ({video_id}): {e}")
        return None

def summarize_with_gemini(text):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash") 
        prompt = f"다음 내용을 블로그 포스팅 형식으로 요약해줘. 마지막 문단에서 본문 중 사실이 아닌 부분을 지적하고, 사실에 근거하여 반론을 제기해줘:\n\n{text}"
        return model.generate_content(prompt).text
    except Exception as e:
        logging.error(f"AI 요약 오류: {e}")
        return None

def post_to_blog(title, content, source_url):
    try:
        service = get_blog_service()
        formatted_content = f"{content}<br><hr><p>출처: <a href='{source_url}'>{source_url}</a></p>"
        
        post_body = {
            "kind": "blogger#post",
            "title": title,
            "content": formatted_content,
            "labels": ["유튜브요약"]
        }
        result = service.posts().insert(blogId=BLOG_ID, body=post_body).execute()
        logging.info(f"게시 성공! ID: {result['id']}")
        return True
    except Exception as e:
        logging.error(f"블로그 게시 오류: {e}")
        return False

def process_single_video(url):
    """영상 하나를 처리하는 전체 파이프라인"""
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url)
    if not match: return False
    
    video_id = match.group(1)
    script = get_transcript(video_id)
    if not script: return False
    
    summary = summarize_with_gemini(script)
    if not summary: return False
    
    title = summary.splitlines()[0]
    content = markdown.markdown(summary)
    
    return post_to_blog(title, content, url)

async def send_telegram_alert(message):
    try:
        bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
        await bot.send_message(chat_id=os.getenv("TELEGRAM_CHAT_ID"), text=message)
    except Exception as e:
        logging.error(f"텔레그램 전송 오류: {e}")