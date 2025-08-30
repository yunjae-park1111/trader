# 📈 News Listener - AI 기반 실시간 뉴스 트레이딩 분석 시스템

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5-green.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**StockTitan 실시간 뉴스를 수신하여 GPT로 분석하고, 주가 변동을 모니터링하는 자동화된 AI 트레이딩 분석 시스템**

## 🌟 주요 기능

### 🔥 핵심 기능
- **🌐 실시간 뉴스 수신**: StockTitan 웹소켓을 통한 실시간 뉴스 스트림 모니터링
- **🤖 GPT 뉴스 분석**: OpenAI GPT-5를 활용한 뉴스 감성 분석 및 평점 시스템 (1-5점)
- **📊 주가 데이터 수집**: Webull API 연동으로 실시간 및 과거 주가/거래량 데이터 수집
- **🔮 AI 가격 예측**: 뉴스 분석 + 과거 데이터 기반 1시간 후 주가 예측
- **📱 텔레그램 실시간 알림**: 뉴스 발생, 분석 결과, 예측 정확도 실시간 알림
- **🔄 자동 재시작**: 시스템 오류 시 자동 재시작 및 오류 알림

### 💡 고급 기능  
- **📈 60분 주가 모니터링**: 뉴스 발생 전후 각 60분간 분별 데이터 수집
- **🎯 예측 정확도 추적**: 예측 vs 실제 결과 비교 분석
- **📋 CSV 데이터 저장**: 체계적인 데이터 수집 및 저장 시스템
- **🐳 Docker & K8s 지원**: 간편한 배포 및 확장성

## 🏗 아키텍처 및 패키지 구조

```
📦 Trader/
├── 🚀 main.py                    # 메인 실행 파일 
├── 📋 test_news_listener.py      # 테스트 파일
├── 📄 requirements.txt           # 패키지 의존성
├── 🐳 Dockerfile                 # Docker 설정
├── ☸️  k8s-deployment.yaml       # 쿠버네티스 배포 파일
├── 🌐 .env                       # 환경변수 (git에서 제외)
└── 📦 news_listener/             # 핵심 패키지
    ├── 🔧 __init__.py            # 패키지 초기화 및 Export
    ├── ⚙️  config.py              # 설정 관리 및 환경변수 로드
    ├── 🤖 llm_analyzer.py        # GPT 분석 엔진
    ├── 📈 webull_client.py       # Webull API 클라이언트  
    ├── 📱 telegram_notifier.py   # 텔레그램 알림 시스템
    ├── 📊 price_monitor.py       # 가격 모니터링 스레드
    └── 📰 news_handler.py        # 뉴스 처리 로직
```

## 🚀 빠른 시작

### 1️⃣ 환경 설정

```bash
# 1. 저장소 클론
git clone <repository-url>
cd Trader

# 2. Python 가상환경 설정 (권장)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. 패키지 설치
pip3 install -r requirements.txt

# 4. Playwright 브라우저 설치
python3 -m playwright install chromium
```

### 2️⃣ 환경변수 설정

`.env` 파일을 생성하고 다음 내용을 설정하세요:

```bash
# 🔑 OpenAI API (필수)
OPENAI_API_KEY=your_openai_api_key_here
GPT_MODEL=gpt-5

# 🌐 StockTitan 계정 (필수)
STOCKTITAN_EMAIL=your_email@example.com
STOCKTITAN_PASSWORD=your_password
STOCKTITAN_NAME=your_display_name

# 📱 텔레그램 봇 설정 (필수)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# 📈 Webull 계정 (선택사항)
WB_EMAIL=your_webull_email
WB_PASSWORD=your_webull_password
WB_TRADE_PIN=your_trade_pin

# 🔧 기타 설정
LOG_LEVEL=INFO
```

### 3️⃣ 실행

```bash
# 로컬 실행
python3 main.py

# 또는 테스트 먼저
python3 test_news_listener.py
```

## 🐳 Docker 사용법

### 빠른 Docker 실행

```bash
# 1. Docker 이미지 빌드
docker build -t news-listener .

# 2. 컨테이너 실행 (.env 파일 필요)
docker run -d \
  --name news-listener \
  --env-file .env \
  -v $(pwd)/news_data_browser:/app/news_data_browser \
  news-listener
```

### Docker Compose (권장)

```bash
# 백그라운드 실행
docker-compose up -d

# 로그 확인  
docker-compose logs -f

# 중지
docker-compose down
```

## ☸️ 쿠버네티스 사용법

### 쿠버네티스 배포

```bash
# 1. Docker 이미지 빌드 & GitHub Container Registry로 푸시
docker build -t ghcr.io/yunjae-park1111/stocktitan-news-listener:latest .
docker push ghcr.io/yunjae-park1111/stocktitan-news-listener:latest

# 2. 쿠버네티스 배포
kubectl apply -f k8s-deployment.yaml

# 3. 상태 확인
kubectl get pods -l app=stocktitan-news-listener
kubectl logs -l app=stocktitan-news-listener -f
```

