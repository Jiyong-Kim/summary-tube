import streamlit as st
import logging
import asyncio
from core.youtube import get_videos_from_list
from main import extract_id, main, process_in_batches
from core.telegram import send_telegram_alert
from utils import db

st.title("🚀 Summary Youtube")

# --- 상태 초기화 ---
if 'url_text' not in st.session_state:
    st.session_state.url_text = ""

# --- UI 레이아웃 ---
input_urls = st.text_area(
    label="유튜브 URL 입력", 
    value=st.session_state.url_text,
    height=150,
    key="input_area"
)

if st.button("구독자 최신 영상 수집"):
    today_list = get_videos_from_list()
    # 기존 입력값과 합쳐서 중복 제거
    current_list = input_urls.splitlines()
    combined = list(dict.fromkeys(today_list + current_list))
    st.session_state.url_text = "\n".join([url for url in combined if url.strip()])
    st.rerun()

if st.button("작업 시작"):
    video_urls = [u.strip() for u in input_urls.splitlines() if u.strip()]
    url_list = []
    skip_cnt = 0
   
    for url in video_urls:
        video_id = extract_id(url)
        if video_id and db.is_video_unprocessed(video_id):
            url_list.append(url)
        else:
            skip_cnt += 1

    if not url_list:
        st.warning("처리할 새로운 영상이 없습니다.")
    else:
        with st.spinner("영상 요약 및 게시 중... (배치 처리)"):
            batch_results = process_in_batches(url_list, batch_size=3)
            
            success_cnt = sum(1 for r in batch_results if r)
            fail_cnt = len(url_list) - success_cnt

            msg = f"유튜브 요약 완료: 성공 {success_cnt}, 실패 {fail_cnt}, 건너뛰기 {skip_cnt}"
            logging.info(msg)
            
            # 알림 발송
            asyncio.run(send_telegram_alert(msg))
            st.success(msg)

if st.button("메인테스트"):
    main()
    st.rerun()