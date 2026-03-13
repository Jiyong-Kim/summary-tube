import os
import logging
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
from datetime import datetime, timezone

_supabase: Optional[Client] = None
_secrets_cache: Dict[str, str] = {}


def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        _supabase = create_client(url, key)

    return _supabase


def get_code(code: str) -> Optional[str]:
    # 1. 캐시 확인
    if code in _secrets_cache:
        return _secrets_cache[code]

    logging.info(f"code : {code}")
    try:
        supabase = get_supabase()
        response = supabase.table("ys_codes").select("value").eq("code", code).execute()

        # 데이터가 있는지 확인
        if response.data and len(response.data) > 0:
            _secrets_cache[code] = response.data[0].get("value")  # 캐시에 저장
            return response.data[0].get("value")
        return None

    except Exception as e:
        logging.error(f"Supabase 조회 중 오류 발생: {e}")
        return None


def update_code(code_key, value):
    """
    DB의 ys_codes 테이블에서 code_key에 해당하는 value를 업데이트합니다.
    데이터가 없으면 새로 삽입합니다.
    """
    try:
        # 데이터 업데이트/삽입 (Upsert)
        supabase = get_supabase()
        response = (
            supabase.table("ys_codes")
            .upsert({"code": code_key, "value": value})
            .execute()
        )

        # 캐시도 함께 업데이트하여 정합성 유지
        _secrets_cache[code_key] = value

        return response
    except Exception as e:
        logging.error(f"DB 업데이트 오류 (코드: {code_key}): {e}")
        return None


def get_channels():
    supabase = get_supabase()
    response = (
        supabase.table("ys_channels")
        .select("channel_id, uploads_playlist_id")
        .execute()
    )
    return response.data


def update_channel_uploads_id(channel_id, uploads_id, channel_title):
    try:
        supabase = get_supabase()
        response = (
            supabase.table("ys_channels")
            .update({"uploads_playlist_id": uploads_id, "name": channel_title})
            .eq("channel_id", channel_id)
            .execute()
        )

        # 성공 여부 확인
        if response.data:
            print(f"Successfully updated channel: {channel_id}")
        return response
    except Exception as e:
        logging.error(f"Failed to update channel {channel_id}: {e}")
        return None


def is_video_exists(video_id: str) -> bool:
    try:
        supabase = get_supabase()
        response = (
            supabase.table("ys_videos")
            .select("video_id")
            .eq("video_id", video_id)
            .execute()
        )
        return response.data is not None and len(response.data) > 0
    except Exception as e:
        logging.error(f"비디오 존재 여부 확인 오류 (ID: {video_id}): {e}")
        return False


def is_video_unprocessed(video_id: str) -> bool:
    try:
        supabase = get_supabase()
        response = (
            supabase.table("ys_videos")
            .select("video_id")
            .eq("video_id", video_id)
            .eq("should_retry", True)
            .execute()
        )

        return response.data is not None and len(response.data) > 0
    except Exception as e:
        logging.error(f"미처리 비디오 확인 오류 (ID: {video_id}): {e}")
        return False


def get_video_list() -> List[str]:
    try:
        supabase = get_supabase()
        response = (
            supabase.table("ys_videos")
            .select("video_id")
            .eq("should_retry", True)
            .execute()
        )
        # response.data에서 video_id 값만 바로 추출
        return [item["video_id"] for item in response.data] if response.data else []

    except Exception as e:
        logging.error(f"재시도 비디오 ID 조회 중 오류 발생: {e}")
        return []


def upsert_videos(
                video_id: str,
                is_posted: bool,
                error_message: str = None,
                title: str = None,
                channel_id: str = None,
                should_retry: bool = None,
                description: str = None
            ):
    try:
        supabase = get_supabase()
        logging.info(f"video_id: {video_id}")
        # 2. 업데이트할 데이터 구성
        data_to_upsert = {
            "video_id": video_id,
            "is_posted": is_posted,
            "title": title,
            "should_retry": should_retry,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "description": description
        }

        if is_posted:
            data_to_upsert.update({"error_message": None})
        else:
            data_to_upsert.update({"error_message": error_message})

        if channel_id:
            data_to_upsert.update(
                {"channel_id": channel_id, "should_retry": should_retry}
            )

        # 3. Upsert 실행
        response = supabase.table("ys_videos").upsert(data_to_upsert).execute()
        return response

    except Exception as e:
        logging.error(f"비디오 상태 업데이트 중 오류 발생 (ID: {video_id}): {e}")
        return None
