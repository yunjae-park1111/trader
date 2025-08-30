import os
import csv
from news_listener import (
    handle_news, 
    SAVE_DIR, 
    logger,
    send_error_notification
)
import logging
# logger는 이미 news_listener 패키지에서 import됨

def test_handle_news():
    """뉴스 처리 함수 테스트""" 
    
    # 테스트 뉴스 데이터
    test_data = {
        "payload": {
            "news": {
                "symbol": "TSLA",
                "timestamp": 1640995200000,
                "title": "Tesla news"
            },
            "stock": {
                "marketCap": "800000000000"
            }
        }
    }
    
    # 함수 실행
    filepath = handle_news(test_data, SAVE_DIR)
    logger.info(f"🔍 뉴스 처리 결과: {filepath}")
    assert os.path.exists(filepath)
    
    # CSV 내용 확인
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    assert len(rows) == 2
    assert rows[1][0] == "TSLA"  # symbol
    assert rows[1][1] == "800000000000"  # market_cap
    logger.info("🔍 뉴스 처리 결과 확인 완료")

def test_telegram_notification():
    """텔레그램 봇 알림 테스트"""
    print("🧪 텔레그램 봇 테스트 시작...")
    
    # 에러 알림 테스트
    test_error_msg = "테스트용 에러 메시지입니다. 텔레그램 봇이 정상적으로 작동하는지 확인하는 메시지입니다."
    
    # 텔레그램 에러 알림 발송 테스트
    send_error_notification("테스트 에러", test_error_msg, "TSLA")
    
    print("✅ 텔레그램 테스트 완료! 메시지를 확인해보세요.")

def test_handle_news_error():
    """뉴스 처리 에러 테스트"""
    # 잘못된 데이터 형식
    invalid_data = {"invalid": "data"}
    
    # 에러가 발생해도 예외가 발생하지 않아야 함
    try:
        handle_news(invalid_data, SAVE_DIR)
    except Exception as e:
        assert False, f"handle_news raised an exception: {e}"


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "telegram":
        # 텔레그램 테스트만 실행
        test_telegram_notification()
    else:
        # 모든 테스트 실행
        print("🧪 모든 테스트 시작...")
        test_handle_news()
        test_telegram_notification()
        print("✅ 모든 테스트 완료!")