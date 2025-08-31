import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import pathlib

# .env 파일 경로 명시적 설정
project_root = pathlib.Path(__file__).parent.parent
env_path = project_root / ".env"

# .env 파일 로드
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"✅ .env 파일 로드 완료: {env_path}")
else:
    print(f"⚠️ .env 파일이 없습니다: {env_path}")
    load_dotenv()  # 시스템 환경변수만 사용

# 저장 경로 설정
SAVE_DIR = "news_data_browser"
os.makedirs(SAVE_DIR, exist_ok=True)

# 로깅 설정
LOG_LEVEL = os.getenv("LOG_LEVEL")
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

# Webull 설정
WB_EMAIL = os.getenv("WB_EMAIL")
WB_PASSWORD = os.getenv("WB_PASSWORD")
WB_TRADE_PIN = os.getenv("WB_TRADE_PIN")

# 텔레그램 봇 설정 (일반 알림용)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 텔레그램 봇 설정 (에러 전용)
TELEGRAM_ERROR_BOT_TOKEN = os.getenv("TELEGRAM_ERROR_BOT_TOKEN")
TELEGRAM_ERROR_CHAT_ID = os.getenv("TELEGRAM_ERROR_CHAT_ID")

# OpenAI 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GPT_MODEL = os.getenv("GPT_MODEL")

# Stocktitan 설정
STOCKTITAN_EMAIL = os.getenv("STOCKTITAN_EMAIL")
STOCKTITAN_PASSWORD = os.getenv("STOCKTITAN_PASSWORD")
STOCKTITAN_NAME = os.getenv("STOCKTITAN_NAME")

# 컬럼명 구성 함수
def generate_columns():
    """CSV 파일의 컬럼명을 생성합니다."""
    cols = ["symbol", "market_cap", "news_flag", "llm_rating"]
    cols += [f"pct_m{m}" for m in range(60, 0, -1)]
    cols += [f"volume_m{m}" for m in range(60, 0, -1)]
    cols += [f"pct_p{m}" for m in range(1, 61)]
    cols += [f"volume_p{m}" for m in range(1, 61)]
    return cols
