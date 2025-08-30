import json
import os
import requests
from datetime import datetime
from .config import logger, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from .llm_analyzer import analyze_prediction_accuracy_with_gpt, analyze_price_movement_with_gpt

def send_error_notification(error_type: str, error_message: str, symbol: str = ""):
    """
    에러 발생시 텔레그램으로 알림을 보냅니다.
    """
    try:
        bot_token = TELEGRAM_BOT_TOKEN
        chat_id = TELEGRAM_CHAT_ID
        
        if not bot_token or not chat_id:
            return
        
        symbol_text = f" ({symbol})" if symbol else ""
        message = f"""🚨 *시스템 에러 알림*{symbol_text}

❌ *에러 타입:* {error_type}
📝 *에러 내용:*
```
{error_message}
```

🕐 *시간:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        requests.post(telegram_url, json=payload, timeout=5)
        
    except Exception:
        # 에러 알림 자체에서 에러가 나면 무시 (무한 루프 방지)
        pass

def send_final_result_notification(symbol: str, price_data: list, volume_data: list, filepath: str):
    """
    60분 후 실제 결과와 예측 비교 분석 알림
    """
    try:
        bot_token = TELEGRAM_BOT_TOKEN
        chat_id = TELEGRAM_CHAT_ID
        
        if not bot_token or not chat_id:
            return
        
        # 실제 결과 데이터
        prices = [p for p in price_data if p is not None]
        volumes = [v for v in volume_data if v is not None] if volume_data else []
        
        if not prices:
            return
        
        final_price = prices[-1]
        total_volume = sum(volumes) if volumes else 0
        
        # 예측 데이터 가져오기
        prediction_data = None
        try:
            prediction_filepath = filepath.replace('.csv', '_prediction.json')
            if os.path.exists(prediction_filepath):
                with open(prediction_filepath, 'r', encoding='utf-8') as f:
                    prediction_data = json.load(f)
        except Exception:
            pass
        
        if not prediction_data:
            return
        
        # 예측 vs 실제 비교
        predicted_price = prediction_data.get('prediction', {}).get('predicted_price', 0)
        current_price = prediction_data.get('current_price', 0)
        actual_change = ((final_price - current_price) / current_price * 100) if current_price != 0 else 0
        predicted_change = prediction_data.get('prediction', {}).get('change_percent', 0)
        
        # 예측 정확도 계산
        price_accuracy = 100 - abs(predicted_price - final_price) / final_price * 100 if final_price != 0 else 0
        change_accuracy = 100 - abs(predicted_change - actual_change) if predicted_change != 0 else 0
        
        # AI 결과 분석
        result_analysis = analyze_prediction_accuracy_with_gpt(
            symbol, predicted_price, final_price, predicted_change, actual_change, price_accuracy
        )
        
        # 1분별 데이터 (처음 10분만 표시)
        minute_details = ""
        display_minutes = min(len(prices), 10)
        for i in range(display_minutes):
            price = prices[i]
            volume = volumes[i] if i < len(volumes) else 0
            minute_details += f"• {i+1}분: ${price:.2f}, 거래량 {volume:,.0f}\n"
        
        if len(prices) > 10:
            minute_details += f"... (총 {len(prices)}분 데이터)\n"
        
        # 결과 이모지
        accuracy_emoji = "🎯" if price_accuracy > 80 else "📊" if price_accuracy > 50 else "❌"
        
        message = f"""🏁 *60분 후 최종 결과* {accuracy_emoji}

📈 *종목:* `{symbol}`

🔮 *예측 vs 실제:*
• 예측가: ${predicted_price:.2f} → 실제가: ${final_price:.2f}
• 예측 변화: {predicted_change:+.2f}% → 실제 변화: {actual_change:+.2f}%
• 가격 정확도: {price_accuracy:.1f}%

📊 *거래 결과:*
• 총 거래량: {total_volume:,.0f}

📋 *분별 데이터:*
{minute_details}

