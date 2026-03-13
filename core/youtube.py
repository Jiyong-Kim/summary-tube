import logging
import datetime

from dotenv import load_dotenv
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

from utils import db

def get_youtube_service():
    """YouTube API 클라이언트를 생성하여 반환합니다."""
    api_key = db.get_code("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY가 설정되지 않았습니다!")
    return build("youtube", "v3", developerKey=api_key)
    
def get_videos_from_list():
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    video_urls = []
    youtube = get_youtube_service()
    channels = db.get_channels()

    for channel in channels:
        try:
            uploads_id = channel["uploads_playlist_id"]
            channel_id = channel["channel_id"]
            
            # 1. uploads_id가 없다면 API로 구하고 DB 업데이트
            if not uploads_id:
                res = youtube.channels().list(id=channel_id, part="contentDetails,snippet").execute()
                if not res.get("items"): continue
                uploads_id = res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
                channel_title = res["items"][0]["snippet"]["title"]
                db.update_channel_uploads_id(channel_id, uploads_id, channel_title)
            
            # 2. 영상 정보 가져오기
            playlist_res = youtube.playlistItems().list(
                playlistId=uploads_id, part="snippet", maxResults=10
            ).execute()
            
            for item in playlist_res.get("items", []):
                if item["snippet"]["publishedAt"][:10] >= yesterday:
                    v_id = item["snippet"]["resourceId"]["videoId"]
                    video_urls.append(f"https://www.youtube.com/watch?v={v_id}")
                    print ( "item" + channel_id )
                    if not db.is_video_exists(v_id):
                        print ( "is_video_exists" + v_id )
                        db.upsert_videos(video_id=v_id, channel_id=channel_id, is_posted=False, should_retry=True)
                    
        except Exception as e:
            # 특정 채널에서 에러가 나도 다음 채널은 계속 처리하도록 로깅만 수행
            logging.error(f"Error processing channel {channel.get('name')}: {e}")
            continue
    return video_urls

def get_transcript(video_id):
    try:
        api = YouTubeTranscriptApi()
        srt = api.fetch(video_id=video_id, languages=['ko', 'en'])
        return " ".join([ent.text for ent in srt])
    except Exception as e:
        error_message = f"스크립트 추출 오류 ({video_id}): {e}"
        db.upsert_videos(video_id=video_id, is_posted=False, error_message=error_message, should_retry=False)
        logging.error(error_message)
        return None
