"""
News Listener Package

실시간 뉴스 수신 및 주가 분석을 위한 패키지
"""

from .config import (
    logger, 
    SAVE_DIR,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    WB_EMAIL,
    WB_PASSWORD,
    WB_TRADE_PIN,
    OPENAI_API_KEY,
    GPT_MODEL,
    generate_columns
)

from .llm_analyzer import (
    analyze_news_with_gpt,
    predict_price_with_gpt,
    analyze_prediction_accuracy_with_gpt,
    analyze_price_movement_with_gpt
)

from .webull_client import (
    initialize_webull,
    get_historical_data,
    get_realtime_data
)

from .telegram_notifier import (
    send_error_notification,
    send_final_result_notification,
    send_monitoring_completion_notification,
    send_historical_analysis_notification
)

from .price_monitor import (
    monitor_price_thread,
    update_csv_with_price_data,
    start_monitoring_threads
)

from .news_handler import (
    handle_news
)

__version__ = "1.0.0"
__author__ = "News Listener Team"

__all__ = [
    # Config
    "logger",
    "SAVE_DIR", 
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "WB_EMAIL", 
    "WB_PASSWORD",
    "WB_TRADE_PIN",
    "OPENAI_API_KEY",
    "GPT_MODEL",
    "generate_columns",
    
    # LLM Analyzer
    "analyze_news_with_gpt",
    "predict_price_with_gpt", 
    "analyze_prediction_accuracy_with_gpt",
    "analyze_price_movement_with_gpt",
    
    # Webull Client
    "initialize_webull",
    "get_historical_data",
    "get_realtime_data",
    
    # Telegram Notifier
    "send_error_notification",
    "send_final_result_notification", 
    "send_monitoring_completion_notification",
    "send_historical_analysis_notification",
    
    # Price Monitor
    "monitor_price_thread",
    "update_csv_with_price_data",
    "start_monitoring_threads",
    
    # News Handler
    "handle_news"
]