🤖 *AI 결과 분석:*
{result_analysis.get('analysis', '분석 실패')}

📈 *예측 성능:* {result_analysis.get('performance', 'N/A')}
🔮 *향후 개선점:* {result_analysis.get('improvement', 'N/A')}

🕐 *완료 시간:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        requests.post(telegram_url, json=payload, timeout=5)
        
    except Exception as e:
        logger.error(f"❌ 최종 결과 알림 오류: {e}")

def send_monitoring_completion_notification(symbol: str, period_type: str, price_data: list, volume_data: list = None, original_news: dict = None):
    """
    가격 모니터링 완료시 1분별 상세 데이터와 AI 분석을 포함해서 텔레그램으로 알림을 보냅니다.
    """
    try:
        bot_token = TELEGRAM_BOT_TOKEN
        chat_id = TELEGRAM_CHAT_ID
        
        if not bot_token or not chat_id:
            return
        
        # 유효한 데이터만 필터링
        prices = [p for p in price_data if p is not None]
        volumes = [v for v in volume_data if v is not None] if volume_data else []
        
        if not prices:
            return
        
        # 기본 통계
        start_price = prices[0]
        end_price = prices[-1]
        min_price = min(prices)
        max_price = max(prices)
        price_change = end_price - start_price
        price_change_pct = (price_change / start_price * 100) if start_price != 0 else 0
        total_volume = sum(volumes) if volumes else 0
        
        # 변화율 이모지
        change_emoji = "📈" if price_change > 0 else "📉" if price_change < 0 else "➡️"
        
        # 1분별 상세 데이터 구성 (최대 10분만 표시, 나머지는 요약)
        minute_details = ""
        display_minutes = min(len(prices), 10)
        
        for i in range(display_minutes):
            price = prices[i]
            volume = volumes[i] if i < len(volumes) else 0
            minute_details += f"• {i+1}분: ${price:.2f}, 거래량 {volume:,.0f}\n"
        
        if len(prices) > 10:
            minute_details += f"... (총 {len(prices)}분 데이터)\n"
        
        # AI 재분석 (주가 변화 포함)
        ai_analysis = ""
        if original_news and period_type == "미래 60분":
            # 주가 변화를 포함한 재분석 요청
            analysis_result = analyze_price_movement_with_gpt(symbol, original_news, price_change_pct, total_volume)
            ai_analysis = f"""

🤖 *AI 주가 분석:*
{analysis_result.get('analysis', '분석 실패')}

📊 *예측 정확도:* {analysis_result.get('accuracy', 'N/A')}
🎯 *향후 전망:* {analysis_result.get('outlook', 'N/A')}"""
        
        message = f"""📊 *주가 모니터링 완료* {change_emoji}

📈 *종목:* `{symbol}`
⏰ *기간:* {period_type}

💰 *요약:*
• 시작가: ${start_price:.2f}
• 종료가: ${end_price:.2f}
• 가격 변화: ${price_change:+.2f} ({price_change_pct:+.2f}%)
• 총 거래량: {total_volume:,.0f}

📋 *분별 데이터:*
{minute_details}{ai_analysis}

🕐 *완료 시간:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        requests.post(telegram_url, json=payload, timeout=5)
        
    except Exception:
        # 알림 자체에서 에러가 나면 무시
        pass

def send_historical_analysis_notification(symbol: str, price_data: list, volume_data: list, filepath: str):
    """
    과거 60분 데이터 분석 완료 및 1시간 후 가격 예측 알림
    """
    try:
        bot_token = TELEGRAM_BOT_TOKEN
        chat_id = TELEGRAM_CHAT_ID
        
        if not bot_token or not chat_id:
            return
        
        # 뉴스 데이터 가져오기
        original_news = None
        try:
            analysis_filepath = filepath.replace('.csv', '_analysis.json')
            if os.path.exists(analysis_filepath):
                with open(analysis_filepath, 'r', encoding='utf-8') as f:
                    analysis_data = json.load(f)
                    original_news = analysis_data.get('news', {})
        except Exception:
            pass
        
        # 과거 데이터 분석
        prices = [p for p in price_data if p is not None]
        volumes = [v for v in volume_data if v is not None] if volume_data else []
        
        if not prices:
            return
        
        current_price = prices[-1]  # 뉴스 발표 시점 가격
        avg_price = sum(prices) / len(prices)
        total_volume = sum(volumes) if volumes else 0
        
        # AI로 1시간 후 가격 예측
        from .llm_analyzer import predict_price_with_gpt
        prediction_result = predict_price_with_gpt(symbol, original_news, prices, volumes)
        
        # 예측 결과를 파일에 저장 (나중에 비교용)
        prediction_filepath = filepath.replace('.csv', '_prediction.json')
        prediction_data = {
            "symbol": symbol,
            "current_price": current_price,
            "prediction": prediction_result,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(prediction_filepath, 'w', encoding='utf-8') as f:
            json.dump(prediction_data, f, ensure_ascii=False, indent=2)
        
        # 뉴스 분석 결과 가져오기
        news_analysis = None
        try:
            analysis_filepath = filepath.replace('.csv', '_analysis.json')
            if os.path.exists(analysis_filepath):
                with open(analysis_filepath, 'r', encoding='utf-8') as f:
                    analysis_data = json.load(f)
                    news_analysis = analysis_data.get('llm_analysis', {})
        except Exception:
            pass
        
        # 뉴스 정보
        news_title = original_news.get('title', '제목 없음') if original_news else '뉴스 없음'
        news_info = ""
        if news_analysis:
            rating_emoji = "📈" if news_analysis.get('rating', 3) >= 4 else "📉" if news_analysis.get('rating', 3) <= 2 else "📊"
            sentiment_emoji = {"positive": "😊", "negative": "😰", "neutral": "😐"}.get(news_analysis.get('sentiment', 'neutral'), "😐")
            impact_emoji = {"high": "🔥", "medium": "⚡", "low": "💧"}.get(news_analysis.get('impact', 'medium'), "⚡")
            
            news_info = f"""

