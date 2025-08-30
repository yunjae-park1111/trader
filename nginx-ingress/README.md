# Nginx Ingress Controller with SSL & Router Proxy

**고가용성 SSL 종료 및 외부 라우터 프록시 시스템**

## 📋 개요

이 Helm 차트는 다음 구성 요소들을 통합한 완전한 인그레스 솔루션을 제공합니다:

- **Nginx Ingress Controller**: 쿠버네티스 내부 서비스 라우팅
- **Cert-Manager**: Let's Encrypt 자동 SSL 인증서 발급/갱신
- **Router Proxy**: 전용 SSL 종료 및 외부 IP 포워딩

## 🏗️ 아키텍처

```
Internet → RouterProxy (SSL Termination) → Internal Services
                ↓
        [80] HTTP → HTTPS Redirect
        [443] HTTPS → HTTP Proxy to Ingress
        [10000] HTTPS → HTTP Proxy to Router
```

### 주요 특징

✅ **SSL Termination**: 모든 HTTPS 트래픽을 RouterProxy에서 종료  
✅ **자동 HTTP→HTTPS 리다이렉트**: 포트 80에서 443으로 자동 전환  
✅ **외부 IP 통합**: 외부 하드웨어 라우터 등을 쿠버네티스에 통합  
✅ **경로 기반 라우팅**: 단일 백엔드에서 여러 경로 처리  
✅ **포트 매핑**: 백엔드 포트와 프록시 포트 독립적 설정  
✅ **IP/도메인 겸용**: 도메인 없이도 IP만으로 접근 가능  

## 📁 구조

```
nginx-ingress/
├── helm-chart/
│   ├── Chart.yaml              # Helm 차트 메타데이터
│   ├── values.yaml            # 설정 파일 (주요!)
│   ├── templates/
│   │   ├── basic-ingress.yaml       # 기본 인그레스 리소스
│   │   ├── router-proxy.yaml       # RouterProxy (SSL 종료)
│   │   ├── external-services.yaml  # 외부 IP 서비스 생성
│   │   └── letsencrypt-issuer.yaml # SSL 인증서 발급자
│   ├── charts/                # 의존성 차트들
│   └── crds/                  # 커스텀 리소스 정의
└── README.md                   # 이 문서
```

## ⚙️ 설정 (values.yaml)

### Global 설정

```yaml
global:
  # 도메인 설정 (선택사항 - 없으면 IP만 사용)
  domain: yjhome.kro.kr  # 비워두면 IP 전용 모드
  email: piwhyjey@gmail.com  # Let's Encrypt 이메일
  environment: production  # staging 또는 production
  
  # SSL/TLS 설정
  ssl:
    enabled: true  # SSL 활성화/비활성화
    secretName: yjhome-tls-cert
    clusterIssuer: letsencrypt-prod
```

### RouterProxy 설정

```yaml
routerProxy:
  enabled: true
  replicas: 1
  
  # 백엔드 서비스들
  backends:
  - name: router
    serviceName: router-service
    # 외부 서비스 정보 (자동으로 Service/EndpointSlice 생성)
    external:
      ip: 172.30.1.254
      namespace: ingress-nginx
    
    # 라우팅 설정 (경로별 포트 매핑)
    routes:
    - path: /
      ports:
      - targetPort: 8899    # 백엔드 실제 포트
        proxyPort: 10000    # 외부 노출 포트 (생략시 targetPort 사용)
      # - targetPort: 8899  # proxyPort 생략 예시 (8899로 접근)
```

### 주요 개념

- **targetPort**: 백엔드 서비스의 실제 포트
- **proxyPort**: 외부에서 접근하는 포트 (선택사항)
- **path**: 라우팅할 경로 (/, /app 등)
- **external.ip**: 외부 하드웨어 IP 주소
- **external.namespace**: 서비스가 생성될 네임스페이스

## 🚀 설치

```bash
# 1. K3s 클러스터 접속
yjhome_raspi

# 2. 네임스페이스 생성
kubectl create namespace ingress-nginx

# 3. Helm 차트 설치
cd nginx-ingress/helm-chart
helm dependency update
helm install ingress-nginx . --namespace ingress-nginx

# 4. 업그레이드 (설정 변경 후)
helm upgrade ingress-nginx . --namespace ingress-nginx

# 5. 삭제
helm uninstall ingress-nginx --namespace ingress-nginx
```

## 📊 상태 확인

```bash
# 전체 파드 확인
kubectl get pods -n ingress-nginx

# RouterProxy 서비스 확인
kubectl get svc router-proxy-service -n ingress-nginx

# SSL 인증서 확인
kubectl get certificate -A

# 인그레스 확인
kubectl get ingress -A
```

## 🧪 테스트

### SSL 종료 테스트

