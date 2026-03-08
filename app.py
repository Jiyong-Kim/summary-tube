import streamlit as st
import asyncio
import concurrent.futures

from logic import (
    get_transcript, summarize_with_gemini, get_today_videos_from_list, 
    post_to_blog, send_telegram_alert, process_single_video
)

st.title("🚀 Summary Youtube ")

# --- 상태 초기화 ---
if 'url_text' not in st.session_state:
    st.session_state.url_text = ""

# --- 콜백 함수 ---
def fetch_today_videos():
    today_list = get_today_videos_from_list()
    current_list = input_urls.splitlines() # 위젯으로부터 직접 읽기
    combined = list(dict.fromkeys(today_list + current_list))
    st.session_state.url_text = "\n".join([url for url in combined if url.strip()])
    st.rerun() # 위젯을 다시 그려서 값이 반영되게 함

# --- UI 레이아웃 ---
input_urls = st.text_area(
    label="유튜브 URL 입력", 
    value=st.session_state.get('url_text', ""),
    height=150
)

col1, col2 = st.columns(2)
with col1:
    if st.button("구독자 최신 영상 수집"):
        fetch_today_videos()
        st.rerun()

# --- 메인 작업 로직 ---
if st.button("작업 시작"):
    url_list = [u.strip() for u in input_urls.splitlines() if u.strip()]
    
    with st.spinner("병렬로 영상 요약 및 게시 중..."):
        # 최대 5개 영상까지 동시에 처리하도록 설정
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # 작업 예약
            futures = [executor.submit(process_single_video, url) for url in url_list]
            
            # 결과 취합
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
            
    success_cnt = sum(results)
    fail_cnt = len(results) - success_cnt
    
    asyncio.run(send_telegram_alert(f"유튜브 요약 완료: 성공 {success_cnt}, 실패 {fail_cnt}"))
    st.success("모든 작업이 완료되었습니다!")