📰 *뉴스 분석:*
• 제목: {news_title}
• AI 평점: {news_analysis.get('rating', 3)}/5 {sentiment_emoji}
• 감성: {news_analysis.get('sentiment', 'neutral')}
• 영향도: {news_analysis.get('impact', 'medium')} {impact_emoji}

🤖 *뉴스 분석 내용:*
{news_analysis.get('analysis', '분석 없음')}"""

        # 1분별 상세 데이터 구성 (최대 10분만 표시)
        minute_details = ""
        display_minutes = min(len(prices), 10)
        
        for i in range(display_minutes):
            price = prices[i]
            volume = volumes[i] if i < len(volumes) else 0
            minute_details += f"• {i+1}분: ${price:.2f}, 거래량 {volume:,.0f}\n"
        
        if len(prices) > 10:
            minute_details += f"... (총 {len(prices)}분 데이터)\n"

        message = f"""🚨 *뉴스 발생 & 과거 60분 분석 완료*

📈 *종목:* `{symbol}` {rating_emoji if news_analysis else ""}
💰 *현재가:* ${current_price:.2f}
📊 *평균가:* ${avg_price:.2f}
📋 *총 거래량:* {total_volume:,.0f}{news_info}

📋 *과거 60분 분별 데이터:*
{minute_details}

🔮 *AI 1시간 후 예측:*
• 예상 가격: ${prediction_result.get('predicted_price', 0):.2f}
• 변화율: {prediction_result.get('change_percent', 0):+.2f}%
• 신뢰도: {prediction_result.get('confidence', 'N/A')}

📝 *예측 근거:*
{prediction_result.get('reasoning', '분석 실패')}

🕐 *분석 시간:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        requests.post(telegram_url, json=payload, timeout=5)
        
    except Exception as e:
        logger.error(f"❌ 과거 분석 알림 오류: {e}")
