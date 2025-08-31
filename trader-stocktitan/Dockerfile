FROM python:3.9-slim

# 메타데이터
LABEL maintainer="News Listener Team" \
      description="Real-time news analysis system with GPT" \
      version="1.0.0"

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libgtk-4-1 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright 브라우저 설치
RUN playwright install chromium

# 소스 코드 복사
COPY main.py .
COPY news_listener/ ./news_listener/

# 데이터 저장용 디렉토리 생성
RUN mkdir -p news_data_browser

# 볼륨 마운트 포인트
VOLUME ["/app/news_data_browser"]

# 환경변수 기본값 설정 (실제 배포시 값 변경 필요)
ENV TZ=Asia/Seoul
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO
ENV GPT_MODEL=gpt-5
ENV OPENAI_API_KEY=your-openai-api-key-here
ENV WB_EMAIL=your-webull-email@example.com
ENV WB_PASSWORD=your-webull-password
ENV TELEGRAM_BOT_TOKEN=your-telegram-bot-token
ENV TELEGRAM_CHAT_ID=your-telegram-chat-id
ENV TELEGRAM_ERROR_BOT_TOKEN=your-error-telegram-bot-token
ENV TELEGRAM_ERROR_CHAT_ID=your-error-telegram-chat-id
ENV STOCKTITAN_EMAIL=your-email@example.com
ENV STOCKTITAN_PASSWORD=your-password
ENV STOCKTITAN_NAME=your-display-name
#ENV WB_TRADE_PIN=123456

# 기본 실행 명령어
CMD ["python", "main.py"]

# Docker 빌드 및 푸시 명령어 예시:
# docker build -t ghcr.io/your-username/stocktitan-news-listener:latest --platform linux/arm64 --no-cache --push .
