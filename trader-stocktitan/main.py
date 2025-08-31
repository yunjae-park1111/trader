import json
import time
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from news_listener import (
    logger,
    SAVE_DIR,
    initialize_webull,
    handle_news,
    send_error_notification,
    config
)

# 글로벌 변수로 마지막 메시지 시간 기록
last_message_time = None

def main():
    """
    메인 실행 함수
    """
    # Webull 초기화
    initialize_webull()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--single-process',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-animations',
                '--disable-smooth-scrolling',
                '--disable-features=TranslateUI,BlinkGenPropertyTrees'
            ]
        )
        context = browser.new_context(
            # 라즈베리파이 성능에 맞는 타임아웃 설정
            viewport={'width': 1920, 'height': 1080},
            # 추가 안정성을 위한 설정
            accept_downloads=False,
            ignore_https_errors=True
        )
        page = context.new_page()
        
        # 라즈베리파이용 긴 타임아웃 설정
        page.set_default_timeout(120000)  # 2분
        page.set_default_navigation_timeout(120000)  # 2분

        # WebSocket 후킹 스크립트 삽입 (개선된 버전)
        page.add_init_script("""
            (function() {
                const OriginalWebSocket = window.WebSocket;
                window.WebSocket = function(...args) {
                    const ws = new OriginalWebSocket(...args);
                    
                    // 연결 상태 로깅
                    ws.addEventListener('open', () => {
                        console.log("[WS STATUS] Connected to:", args[0]);
                    });
                    
                    ws.addEventListener('close', (event) => {
                        console.log("[WS STATUS] Disconnected, code:", event.code);
                    });
                    
                    ws.addEventListener('error', (error) => {
                        console.log("[WS ERROR]", error);
                    });
                    
                    // 메시지 로깅
                    ws.addEventListener('message', (event) => {
                        console.log("[WS MESSAGE]", event.data);
                    });
                    
                    return ws;
                };
            })();
        """)

        # 콘솔 로그 감지 및 처리 (개선된 버전)
        def handle_console(msg):
            global last_message_time
            txt = msg.text.strip()
            
            # WebSocket 상태 메시지 처리
            if txt.startswith("[WS STATUS]"):
                if "Connected to:" in txt:
                    logger.info("🔌 WebSocket 연결 성공")
                elif "Disconnected" in txt:
                    logger.warning("🔌 WebSocket 연결 끊어짐")
                return
            
            # WebSocket 에러 메시지 처리
            if txt.startswith("[WS ERROR]"):
                logger.error(f"🔌 WebSocket 에러: {txt}")
                send_error_notification("WebSocket 에러", txt)
                return
            
            # WebSocket 메시지 처리
            if txt.startswith("[WS MESSAGE]"):
                try:
                    raw_json = txt.replace("[WS MESSAGE]", "").strip()
                    data = json.loads(raw_json)
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
                        filepath = handle_news(data, SAVE_DIR)
                        logger.info(f"📰 뉴스 처리 완료: {filepath}")
                        
                    else:
                        error_msg = f"알 수 없는 메시지 타입: {message_type}"
                        logger.error(f"❌ {error_msg}")
                        send_error_notification("알 수 없는 메시지 타입", f"{error_msg}\n\n전체 데이터: {str(data)[:500]}...")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON 파싱 실패: {e}")
                except Exception as e:
                    logger.error(f"❌ 메시지 처리 오류: {e}")
                    send_error_notification("메시지 처리 오류", str(e))

        page.on("console", handle_console)

        # 접속 및 클릭 흐름
        page.goto("https://www.stocktitan.net/")
        logger.info("🌐 메인 페이지 접속 중...")

        timeout = 60000
        
        if config.STOCKTITAN_EMAIL and config.STOCKTITAN_PASSWORD:
            # Bootstrap이 로드되었는지 확인
            page.wait_for_function("typeof bootstrap !== 'undefined' || typeof window.bootstrap !== 'undefined'", timeout=timeout)
            logger.info("🌐 메인 페이지 접속 완료")
            logger.info("🌐 로그인 중...")

            # Login 버튼이 나타날 때까지 대기 (정확한 선택자로 2개 요소 문제 해결)
            page.wait_for_selector('ul.nav li.nav-item a[data-bs-target="#login-modal"]', timeout=timeout)
            
            # 라즈베리파이에서 안정성을 위한 추가 대기
            page.wait_for_timeout(2000)
            
            # Login 버튼 클릭 (순수 Playwright)
            page.click('ul.nav li.nav-item a[data-bs-target="#login-modal"]')
            logger.info("✅ Login 버튼 클릭 완료")
            
            # 모달이 완전히 열릴 때까지 대기
            page.wait_for_selector('#login-modal', state='attached', timeout=timeout)
            page.wait_for_timeout(3000)  # 애니메이션 완료 대기

            # 이메일 입력 필드가 나타날 때까지 대기
            page.wait_for_selector("input[name='email']", timeout=timeout)
            page.fill("input[name='email']", config.STOCKTITAN_EMAIL)
            logger.info("✅ 이메일 입력 완료")
            
            # 패스워드 입력 필드가 나타날 때까지 대기
            page.wait_for_selector("input[name='password']", timeout=timeout)
            page.fill("input[name='password']", config.STOCKTITAN_PASSWORD)
            logger.info("✅ 패스워드 입력 완료")
            
            # 로그인 제출 버튼이 활성화될 때까지 대기
            page.wait_for_selector("button#login-submit", timeout=timeout)
            page.wait_for_timeout(1000)  # 버튼 활성화 대기
            
            # 로그인 제출 버튼 클릭 (순수 Playwright)
            page.click("button#login-submit")
            logger.info("✅ 로그인 제출 버튼 클릭 완료")
            
            # 로그인 성공 확인 (닉네임이 나타나는지 체크)
            try:
                # ID 기반으로 닉네임 찾기
                page.wait_for_selector(f'a#navbarDropdownMenuLink:has-text("{config.STOCKTITAN_NAME}")', timeout=timeout)
                logger.info(f"✅ 로그인 성공: {config.STOCKTITAN_NAME}")
            except:
                logger.error("❌ 로그인 실패 - 닉네임을 찾을 수 없습니다")
                send_error_notification("StockTitan 로그인 실패", f"닉네임 '{config.STOCKTITAN_NAME}'을 찾을 수 없습니다.")
        else:
            logger.info("⚠️ StockTitan 로그인 정보 없음 - 게스트로 진행")

        page.wait_for_load_state('load', timeout=timeout)

        # NEWS FEED 버튼이 나타날 때까지 대기
        page.wait_for_selector("text=NEWS FEED", timeout=timeout)
        page.click("text=NEWS FEED")
        logger.info("✅ NEWS FEED 클릭 완료")

        page.wait_for_load_state('load', timeout=timeout)
        
        # 드롭다운 메뉴가 나타날 때까지 대기
        page.wait_for_selector("a.dropdown-item[href='/news/live.html']", timeout=timeout)
        page.click("a.dropdown-item[href='/news/live.html']")
        logger.info("🌐 실시간 뉴스 수신 페이지 이동 중...")

        page.wait_for_load_state('load', timeout=timeout)

        logger.info("🌐 실시간 뉴스 수신 페이지 이동 완료")
        logger.info("🌐 실시간 뉴스 수신 중...")

        # 타임아웃 체크 카운터
        timeout_check_counter = 0
        
        while True:
            page.wait_for_timeout(1000)
            timeout_check_counter += 1
            
            # 60초마다 타임아웃 체크 (60 * 1초 = 60초)
            if timeout_check_counter >= 60:
                timeout_check_counter = 0
                
                if last_message_time is not None:
                    time_diff = datetime.now() - last_message_time
                    if time_diff > timedelta(minutes=10):
                        error_msg = f"핑퐁/뉴스 수신 타임아웃: {time_diff.total_seconds()/60:.1f}분간 메시지 없음"
                        logger.error(f"❌ {error_msg}")
                        send_error_notification("WebSocket 타임아웃", error_msg)
                        break

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
