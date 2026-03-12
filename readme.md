# YouTube to Blogger Auto-Poster

author : jiyongcor ( g-m-a-i_l )

This project is an automation bot designed to monitor the latest videos from specified YouTube channels, extract their transcripts, summarize the content, and automatically post it to Google Blogger.

## Key Features
- Automated Monitoring: Checks for new videos from YouTube channels registered in the database on a daily basis.
- Transcript Extraction & Summarization: Automatically extracts transcripts using youtube-transcript-api and summarizes content.
- Automated Posting: Automatically uploads summarized content as blog posts via the Google Blogger API.
- Database-Driven Management: Uses a centralized database (Supabase) to securely manage channel information and API authentication tokens.

## Tech Stack
- Language: Python
- Database: Supabase (PostgreSQL)
- APIs: YouTube Data API v3, Google Blogger API v3
- Authentication: OAuth 2.0 (with automated token refresh support)

## Core Logic
- Channel Retrieval: Fetches channel IDs and playlist information from Supabase.
- Video Collection: Lists video URLs uploaded within a specific timeframe via the YouTube API.
- Transcript Extraction: Retrieves transcripts based on the video ID.
- Blog Posting: Generates a blog post containing the summarized content and a link to the original video source.

## Setup Instructions (Brief)
- Create a .env file and configure the necessary environment variables (e.g., SUPABASE_URL, SUPABASE_KEY).
- Create the required Supabase tables (refer to resources/query.txt).
- Complete OAuth 2.0 authentication and store the GOOGLE_BLOGGER_TOKEN in the database.
- Run the script to initiate the automation pipeline.

summary-tube/
├── app.py                # [UI] Streamlit interface (user interaction)
├── main.py               # [Controller] Workflow management and scheduling
├── core/
│   ├── __init__.py
│   ├── youtube_api.py    # YouTube integration (video info, transcript extraction)
│   ├── gemini_api.py     # AI summarization logic
│   ├── blog_api.py       # Blog posting integration
│   └── telegram_api.py   # Telegram notification service
└── utils/
    ├── __init__.py
    └── db.py             # Database connectivity and helpers