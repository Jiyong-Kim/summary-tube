# YouTube to Blogger Auto-Poster

 author : jiyongcor (ㅈ ㅣ ㅁ ㅔ 일)

이 프로젝트는 지정된 YouTube 채널들의 최신 영상을 자동으로 감시하고, 자막을 추출하여 Google Blogger에 자동으로 포스팅해 주는 자동화 봇입니다.

## 주요 기능
- **자동 감시:** DB에 등록된 YouTube 채널들의 신규 영상을 매일 체크합니다.
- **자막 요약:** `youtube-transcript-api`를 활용해 영상 자막을 자동으로 추출합니다.
- **자동 포스팅:** 추출된 내용을 Google Blogger API를 통해 블로그 글로 자동 업로드합니다.
- **데이터베이스 기반 관리:** DB를 사용하여 채널 정보 및 API 인증 토큰을 안전하게 중앙 관리합니다.

## 기술 스택
- **Language:** Python
- **Database:** Supabase (PostgreSQL)
- **API:** YouTube Data API v3, Google Blogger API v3
- **Authentication:** OAuth 2.0 (토큰 자동 갱신 지원)

## 핵심 로직
1. **채널 조회:** Supabase에서 채널 ID 및 플레이리스트 정보를 가져옵니다.
2. **영상 수집:** API를 통해 특정 기간동안 업로드된 영상 URL을 리스트업합니다.
3. **자막 추출:** 영상 ID를 기반으로 자막을 가져옵니다.
4. **블로그 게시:** 요약된 내용과 영상 출처 링크를 포함하여 블로그에 글을 생성합니다.

## 설정 방법 (간략)
1. `.env` 파일을 생성하여 필요한 환경 변수(`SUPABASE_URL`, `SUPABASE_KEY` 등)를 설정합니다.
2. Supabase 테이블(resources/query.txt)을 생성합니다.
3. OAuth 2.0 인증을 통해 `GOOGLE_BLOGGER_TOKEN`을 DB에 저장합니다.
4. 스크립트를 실행하여 자동화 파이프라인을 가동합니다.

# summary-tube/
# ├── app.py                # [UI] 스트림릿 화면 담당 (사용자 접점)
# ├── main.py               # [Controller] 전체 작업 흐름 및 스케줄링 담당
# ├── core/
# │   ├── __init__.py
# │   ├── youtube_api.py    # 유튜브 관련(영상 정보, 자막 추출)
# │   ├── gemini_api.py     # AI 요약 관련
# │   ├── blog_api.py       # 블로그 게시 관련
# │   └── telegram_api.py   # 텔레그램 알림 관련
# └── utils/
#     ├── __init__.py
#     └── db.py             # DB 관련