```bash
# HTTPS 접근 테스트 (SSL 종료)
curl -I https://yjhome.kro.kr:10000

# HTTP 리다이렉트 테스트
curl -I http://yjhome.kro.kr:80
```

### IP 접근 테스트

```bash
# IP로 직접 접근
curl -I https://172.30.1.100:10000

# HTTP에서 HTTPS 리다이렉트
curl -I http://172.30.1.100:80
```

## 🔧 사용 예시

### 1. 새 백엔드 추가

```yaml
# values.yaml에 추가
routerProxy:
  backends:
  - name: myapp
    serviceName: my-app-service
    external:
      ip: 192.168.1.100
      namespace: default
    routes:
    - path: /app
      ports:
      - targetPort: 8080
        proxyPort: 9000
```

### 2. SSL 비활성화 (개발 환경)

```yaml
global:
  ssl:
    enabled: false  # HTTP만 사용
```

### 3. 도메인 없이 IP만 사용

```yaml
global:
  domain: ""  # 빈 문자열로 설정
```

## 🚨 트러블슈팅

### 1. SSL 인증서 발급 실패

```bash
# 인증서 상태 확인
kubectl describe certificate yjhome-tls-cert -n ingress-nginx

# CertificateRequest 확인
kubectl get certificaterequest -n ingress-nginx

# ClusterIssuer 상태 확인
kubectl describe clusterissuer letsencrypt-prod
```

### 2. RouterProxy 파드 시작 실패

```bash
# 파드 로그 확인
kubectl logs -n ingress-nginx deployment/router-proxy

# 설정 확인
kubectl describe configmap router-proxy-config -n ingress-nginx
```

### 3. LoadBalancer Pending

```bash
# 서비스 상태 확인
kubectl describe svc router-proxy-service -n ingress-nginx

# K3s ServiceLB 로그 확인
kubectl logs -n kube-system -l app=svclb-router-proxy-service
```

### 4. 포트 충돌

```bash
# 포트 사용 중인 서비스 확인
kubectl get svc -A | grep LoadBalancer

# K3s Traefik 비활성화 (필요시)
# sudo systemctl stop k3s
# sudo systemctl start k3s --disable traefik
```

### 5. Nginx 설정 오류

```bash
# 설정 파일 확인
kubectl exec -n ingress-nginx deployment/router-proxy -- nginx -t

# 설정 파일 내용 확인
kubectl exec -n ingress-nginx deployment/router-proxy -- cat /etc/nginx/nginx.conf
```

## 🔄 업그레이드

### values.yaml 수정 후

```bash
cd nginx-ingress/helm-chart
helm upgrade ingress-nginx . --namespace ingress-nginx
```

### 강제 재시작

```bash
# RouterProxy 파드 재시작
kubectl rollout restart deployment/router-proxy -n ingress-nginx

# Nginx Ingress Controller 재시작
kubectl rollout restart deployment/ingress-nginx-controller -n ingress-nginx
```

## 🗂️ 주요 파일 설명

### Chart.yaml
- Helm 차트 메타데이터
- ingress-nginx, cert-manager 의존성 정의

### values.yaml
- **가장 중요한 설정 파일**
- 모든 구성 요소의 설정을 중앙화

### router-proxy.yaml
- SSL 종료를 담당하는 전용 Nginx 프록시
- ConfigMap으로 동적 nginx.conf 생성
- 백엔드 리다이렉트 포트 변환 (`proxy_redirect`) 처리

### external-services.yaml
- 외부 IP를 위한 Service/EndpointSlice 자동 생성
- values.yaml의 `external` 설정 기반

### basic-ingress.yaml
- 기본 인그레스 리소스 (필요시 사용)
- RouterProxy가 주 진입점이므로 보조 역할

## 📊 모니터링

### 메트릭 확인

```bash
# RouterProxy 상태
kubectl top pods -n ingress-nginx | grep router-proxy

# 인그레스 컨트롤러 상태  
kubectl top pods -n ingress-nginx | grep ingress-nginx-controller
```

### 로그 모니터링

```bash
# RouterProxy 로그
kubectl logs -f -n ingress-nginx deployment/router-proxy

# 인그레스 컨트롤러 로그
kubectl logs -f -n ingress-nginx deployment/ingress-nginx-controller
```

## 🎯 핵심 장점

1. **통합 관리**: 모든 설정을 values.yaml에서 중앙 관리
2. **유연한 포트 매핑**: targetPort와 proxyPort 독립 설정
3. **자동 SSL**: Let's Encrypt 완전 자동화
4. **외부 통합**: 하드웨어 라우터 등 쿠버네티스에 자연스럽게 통합
5. **IP/도메인 겸용**: 개발/운영 환경 모두 지원
6. **확장성**: 백엔드 추가/제거 용이

## 📞 문의

- 이메일: piwhyjey@gmail.com
- 도메인: https://yjhome.kro.kr

---

**Happy Networking! 🚀**
