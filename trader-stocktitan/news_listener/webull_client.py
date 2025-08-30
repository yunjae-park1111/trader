import pandas as pd
from datetime import datetime, timedelta
from webull import webull
from .config import logger, WB_EMAIL, WB_PASSWORD, WB_TRADE_PIN
from .telegram_notifier import send_error_notification

# webull 초기화
wb = webull()

def initialize_webull():
    """Webull 클라이언트를 초기화하고 로그인합니다."""
    try:
        if WB_EMAIL and WB_PASSWORD:
            wb.login(WB_EMAIL, WB_PASSWORD)
            if WB_TRADE_PIN:
                wb.get_trade_token(WB_TRADE_PIN)
            logger.info("✅ Webull 로그인 성공")
            return True
        else:
            logger.warning("⚠️ Webull 로그인 정보 없음 - 더미 데이터 사용")
            return False
    except Exception as e:
        error_msg = f"Webull 로그인 실패: {e}"
        logger.error(f"❌ {error_msg}")
        send_error_notification("Webull 로그인 실패", error_msg)
        return False

def get_historical_data(symbol: str, minutes: int = 60) -> dict:
    """webull 라이브러리로 과거 60분 히스토리 데이터를 수집합니다."""
    try:
        if WB_EMAIL and WB_PASSWORD:
            # 현재 시간 기준 60분 전부터 1분 단위 데이터 가져오기
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=minutes)
            
            # get_bars로 1분봉 데이터 가져오기
            bars = wb.get_bars(stock=symbol, interval='m1', count=minutes)
            
            if bars is not None and not bars.empty:
                price_data = []
                volume_data = []
                
                # DataFrame 인덱스로 순회
                for idx, row in bars.iterrows():
                    price_data.append(row['close'] if 'close' in row else None)
                    volume_data.append(row['volume'] if 'volume' in row else None)
                
                return {
                    'prices': price_data,
                    'volumes': volume_data,
                    'timestamp': datetime.now()
                }
        else:
            # 로그인 정보가 없으면 더미 데이터 반환
            logger.warning(f"⚠️ Webull 로그인 정보 없음 - {symbol} 더미 데이터 사용")
            return {
                'prices': [None] * minutes,  # 더미 가격
                'volumes': [None] * minutes,  # 더미 볼륨
                'timestamp': datetime.now()
            }
    except Exception as e:
        error_msg = f"Webull 히스토리 데이터 오류 ({symbol}): {e}"
        logger.error(f"❌ {error_msg}")
        send_error_notification("Webull 히스토리 데이터 오류", error_msg, symbol)
    
    # 에러 발생 시 더미 데이터 반환
    return {
        'prices': [None] * minutes,
        'volumes': [None] * minutes,
        'timestamp': datetime.now()
    }

def get_realtime_data(symbol: str) -> dict:
    """webull 라이브러리로 실시간 주식 데이터를 수집합니다."""
    try:
        if WB_EMAIL and WB_PASSWORD:
            quote = wb.get_quote(symbol)
            if quote:
                return {
                    'price': quote.get('close', 0),
                    'volume': quote.get('volume', 0),
                    'timestamp': datetime.now()
                }
        else:
            # 로그인 정보가 없으면 더미 데이터 반환
            logger.warning(f"⚠️ Webull 로그인 정보 없음 - {symbol} 더미 데이터 사용")
            return {
                'price': None,  # 더미 가격
                'volume': None,  # 더미 볼륨
                'timestamp': datetime.now()
            }
    except Exception as e:
        error_msg = f"Webull 실시간 데이터 오류 ({symbol}): {e}"
        logger.error(f"❌ {error_msg}")
        send_error_notification("Webull 실시간 데이터 오류", error_msg, symbol)
    
    # 에러 발생 시 더미 데이터 반환
    return {'price': 0, 'volume': 0, 'timestamp': datetime.now()}
