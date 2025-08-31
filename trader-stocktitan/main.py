import json
import time
import websocket
from datetime import datetime, timedelta
from news_listener import (
    logger,
    SAVE_DIR,
    handle_news,
    send_error_notification,
    initialize_webull
)

# 글로벌 변수로 마지막 메시지 시간 기록
last_message_time = None

def on_message(ws, message):
    """웹소켓 메시지 수신 처리"""
    global last_message_time
    
    try:
        data = json.loads(message)
        message_type = data.get("header", {}).get("type", "unknown")
        
        if message_type == "ping":
            # 핑퐁 수신 시 시간 기록
            last_message_time = datetime.now()
            payload = data.get("payload", {})
            k_value = payload.get("k", "")
            logger.info(f"🔄 핑퐁 수신... {k_value} {datetime.now().strftime('%H:%M:%S')}")
            
        elif message_type == "news":
            # 뉴스 수신 시 시간 기록
            last_message_time = datetime.now()
            
            # 뉴스 필터링
            payload = data.get("payload", {})
            
            # OTC 제외 필터링
            exchanges = payload.get("exchanges", [])
            if "OTC" in exchanges:
                logger.info(f"🚫 OTC 뉴스 필터링됨: {payload.get('title', 'Unknown')}")
                return
            
            # 임팩트 & 감정분석 스코어 필터링 (둘 다 2점 이하일 때만 제외)
            impact_score = payload.get("impact_score", 0)
            sentiment_score = payload.get("sentiment_score", 0)
            if impact_score <= 2 and sentiment_score <= 2:
                logger.info(f"🚫 낮은 품질 뉴스 필터링됨 (임팩트: {impact_score}, 감정: {sentiment_score}): {payload.get('title', 'Unknown')}")
                return
            
            # 필터링 통과한 뉴스만 처리
            filepath = handle_news(data, SAVE_DIR)
            logger.info(f"📰 뉴스 처리 완료 (임팩트: {impact_score}, 감정: {sentiment_score}): {filepath}")
            
        else:
            error_msg = f"알 수 없는 메시지 타입: {message_type}"
            logger.error(f"❌ {error_msg}")
            send_error_notification("알 수 없는 메시지 타입", f"{error_msg}\n\n전체 데이터: {str(data)[:500]}...")
            
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON 파싱 실패: {e}")
    except Exception as e:
        logger.error(f"❌ 메시지 처리 오류: {e}")
        send_error_notification("메시지 처리 오류", str(e))

def on_error(ws, error):
    """웹소켓 에러 처리"""
    logger.error(f"🔌 WebSocket 에러: {error}")
    send_error_notification("WebSocket 에러", str(error))

def on_close(ws, close_status_code, close_msg):
    """웹소켓 연결 종료 처리"""
    logger.error("🔌 WebSocket 연결 끊어짐")
    send_error_notification("WebSocket 연결 끊어짐", f"코드: {close_status_code}, 메시지: {close_msg}")

def on_open(ws):
    """웹소켓 연결 성공 처리"""
    global last_message_time
    last_message_time = datetime.now()
    logger.info("🔌 WebSocket 연결 성공")

def main():
    """
    메인 실행 함수
    """
    global last_message_time
    
    logger.info("🚀 StockTitan 웹소켓 리스너 시작")
    
    # Webull 초기화
    initialize_webull()
    
    # 웹소켓 연결
    websocket_url = "wss://ws1.stocktitan.net:9011/"
    
    logger.info(f"🔌 웹소켓 연결 시도: {websocket_url}")
    
    # 웹소켓 클라이언트 생성
    ws = websocket.WebSocketApp(
        websocket_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # 연결 시작
    ws.run_forever()

def run_with_auto_restart():
    """
    자동 재시작 기능이 있는 메인 실행 함수
    """
    restart_count = 0
    max_restarts = 10  # 최대 재시작 횟수
    
    while restart_count < max_restarts:
        try:
            logger.info(f"🚀 뉴스 리스너 시작 (재시작 횟수: {restart_count})")
            
            # 재시작 알림 (첫 시작이 아닌 경우)
            if restart_count > 0:
                send_error_notification(
                    "시스템 재시작", 
                    f"뉴스 리스너가 자동으로 재시작되었습니다. (재시작 횟수: {restart_count})"
                )
            
            main()
            
        except KeyboardInterrupt:
            logger.info("👋 사용자에 의해 종료됨")
            send_error_notification("시스템 종료", "사용자에 의해 뉴스 리스너가 종료되었습니다.")
            break
            
        except Exception as e:
            restart_count += 1
            error_msg = f"메인 프로세스 오류: {e}"
            logger.error(f"❌ {error_msg}")
            send_error_notification("메인 프로세스 오류", f"{error_msg}\n\n{restart_count}/{max_restarts} 재시작 시도 중...")
            
            if restart_count < max_restarts:
                logger.info("⏰ 10초 후 재시작...")
                time.sleep(10)
            else:
                logger.error(f"❌ 최대 재시작 횟수({max_restarts}) 초과. 프로그램 종료.")
                send_error_notification(
                    "시스템 완전 종료", 
                    f"최대 재시작 횟수({max_restarts})를 초과하여 뉴스 리스너가 완전히 종료되었습니다."
                )
                break

if __name__ == "__main__":
    run_with_auto_restart()