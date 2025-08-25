import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from news_listener import (
    logger,
    SAVE_DIR,
    initialize_webull,
    handle_news,
    send_error_notification,
    config
)

def main():
    """
    메인 실행 함수
    """
    # Webull 초기화
    initialize_webull()
    logger.info(f"STOCKTITAN_EMAIL: {config.STOCKTITAN_EMAIL}")
    logger.info(f"STOCKTITAN_PASSWORD: {config.STOCKTITAN_PASSWORD}")
    logger.info(f"STOCKTITAN_NAME: {config.STOCKTITAN_NAME}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # WebSocket 후킹 스크립트 삽입
        page.add_init_script("""
            (function() {
                const OriginalWebSocket = window.WebSocket;
                window.WebSocket = function(...args) {
                    const ws = new OriginalWebSocket(...args);
                    ws.addEventListener('message', event => {
                        console.log("[WS MESSAGE]", event.data);
                    });
                    return ws;
                }
            })();
        """)

        # 콘솔 로그 감지 → 뉴스만 추출
        def handle_console(msg):
            txt = msg.text
            if txt.startswith("[WS MESSAGE]"):
                try:
                    raw_json = txt.replace("[WS MESSAGE]", "").strip()
                    data = json.loads(raw_json)
                    if data.get("header", {}).get("type") == "ping":
                        payload = data.get("payload", {})
                        k_value = payload.get("k", "")
                        logger.info(f"뉴스 대기 중... {k_value} {datetime.now()}")
                    elif data.get("header", {}).get("type") == "news":
                        filepath = handle_news(data, SAVE_DIR)
                        logger.info(f"🔍 뉴스 처리 결과: {filepath}")
                    else:
                        error_msg = f"처리되지 않은 응답 타입: {data.get('header', {}).get('type', 'unknown')}"
                        logger.error(f"⚠️ {error_msg}")
                        send_error_notification("알 수 없는 메시지 타입", f"{error_msg}\n\n전체 데이터: {str(data)}...")
                except Exception as e:
                    error_msg = f"JSON 파싱 오류: {e}"
                    logger.error(f"❌ {error_msg}")
                    send_error_notification("JSON 파싱 오류", error_msg)

        page.on("console", handle_console)

        # 접속 및 클릭 흐름
        page.goto("https://www.stocktitan.net/")
        
        # 페이지 로드 완료 대기
        logger.info("🌐 메인 페이지 접속 중...")
        page.wait_for_load_state('load', timeout=10000)
        logger.info("🌐 메인 페이지 접속 완료")
        time.sleep(1)
        
        if config.STOCKTITAN_EMAIL and config.STOCKTITAN_PASSWORD:
            logger.info("🌐 로그인 중...")
            
            # Login 버튼이 나타날 때까지 대기 (정확한 선택자 사용)
            page.wait_for_selector('a[data-bs-target="#login-modal"]', timeout=10000)
            page.click('a[data-bs-target="#login-modal"]')
            logger.info("✅ Login 버튼 클릭 완료")
            
            # 로그인 모달이 나타날 때까지 대기
            page.wait_for_selector('#login-modal', timeout=10000)
            logger.info("✅ 로그인 모달 나타남")
            time.sleep(1)

            # 이메일 입력 필드가 나타날 때까지 대기
            page.wait_for_selector("input[name='email']", timeout=10000)
            page.fill("input[name='email']", config.STOCKTITAN_EMAIL)
            logger.info("✅ 이메일 입력 완료")
            
            # 패스워드 입력 필드가 나타날 때까지 대기
            page.wait_for_selector("input[name='password']", timeout=10000)
            page.fill("input[name='password']", config.STOCKTITAN_PASSWORD)
            logger.info("✅ 패스워드 입력 완료")
            
            # 로그인 제출 버튼이 나타날 때까지 대기
            page.wait_for_selector("button#login-submit", timeout=10000)
            page.click("button#login-submit")
            logger.info("✅ 로그인 제출 버튼 클릭 완료")
            
            # 로그인 성공 확인 (닉네임이 나타나는지 체크)
            try:
                page.wait_for_load_state('load', timeout=10000)
                time.sleep(1)

                page.wait_for_selector(f"text={config.STOCKTITAN_NAME}", timeout=10000)
                logger.info(f"✅ 로그인 성공: {config.STOCKTITAN_NAME}")
            except:
                logger.error("❌ 로그인 실패 - 닉네임을 찾을 수 없습니다")
                send_error_notification("StockTitan 로그인 실패", f"닉네임 '{config.STOCKTITAN_NAME}'을 찾을 수 없습니다.")
        else:
            logger.info("⚠️ StockTitan 로그인 정보 없음 - 게스트로 진행")

        page.wait_for_load_state('load', timeout=10000)
        time.sleep(1)

        # NEWS FEED 버튼이 나타날 때까지 대기
        page.wait_for_selector("text=NEWS FEED", timeout=15000)
        page.click("text=NEWS FEED")
        logger.info("✅ NEWS FEED 클릭 완료")

        page.wait_for_load_state('load', timeout=10000)
        time.sleep(1)
        
        # 드롭다운 메뉴가 나타날 때까지 대기
        page.wait_for_selector("a.dropdown-item[href='/news/live.html']", timeout=10000)
        page.click("a.dropdown-item[href='/news/live.html']")
        logger.info("🌐 실시간 뉴스 수신 페이지 이동 중...")

        page.wait_for_load_state('load', timeout=10000)
        time.sleep(1)

        logger.info("🌐 실시간 뉴스 수신 페이지 이동 완료")
        logger.info("🌐 실시간 뉴스 수신 중...")

        while True:
            page.wait_for_timeout(1000)

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