### 쿠버네티스 관리 명령어

```bash
# 배포 상태 확인
kubectl get deployment stocktitan-news-listener

# Pod 상태 확인
kubectl get pods -l app=stocktitan-news-listener

# 로그 확인
kubectl logs -l app=stocktitan-news-listener -f

# 재시작 (새 이미지 배포시)
kubectl rollout restart deployment/stocktitan-news-listener

# 제거
kubectl delete -f k8s-deployment.yaml
```

### 쿠버네티스 주의사항

- **환경변수**: 이미 `.env` 파일 값이 `k8s-deployment.yaml`에 적용되어 있습니다
- **이미지**: GitHub Container Registry (`ghcr.io`) 사용, `imagePullPolicy: Always`로 설정됨
- **리소스**: CPU 500m~1000m, 메모리 512Mi~1Gi로 설정
- **보안**: 운영환경에서는 `Secret` 사용 권장
- **데이터**: 영속성이 필요하면 `PersistentVolume` 추가 구성 필요

## 📊 데이터 구조

### CSV 파일 구조 (240개 컬럼)
```csv
symbol, market_cap, news_flag, llm_rating,
pct_m60, pct_m59, ..., pct_m1,           # 과거 60분 가격 변화율
volume_m60, volume_m59, ..., volume_m1,   # 과거 60분 거래량  
pct_p1, pct_p2, ..., pct_p60,            # 미래 60분 가격 변화율
volume_p1, volume_p2, ..., volume_p60     # 미래 60분 거래량
```

### JSON 분석 파일
```json
{
  "symbol": "TSLA",
  "timestamp": "2024-01-01T09:00:00",
  "news": {
    "title": "Tesla announces breakthrough...",
    "content": "Tesla today announced...",
    "timestamp": 1640995200000
  },
  "llm_analysis": {
    "analysis": "이 뉴스는 Tesla의 획기적인 발전을...",
    "rating": 4,
    "sentiment": "positive",
    "impact": "high"
  },
  "market_cap": "800000000000"
}
```

## 🤖 AI 분석 시스템

### 1. 뉴스 감성 분석
- **📊 평점**: 1점(매우 부정적) ~ 5점(매우 긍정적)  
- **💭 감성**: positive/negative/neutral
- **🎯 영향도**: high/medium/low
- **📝 분석**: 상세한 한국어 분석 결과

### 2. 주가 예측 엔진
- **📈 입력**: 과거 60분 가격/거래량 데이터 + 뉴스 분석
- **🔮 출력**: 1시간 후 예상 가격 및 변화율
- **🎯 신뢰도**: AI가 판단한 예측 신뢰도
- **💡 근거**: 예측 이유 및 분석 근거

### 3. 예측 정확도 검증
- **⏰ 60분 후**: 실제 결과와 예측 비교
- **📊 정확도**: 가격 정확도 및 방향성 정확도  
- **🔍 분석**: AI 기반 예측 성능 분석
- **📈 개선**: 향후 개선 방향 제안

## 📱 텔레그램 알림 시스템

### 🚨 뉴스 발생 알림
```
📰 뉴스 발생 & 과거 60분 분석 완료

📈 종목: TSLA 📈
💰 현재가: $250.50
📊 평균가: $248.30  
📋 총 거래량: 1,234,567

📰 뉴스 분석:
• 제목: Tesla announces breakthrough...
• AI 평점: 4/5 😊
• 감성: positive
• 영향도: high 🔥

🔮 AI 1시간 후 예측:
• 예상 가격: $255.20
• 변화율: +1.9%
• 신뢰도: 높음

📝 예측 근거:
긍정적인 기술 발표로 인한 상승 모멘텀 예상...
```

### 🏁 최종 결과 알림  
```
🏁 60분 후 최종 결과 🎯

📈 종목: TSLA
🔮 예측 vs 실제:
• 예측가: $255.20 → 실제가: $254.80
• 예측 변화: +1.9% → 실제 변화: +1.7%  
• 가격 정확도: 99.8%

🤖 AI 결과 분석:
예측이 매우 정확했으며, 뉴스의 긍정적 영향이 실제로 나타났습니다...
```

## 🛠 기술 스택

### 🐍 Backend
- **Python 3.9+**: 메인 프로그래밍 언어
- **Playwright**: 웹 자동화 및 웹소켓 후킹
- **OpenAI GPT-5**: 뉴스 분석 및 예측 엔진
- **Webull API**: 주식 데이터 수집

### 📦 핵심 라이브러리
- **openai**: GPT API 연동
- **playwright**: 브라우저 자동화  
- **webull**: 주식 데이터 API
- **python-dotenv**: 환경변수 관리
- **requests**: HTTP 통신
- **pandas**: 데이터 처리

