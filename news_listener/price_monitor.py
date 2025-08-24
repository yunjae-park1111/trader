import csv
import time
import threading
from .config import logger
from .webull_client import get_historical_data, get_realtime_data
from .telegram_notifier import send_error_notification, send_historical_analysis_notification, send_final_result_notification

def monitor_price_thread(symbol: str, filepath: str, before: bool = True):
    """
    가격 모니터링 스레드 함수
    """
    try:
        logger.info(f"🔍 가격 모니터링 스레드 시작: {symbol}")
        
        if before:
            # 과거 60분 히스토리 데이터 한번에 가져오기
            logger.info(f"🔍 뉴스 발생 전 60분 데이터 수집 시작: {symbol}")
            historical_data = get_historical_data(symbol, 60)
            
            price_data = {
                'pct': historical_data['prices'],
                'volume': historical_data['volumes']
            }
            
            logger.info(f"✅ 과거 60분 데이터 수집 완료: {symbol} ({len(price_data['pct'])}개)")
            
        else:
            # 뉴스 발생 후 60분 동안 1분마다 실시간 데이터 수집
            logger.info(f"🔍 뉴스 발생 후 60분 데이터 수집 시작: {symbol}")
            price_data = {'pct': [], 'volume': []}
            
            for i in range(1, 61):  # 1분부터 60분까지
                data = get_realtime_data(symbol)
                price_data['pct'].append(data['price'])
                price_data['volume'].append(data['volume'])
                logger.info(f"📊 {i}분차 {symbol} 실시간 데이터: 가격={data['price']}, 볼륨={data['volume']}")
                
                time.sleep(60)  # 실제 1분 대기
        
        update_csv_with_price_data(filepath, price_data, before=before)
        
        if before:
            completion_msg = f"뉴스 발생 전 60분 데이터 업데이트 완료: {symbol}"
            logger.info(f"✅ {completion_msg}")
            
            # 과거 데이터 분석 및 가격 예측 알림
            send_historical_analysis_notification(symbol, price_data['pct'], price_data['volume'], filepath)
        else:
            completion_msg = f"뉴스 발생 후 60분 데이터 수집 완료: {symbol}"
            logger.info(f"✅ {completion_msg}")
            
            # 60분 후 결과 비교 분석 알림
            send_final_result_notification(symbol, price_data['pct'], price_data['volume'], filepath)
        
    except Exception as e:
        error_msg = f"모니터링 오류 ({symbol}): {e}"
        logger.error(f"❌ {error_msg}")
        send_error_notification("모니터링 오류", error_msg, symbol)

def update_csv_with_price_data(filepath: str, price_data: dict, before: bool = True):
    """
    CSV 파일에 가격 데이터를 업데이트합니다.
    """
    try:
        logger.info("🔍 가격 데이터 업데이트 시작")
        # 기존 파일 읽기
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        if len(rows) >= 2:
            # 가격 데이터 업데이트
            data_row = rows[1]
            # pct_m60~m1, volume_m60~m1, pct_p1~p60, volume_p1~p60 순서로 업데이트
            start_idx = 4  # symbol, market_cap, news_flag, llm_rating 다음부터

            if before:
                # 이전 60분 데이터
                for i in range(60):
                    data_row[start_idx + i] = price_data['pct'][i]
                    data_row[start_idx + 60 + i] = price_data['volume'][i]
            else:
                # 이후 60분 데이터  
                for i in range(60):
                    data_row[start_idx + 120 + i] = price_data['pct'][i]
                    data_row[start_idx + 180 + i] = price_data['volume'][i]
            
            # 파일 다시 쓰기
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
                
    except Exception as e:
        error_msg = f"CSV 업데이트 오류: {e}"
        logger.error(f"❌ {error_msg}")
        send_error_notification("CSV 업데이트 오류", error_msg)

def start_monitoring_threads(symbol: str, filepath: str):
    """
    가격 모니터링 스레드들을 시작합니다.
    """
    try:
        # 과거 60분 데이터 수집 스레드 (즉시 실행)
        monitor_thread_before = threading.Thread(
            target=monitor_price_thread,
            args=(symbol, filepath, True),  # before=True
            daemon=False
        )
        monitor_thread_before.start()

        # 미래 60분 데이터 수집 스레드 (백그라운드에서 계속 실행)
        monitor_thread_after = threading.Thread(
            target=monitor_price_thread,
            args=(symbol, filepath, False),  # before=False
            daemon=False
        )
        monitor_thread_after.start()
        
        logger.info(f"✅ 모니터링 스레드 시작 완료: {symbol}")
        
    except Exception as e:
        error_msg = f"모니터링 스레드 시작 오류 ({symbol}): {e}"
        logger.error(f"❌ {error_msg}")
        send_error_notification("모니터링 스레드 오류", error_msg, symbol)
