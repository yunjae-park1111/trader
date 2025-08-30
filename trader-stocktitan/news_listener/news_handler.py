import csv
import json
from datetime import datetime
from .config import logger, generate_columns
from .llm_analyzer import analyze_news_with_gpt
from .price_monitor import start_monitoring_threads
from .telegram_notifier import send_error_notification

def handle_news(data: dict, save_dir: str) -> str:
    """
    뉴스 데이터 수신 → CSV 저장 및 스레드 시작
    """
    try:
        news = data["payload"]["news"]
        stock = data["payload"].get("stock", {})

        symbol = news.get("symbol", "")
        timestamp = datetime.fromtimestamp(news["timestamp"] / 1000)
        file_ts = timestamp.strftime("%Y-%m-%d_%H-%M")
        filename = f"{symbol}_{file_ts}.csv"
        filepath = f"{save_dir}/{filename}"

        market_cap = stock.get("marketCap", "")
        
        # GPT로 뉴스 분석
        logger.info(f"🤖 GPT 분석 시작: {symbol}")
        llm_result = analyze_news_with_gpt(news)
        
        # 분석 결과 로깅
        logger.info(f"📊 분석 결과 - {symbol}: 평점={llm_result['rating']}, 감성={llm_result['sentiment']}")
        logger.info(f"💬 분석 내용: {llm_result['analysis'][:100]}...")
        
        # CSV에 저장할 데이터 (기존 sentiment_score 대신 GPT rating 사용)
        sentiment_score = llm_result['rating']

        row = [symbol, market_cap, 1, sentiment_score]
        row += [""] * (60 * 2 + 60 * 2)

        # CSV 파일 생성
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(generate_columns())
            writer.writerow(row)
        
        # 분석 결과를 별도 JSON 파일로도 저장
        analysis_filename = f"{symbol}_{file_ts}_analysis.json"
        analysis_filepath = f"{save_dir}/{analysis_filename}"
        
        analysis_data = {
            "symbol": symbol,
            "timestamp": timestamp.isoformat(),
            "news": news,
            "llm_analysis": llm_result,
            "market_cap": market_cap
        }
        
        with open(analysis_filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 분석 결과 저장: {analysis_filename}")
        logger.info(f"[📰 저장 완료] {filename}")
        logger.info(f"⏳ 과거 60분 데이터 분석 후 알림 예정: {symbol}")

        # 가격 모니터링 스레드 시작
        start_monitoring_threads(symbol, filepath)

        return filepath

    except Exception as e:
        error_msg = f"뉴스 처리 오류: {e}"
        logger.error(f"❌ {error_msg}")
        send_error_notification("뉴스 처리 오류", error_msg)
        return None
