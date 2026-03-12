-- 1. 채널 테이블
CREATE TABLE IF NOT EXISTS ys_channels (
    channel_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    uploads_playlist_id TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. 비디오 테이블 (이름을 명확히 정의)
CREATE TABLE IF NOT EXISTS ys_videos (
    id SERIAL PRIMARY KEY,
    channel_id TEXT,
    video_id TEXT NOT NULL,
    title TEXT,
    --summary TEXT,
    is_posted BOOLEAN DEFAULT FALSE, 
    should_retry BOOLEAN DEFAULT FALSE, 
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. 코드(공통 코드) 테이블
CREATE TABLE IF NOT EXISTS ys_codes (
    code VARCHAR(24),
    value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);