### 🏗 인프라
- **Docker**: 컨테이너화
- **Kubernetes**: 오케스트레이션
- **환경변수**: 설정 관리
- **CSV/JSON**: 데이터 저장

## 🔧 고급 설정

### 환경변수 상세 설명

| 변수명 | 필수여부 | 설명 | 예시 |
|--------|----------|------|------|
| `OPENAI_API_KEY` | ✅ 필수 | OpenAI API 키 | `sk-proj-...` |
| `GPT_MODEL` | ✅ 필수 | 사용할 GPT 모델 | `gpt-5` |
| `STOCKTITAN_EMAIL` | ✅ 필수 | StockTitan 로그인 이메일 | `user@example.com` |
| `STOCKTITAN_PASSWORD` | ✅ 필수 | StockTitan 비밀번호 | `password123` |
| `STOCKTITAN_NAME` | ✅ 필수 | StockTitan 표시명 | `john_doe` |
| `TELEGRAM_BOT_TOKEN` | ✅ 필수 | 텔레그램 봇 토큰 | `123456:ABC...` |
| `TELEGRAM_CHAT_ID` | ✅ 필수 | 텔레그램 채팅 ID | `123456789` |
| `WB_EMAIL` | ⚪ 선택 | Webull 이메일 | `user@example.com` |
| `WB_PASSWORD` | ⚪ 선택 | Webull 비밀번호 | `password123` |
| `WB_TRADE_PIN` | ⚪ 선택 | Webull 거래 PIN | `123456` |
| `LOG_LEVEL` | ⚪ 선택 | 로그 레벨 | `INFO` |

### 텔레그램 봇 설정 방법

1. **@BotFather**에게 `/newbot` 명령어 전송
2. 봇 이름과 사용자명 설정
3. **Token** 받기 → `TELEGRAM_BOT_TOKEN`에 입력
4. 봇과 대화 시작 후 Chat ID 확인
5. 또는 `https://api.telegram.org/bot<TOKEN>/getUpdates` 접속

## 📈 성능 및 확장성

### ⚡ 성능 특징
- **실시간 처리**: 뉴스 수신 즉시 분석 시작
- **병렬 처리**: 과거/미래 데이터 수집 동시 진행  
- **메모리 효율**: 스트림 방식 데이터 처리
- **자동 재시작**: 오류 시 자동 복구

### 🔧 확장 가능성
- **멀티 심볼**: 여러 종목 동시 모니터링 지원
- **다중 뉴스 소스**: 추가 뉴스 사이트 연동 가능
- **ML 모델**: 커스텀 예측 모델 통합 가능
- **데이터베이스**: PostgreSQL/MongoDB 연동 가능

## 🚦 문제 해결

### 자주 발생하는 문제

**Q: 로그인이 안 됩니다**
```bash
# 로그에서 환경변수 확인
python3 -c "from news_listener.config import *; print(f'Email: {STOCKTITAN_EMAIL}')"
```

**Q: OpenAI API 오류**
```bash
# API 키 확인
python3 -c "import openai; print('API 키 유효함' if openai.api_key else 'API 키 없음')"
```

**Q: 텔레그램 알림이 안 옴**
```bash
# 텔레그램 봇 테스트
python3 test_news_listener.py telegram
```

**Q: Docker 실행 오류**
```bash
# 컨테이너 로그 확인
docker logs news-listener

# 환경변수 확인
docker exec news-listener env | grep -E "(OPENAI|STOCK|TELEGRAM)"
```

**Q: 쿠버네티스 배포 오류**
```bash
# Pod 상태 확인
kubectl describe pod -l app=stocktitan-news-listener

# 로그 확인
kubectl logs -l app=stocktitan-news-listener --previous

# 이미지 풀 오류 확인
kubectl get events --sort-by=.metadata.creationTimestamp
```

## 📝 라이선스 및 면책조항

### 📄 라이선스
이 프로젝트는 **MIT 라이선스** 하에 배포됩니다.

### ⚠️ 면책조항
- 이 시스템은 **교육 및 연구 목적**으로 제작되었습니다
- **실제 투자에 대한 조언을 제공하지 않습니다**
- 투자 결정은 **본인의 판단과 책임** 하에 이루어져야 합니다
- 시스템 사용으로 인한 **손실에 대해 책임지지 않습니다**
- 실제 거래 전 **충분한 백테스팅과 검증**을 권장합니다

## 🤝 기여하기

1. **Fork** the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)  
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a **Pull Request**

## 📞 연락처 및 지원

- **이슈 제보**: GitHub Issues
- **기능 제안**: GitHub Discussions  
- **보안 문제**: 이메일로 개별 연락

---

<div align="center">

**⭐ 도움이 되었다면 Star를 눌러주세요! ⭐**

</div>