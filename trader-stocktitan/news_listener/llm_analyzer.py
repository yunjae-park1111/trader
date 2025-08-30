import json
import openai
from .config import logger, OPENAI_API_KEY, GPT_MODEL

# OpenAI API 키 설정
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
else:
    logger.warning("⚠️ OpenAI API 키가 설정되지 않았습니다.")

def analyze_news_with_gpt(news_data: dict) -> dict:
    """
    OpenAI GPT를 사용해 뉴스를 분석하고 평점(1-5)을 받아옵니다.
    """
    try:
        if not OPENAI_API_KEY:
            logger.error("❌ OpenAI API 키가 설정되지 않았습니다.")
            return get_default_analysis("API 키 없음")
        
        # 뉴스 데이터 준비
        title = news_data.get("title", "")
        content = news_data.get("content", "")
        symbol = news_data.get("symbol", "")
        
        # GPT에 보낼 프롬프트 구성
        prompt = f"""
다음 뉴스를 분석해주세요:

종목: {symbol}
제목: {title}
내용: {content}

다음 형식으로 JSON 응답해주세요:
{{
    "analysis": "뉴스 분석 결과 (한국어)",
    "rating": 3,
    "sentiment": "positive/negative/neutral",
    "impact": "high/medium/low"
}}

평점은 1(매우 부정적) ~ 5(매우 긍정적) 사이의 숫자로 주세요.
"""

        # GPT API 호출
        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        
        # JSON 파싱 시도
        try:
            analysis_result = json.loads(content)
            logger.info(f"✅ GPT 분석 완료: {symbol} - 평점 {analysis_result.get('rating', 3)}")
            return analysis_result
        except json.JSONDecodeError:
            # JSON 파싱 실패시 텍스트에서 평점 추출 시도
            logger.warning("⚠️ JSON 파싱 실패, 텍스트에서 평점 추출 시도")
            rating = 3  # 기본값
            if "rating" in content.lower():
                import re
                rating_match = re.search(r'"rating":\s*(\d)', content)
                if rating_match:
                    rating = int(rating_match.group(1))
            
            return {
                "analysis": content,
                "rating": rating,
                "sentiment": "neutral",
                "impact": "medium"
            }
            
    except openai.error.OpenAIError as e:
        error_msg = f"OpenAI API 오류: {e}"
        logger.error(f"❌ {error_msg}")
        return get_default_analysis("API 오류")
        
    except Exception as e:
        error_msg = f"GPT 분석 오류: {e}"
        logger.error(f"❌ {error_msg}")
        return get_default_analysis("분석 오류")

def predict_price_with_gpt(symbol: str, news_data: dict, price_history: list, volume_history: list) -> dict:
    """
    뉴스 내용과 과거 60분 데이터를 바탕으로 GPT를 사용해 1시간 후 가격을 예측합니다.
    """
    try:
        if not OPENAI_API_KEY:
            logger.error("❌ OpenAI API 키가 설정되지 않았습니다.")
            return get_default_prediction(price_history)
        
        if not news_data:
            return get_default_prediction(price_history)
        
        title = news_data.get("title", "")
        current_price = price_history[-1] if price_history else 0
        avg_volume = sum(volume_history) / len(volume_history) if volume_history else 0
        
        prompt = f"""
다음 정보를 바탕으로 1시간 후 주가를 예측해주세요:

종목: {symbol}
뉴스: {title}
현재가: ${current_price:.2f}
과거 60분 평균 거래량: {avg_volume:,.0f}

다음 형식으로 JSON 응답해주세요:
{{
    "predicted_price": 250.50,
    "change_percent": 2.5,
    "confidence": "높음/보통/낮음",
    "reasoning": "예측 근거 설명"
}}
"""

        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400
        )
        
        content = response.choices[0].message.content
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # JSON 파싱 실패시 기본값
            return {
                "predicted_price": current_price,
                "change_percent": 0,
                "confidence": "낮음",
                "reasoning": content[:200] + "..."
            }
        
    except openai.error.OpenAIError as e:
        logger.error(f"❌ OpenAI API 가격 예측 오류: {e}")
    except Exception as e:
        logger.error(f"❌ GPT 가격 예측 오류: {e}")
    
    return get_default_prediction(price_history)

def analyze_prediction_accuracy_with_gpt(symbol: str, predicted_price: float, actual_price: float, 
                                       predicted_change: float, actual_change: float, accuracy: float) -> dict:
    """
    예측 정확도를 GPT로 분석합니다.
    """
    try:
        if not OPENAI_API_KEY:
            return get_default_accuracy_analysis(accuracy)
        
        prompt = f"""
다음 주가 예측 결과를 분석해주세요:

종목: {symbol}
예측가: ${predicted_price:.2f} → 실제가: ${actual_price:.2f}
예측 변화: {predicted_change:+.2f}% → 실제 변화: {actual_change:+.2f}%
정확도: {accuracy:.1f}%

다음 형식으로 JSON 응답해주세요:
{{
    "analysis": "예측 결과 분석 (한국어)",
    "performance": "예측 성능 평가",
    "improvement": "향후 개선 방향"
}}
"""

        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        
        content = response.choices[0].message.content
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "analysis": content,
                "performance": "분석 완료",
                "improvement": "지속적 모니터링"
            }
        
    except Exception as e:
        logger.error(f"❌ GPT 정확도 분석 오류: {e}")
    
    return get_default_accuracy_analysis(accuracy)

def analyze_price_movement_with_gpt(symbol: str, original_news: dict, price_change_pct: float, total_volume: int) -> dict:
    """
    뉴스 발표 후 실제 주가 움직임을 GPT로 분석합니다.
    """
    try:
        if not OPENAI_API_KEY:
            return get_default_movement_analysis()
        
        title = original_news.get("title", "")
        
        prompt = f"""
다음 뉴스 발표 후 실제 주가 움직임을 분석해주세요:

종목: {symbol}
뉴스: {title}
실제 주가 변화: {price_change_pct:+.2f}%
총 거래량: {total_volume:,.0f}

다음 형식으로 JSON 응답해주세요:
{{
    "analysis": "뉴스와 실제 주가 움직임 분석 (한국어)",
    "accuracy": "예측 정확도 평가",
    "outlook": "향후 전망"
}}
"""

        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        
        content = response.choices[0].message.content
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "analysis": content,
                "accuracy": "분석 완료",
                "outlook": "추가 모니터링 필요"
            }
        
    except Exception as e:
        logger.error(f"❌ GPT 주가 분석 오류: {e}")
    
    return get_default_movement_analysis()

def get_default_analysis(reason: str) -> dict:
    """기본 분석 결과를 반환합니다."""
    return {
        "analysis": f"분석 실패: {reason}",
        "rating": 3,
        "sentiment": "neutral",
        "impact": "medium"
    }

def get_default_prediction(price_history: list) -> dict:
    """기본 예측 결과를 반환합니다."""
    current_price = price_history[-1] if price_history else 0
    return {
        "predicted_price": current_price,
        "change_percent": 0,
        "confidence": "낮음",
        "reasoning": "예측 실패"
    }

def get_default_accuracy_analysis(accuracy: float) -> dict:
    """기본 정확도 분석 결과를 반환합니다."""
    return {
        "analysis": "예측 결과 분석 완료",
        "performance": f"정확도 {accuracy:.1f}%",
        "improvement": "데이터 수집 지속"
    }

def get_default_movement_analysis() -> dict:
    """기본 주가 움직임 분석 결과를 반환합니다."""
    return {
        "analysis": "GPT 분석 실패",
        "accuracy": "N/A",
        "outlook": "수동 분석 필요"
    }
