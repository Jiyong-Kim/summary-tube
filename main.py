
import asyncio
import concurrent.futures
import re
import logging
import time

from dotenv import load_dotenv

# 내부 모듈
from core.gemini import summarize_with_gemini
from core.post import post_to_blog
from core.telegram import send_telegram_alert
from core.youtube import get_videos_from_list, get_transcript
from utils import db

# 환경설정
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_id(url):
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url)
    return match.group(1) if match else None

def process_single_video(url):
    video_id = extract_id(url)
    title, summary = None, None 
    
    # or not db.is_video_unprocessed(video_id) 부분 삭제 가능.
    if not video_id or not db.is_video_unprocessed(video_id):
        return False
    try:
        script = get_transcript(video_id)
        if not script: return False

        summary = summarize_with_gemini(script)
        if not summary: return False

        parts = summary.split('\n', 1)
        if len(parts) >= 2:
            raw_title, content = parts
            title = re.sub('<[^<]+?>', '', raw_title).strip()
        else:
            title = "YouTube 요약 (제목 없음)"
            content = summary

        desc = f"스크립트길이 {len(script)}자, 요약길이 {len(summary)}자"
        result = post_to_blog(title, content, url)
        db.upsert_videos(video_id=video_id, is_posted=result, title=title, should_retry=False, description=desc)
        return result
    except Exception as e:
            db.upsert_videos(video_id=video_id, is_posted=False, error_message=str(e), title=title, should_retry=False)
            logging.error(f"process_single_video : {e}")
    return False
    
def process_in_batches(url_list, batch_size=3):
    all_results = []
    for i in range(0, len(url_list), batch_size):
        batch = url_list[i : i + batch_size]
        logging.info(f"현재 배치 처리 중: {batch}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = [executor.submit(process_single_video, url) for url in batch]
            batch_results = [f.result() for f in concurrent.futures.as_completed(futures)]
            all_results.extend(batch_results)
        
        if i + batch_size < len(url_list):
            logging.info("1분 대기 시작...")
            time.sleep(60)
    return all_results

def main():
    # 죄회 결과를 DB에 Insert하고 불러오기.
    get_videos_from_list() 
    video_ids = db.get_video_list()
    url_list = []
    for video_id in video_ids:
        url_list.append(f"https://www.youtube.com/watch?v={video_id}")

    # 배치 처리 호출 수정
    batch_results = process_in_batches(url_list, batch_size=3)
    
    success_cnt = sum(1 for r in batch_results if r)
    fail_cnt = len(url_list) - success_cnt

    msg = f"유튜브 요약 완료: 성공 {success_cnt}, 실패 {fail_cnt}"
    logging.info(msg)
    asyncio.run(send_telegram_alert(msg))
    
if __name__ == "__main__":
    main()