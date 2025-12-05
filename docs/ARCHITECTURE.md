# KTour 예약 크롤러 아키텍처 문서

## 목차
1. [시스템 개요](#시스템-개요)
2. [아키텍처 설계](#아키텍처-설계)
3. [컴포넌트 구조](#컴포넌트-구조)
4. [데이터 플로우](#데이터-플로우)
5. [클래스 다이어그램](#클래스-다이어그램)
6. [시퀀스 다이어그램](#시퀀스-다이어그램)
7. [디렉토리 구조](#디렉토리-구조)
8. [확장성 고려사항](#확장성-고려사항)

---

## 시스템 개요

### 목적
KTour 예약 관리 시스템의 예약 현황을 자동으로 수집하고 분석 가능한 형태로 저장하는 웹 크롤링 시스템

### 주요 기능
- 자동 로그인 및 세션 관리
- 날짜별 예약 정보 수집
- 다중 팀 예약 정보 자동 탐색
- 구조화된 데이터 저장 (CSV/Excel/JSON)
- 통계 및 요약 리포트 생성

### 기술 스택
- **언어**: Python 3.8+
- **웹 자동화**: Selenium WebDriver
- **데이터 처리**: Pandas
- **로깅**: Python logging module

---

## 아키텍처 설계

### 레이어 구조

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│                  (main.py - CLI Interface)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Business Logic Layer                    │
│  ┌──────────────────────┐      ┌──────────────────────┐   │
│  │   KTourCrawler       │      │    DataSaver         │   │
│  │   (crawler.py)       │      │  (data_saver.py)     │   │
│  └──────────────────────┘      └──────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Selenium    │  │   Pandas     │  │   Logging    │     │
│  │  WebDriver   │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Persistence Layer                 │
│           (CSV Files, Excel Files, JSON Files)              │
└─────────────────────────────────────────────────────────────┘
```

### 설계 원칙

#### 1. 단일 책임 원칙 (Single Responsibility Principle)
- **KTourCrawler**: 웹 크롤링 로직만 담당
- **DataSaver**: 데이터 저장 및 변환만 담당
- **config.py**: 설정 관리만 담당

#### 2. 관심사의 분리 (Separation of Concerns)
- 크롤링 로직과 데이터 저장 로직을 분리
- 설정과 실행 로직 분리

#### 3. 의존성 역전 원칙 (Dependency Inversion)
- 상위 모듈(main.py)은 하위 모듈의 구체적인 구현에 의존하지 않음
- 인터페이스를 통한 느슨한 결합

---

## 컴포넌트 구조

### 1. Main Controller (main.py)

**책임**:
- 명령줄 인자 파싱
- 컴포넌트 초기화 및 조율
- 전체 워크플로우 관리
- 에러 핸들링 및 리소스 정리

**주요 함수**:
```python
def main():
    """
    - CLI 인자 파싱
    - 크롤러 및 저장소 초기화
    - 크롤링 실행
    - 데이터 저장
    - 통계 출력
    """
```

### 2. Crawler Module (crawler.py)

**책임**:
- WebDriver 설정 및 관리
- 웹 페이지 탐색
- 요소 조작 (클릭, 입력)
- 데이터 추출

**주요 클래스**:
```python
class KTourCrawler:
    """웹 크롤링 엔진"""

    # 초기화 및 설정
    def __init__(headless: bool)
    def setup_driver()

    # 인증
    def login()

    # 네비게이션
    def click_date_picker()
    def select_month(year, month)
    def select_day(day)
    def click_ok_button()
    def click_store(store_name)
    def click_team(team_element)

    # 데이터 수집
    def get_team_list()
    def extract_reservation_details(date)

    # 크롤링 오케스트레이션
    def crawl_date(target_date)
    def crawl_date_range(start_date, end_date)

    # 리소스 관리
    def close()
    def get_reservations()
```

**상태 관리**:
- `driver`: Selenium WebDriver 인스턴스
- `wait`: WebDriverWait 인스턴스
- `reservations`: 수집된 예약 데이터 리스트
- `logger`: 로깅 인스턴스

### 3. Data Persistence Module (data_saver.py)

**책임**:
- 다양한 형식으로 데이터 저장
- 데이터 변환 및 포맷팅
- 통계 생성

**주요 클래스**:
```python
class DataSaver:
    """데이터 저장 및 변환 엔진"""

    # 초기화
    def __init__(output_dir)

    # 저장 기능
    def save_to_csv(data, filename)
    def save_to_excel(data, filename)
    def save_to_json(data, filename)
    def append_to_csv(data, filename)

    # 분석 기능
    def get_summary_statistics(data)
    def save_summary(data, filename)
```

### 4. Configuration Module (config.py)

**책임**:
- 애플리케이션 설정 중앙 관리
- 환경별 설정 분리

**주요 설정**:
```python
# 사이트 정보
BASE_URL
LOGIN_ID
LOGIN_PASSWORD

# 타이밍 설정
IMPLICIT_WAIT
EXPLICIT_WAIT
PAGE_LOAD_TIMEOUT
SHORT_DELAY, MEDIUM_DELAY, LONG_DELAY

# 크롤링 범위
START_DATE
END_DATE

# 출력 설정
OUTPUT_DIR
OUTPUT_FORMAT
```

---

## 데이터 플로우

### 전체 데이터 플로우

```
[사용자 입력]
     │
     ├─→ [명령줄 인자]
     │        │
     │        ▼
     │   [main.py 파싱]
     │        │
     │        ▼
     └─→ [KTourCrawler 초기화]
              │
              ▼
         [WebDriver 설정]
              │
              ▼
         [로그인 수행]
              │
              ▼
    ┌─────[날짜 선택]─────┐
    │                      │
    ▼                      ▼
[단일 날짜]           [날짜 범위]
    │                      │
    └──────┬───────────────┘
           │
           ▼
    [날짜 피커 조작]
           │
           ├─→ [년/월 선택]
           ├─→ [일 선택]
           └─→ [OK 클릭]
           │
           ▼
    [상호 클릭]
           │
           ▼
    [팀 목록 수집]
           │
           ▼
    ┌─────────────┐
    │  각 팀마다  │
    │  ┌────────┐ │
    │  │팀 클릭 │ │
    │  └────────┘ │
    │      │      │
    │      ▼      │
    │ [상세 추출]│
    │      │      │
    │      ▼      │
    │ [데이터 저장]│
    │      │      │
    │      ▼      │
    │  [뒤로가기]│
    └─────────────┘
           │
           ▼
    [reservations 배열]
           │
           ▼
    [DataSaver 전달]
           │
           ├─→ [CSV 저장]
           ├─→ [Excel 저장]
           ├─→ [JSON 저장]
           └─→ [통계 생성]
           │
           ▼
    [파일 시스템 저장]
           │
           ▼
    [사용자에게 결과 표시]
```

### 데이터 구조

#### 예약 데이터 스키마
```python
reservation = {
    'date': str,              # YYYY-MM-DD
    'team': str,              # 팀명 (예: TEAM 1)
    'customer_name': str,     # 고객명
    'reservation_number': str,# 예약번호
    'channel': str,           # 채널 약자
    'people_count': str,      # 인원 (Ad: X Kd: Y Bb: Z)
    'country': str,           # 국가
    'product': str,           # 예약 상품
    'time_request': str       # 예약 시간
}
```

#### 통계 데이터 스키마
```python
summary = {
    'total_count': int,
    'date_range': {
        'start': str,
        'end': str
    },
    'by_date': dict,      # {날짜: 건수}
    'by_team': dict,      # {팀: 건수}
    'by_channel': dict,   # {채널: 건수}
    'by_country': dict    # {국가: 건수}
}
```

---

## 클래스 다이어그램

```
┌─────────────────────────────────────────────────────────┐
│                      KTourCrawler                       │
├─────────────────────────────────────────────────────────┤
│ - driver: WebDriver                                     │
│ - wait: WebDriverWait                                   │
│ - reservations: List[Dict]                              │
│ - logger: Logger                                        │
│ - headless: bool                                        │
├─────────────────────────────────────────────────────────┤
│ + __init__(headless: bool)                              │
│ + setup_driver(): void                                  │
│ + login(): void                                         │
│ + click_date_picker(): void                             │
│ + select_month(year: int, month: int): void             │
│ + select_day(day: int): void                            │
│ + click_ok_button(): void                               │
│ + click_store(store_name: str): void                    │
│ + get_team_list(): List[Dict]                           │
│ + click_team(team_element: WebElement): void            │
│ + extract_reservation_details(date: str): Dict          │
│ + crawl_date(target_date: str): void                    │
│ + crawl_date_range(start: str, end: str): void          │
│ + close(): void                                         │
│ + get_reservations(): List[Dict]                        │
│ - _should_click_next(current: str, target: str): bool   │
└─────────────────────────────────────────────────────────┘
                              │
                              │ uses
                              ▼
┌─────────────────────────────────────────────────────────┐
│                      DataSaver                          │
├─────────────────────────────────────────────────────────┤
│ - output_dir: str                                       │
│ - logger: Logger                                        │
├─────────────────────────────────────────────────────────┤
│ + __init__(output_dir: str)                             │
│ + save_to_csv(data: List, filename: str): str           │
│ + save_to_excel(data: List, filename: str): str         │
│ + save_to_json(data: List, filename: str): str          │
│ + append_to_csv(data: List, filename: str): str         │
│ + get_summary_statistics(data: List): Dict              │
│ + save_summary(data: List, filename: str): str          │
└─────────────────────────────────────────────────────────┘
```

---

## 시퀀스 다이어그램

### 크롤링 프로세스

```
사용자        main.py      KTourCrawler    WebDriver    DataSaver    파일시스템
  │              │              │              │            │            │
  │─ 실행 ────→│              │              │            │            │
  │              │              │              │            │            │
  │              │─ 초기화 ──→│              │            │            │
  │              │              │─ setup ────→│            │            │
  │              │              │              │            │            │
  │              │─ login() ──→│              │            │            │
  │              │              │─ navigate ─→│            │            │
  │              │              │◁─ page ─────│            │            │
  │              │              │              │            │            │
  │              │─crawl_date()→│              │            │            │
  │              │              │─ click ────→│            │            │
  │              │              │─ select ───→│            │            │
  │              │              │              │            │            │
  │              │              │─get_teams()─→│            │            │
  │              │              │◁─ elements ─│            │            │
  │              │              │              │            │            │
  │              │              │─ for each team ────┐     │            │
  │              │              │   │ click team     │     │            │
  │              │              │   │ extract data   │     │            │
  │              │              │   │ back()         │     │            │
  │              │              │◁──────────────────┘     │            │
  │              │              │              │            │            │
  │              │◁get_reservations()          │            │            │
  │              │              │              │            │            │
  │              │─ save() ────────────────────────────→│            │
  │              │              │              │            │─ write ─→│
  │              │              │              │            │◁─ ok ────│
  │              │              │              │            │            │
  │              │◁─ summary ──────────────────────────────│            │
  │◁─ 완료 ────│              │              │            │            │
```

---

## 디렉토리 구조

```
ktour_reservation_crawling/
│
├── docs/                           # 문서 디렉토리
│   ├── ARCHITECTURE.md            # 아키텍처 문서
│   ├── TECH_STACK.md              # 기술 스택 문서
│   └── TASKS.md                   # 태스크 문서
│
├── output/                         # 출력 디렉토리 (자동 생성)
│   ├── reservations_*.csv         # CSV 출력
│   ├── reservations_*.xlsx        # Excel 출력
│   ├── reservations_*.json        # JSON 출력
│   └── summary_*.json             # 통계 파일
│
├── crawler.py                      # 크롤러 메인 모듈
├── data_saver.py                  # 데이터 저장 모듈
├── main.py                        # 실행 진입점
├── config.py                      # 설정 파일
│
├── requirements.txt               # 의존성 패키지
├── .env.example                   # 환경변수 예시
├── .gitignore                     # Git 제외 파일
├── README.md                      # 프로젝트 설명
│
├── info_requirements.md           # 요구사항 명세
└── crawler.log                    # 실행 로그
```

---

## 확장성 고려사항

### 1. 멀티 스토어 지원

**현재 구조**:
```python
def click_store(self, store_name="마리엠헤어"):
    # 하드코딩된 상호명
```

**확장 방안**:
```python
# config.py
STORES = ["마리엠헤어", "스토어2", "스토어3"]

# crawler.py
def crawl_all_stores(self, target_date):
    for store in config.STORES:
        self.click_store(store)
        # ... 크롤링 로직
```

### 2. 병렬 처리

**현재 구조**: 순차적 크롤링

**확장 방안**:
```python
from concurrent.futures import ThreadPoolExecutor

def crawl_date_range_parallel(self, start_date, end_date):
    dates = self._generate_date_list(start_date, end_date)

    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(self.crawl_date, dates)
```

### 3. 데이터베이스 저장

**현재 구조**: 파일 기반 저장

**확장 방안**:
```python
# data_saver.py
class DatabaseSaver(DataSaver):
    def __init__(self, db_connection):
        self.db = db_connection

    def save_to_database(self, data):
        # SQLAlchemy or pymongo 사용
        pass
```

### 4. API 서버화

**확장 방안**:
```python
# app.py (FastAPI)
from fastapi import FastAPI
from crawler import KTourCrawler

app = FastAPI()

@app.post("/crawl")
async def trigger_crawl(date: str):
    crawler = KTourCrawler()
    result = crawler.crawl_date(date)
    return {"status": "success", "data": result}
```

### 5. 스케줄링

**확장 방안**:
```python
# scheduler.py
from apscheduler.schedulers.blocking import BlockingScheduler

def scheduled_crawl():
    crawler = KTourCrawler(headless=True)
    crawler.crawl_date(datetime.now().strftime('%Y-%m-%d'))

scheduler = BlockingScheduler()
scheduler.add_job(scheduled_crawl, 'cron', hour=9)
scheduler.start()
```

### 6. 에러 복구 및 재시도

**확장 방안**:
```python
# retry_decorator.py
from functools import wraps
import time

def retry(max_attempts=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
            return wrapper
    return decorator

# 사용
@retry(max_attempts=3)
def click_element(self, selector):
    # ...
```

### 7. 알림 시스템

**확장 방안**:
```python
# notification.py
class Notifier:
    def send_email(self, subject, body):
        # SMTP 이메일 발송
        pass

    def send_slack(self, message):
        # Slack webhook 발송
        pass

    def send_telegram(self, message):
        # Telegram bot API 사용
        pass
```

---

## 성능 최적화 전략

### 1. 셀렉터 최적화
- CSS 셀렉터보다 ID나 고유 속성 사용
- XPath는 최소화

### 2. 대기 시간 최적화
```python
# 명시적 대기 사용
wait.until(EC.presence_of_element_located((By.ID, "element")))

# 암묵적 대기 최소화
driver.implicitly_wait(2)
```

### 3. 메모리 관리
```python
# 주기적으로 드라이버 재시작
if crawled_count % 100 == 0:
    self.driver.quit()
    self.setup_driver()
```

### 4. 캐싱
```python
# 팀 목록 캐싱
@lru_cache(maxsize=32)
def get_team_list(self, date):
    # ...
```

---

## 보안 고려사항

### 1. 크레덴셜 관리
- `.env` 파일 사용
- 환경변수로 관리
- Git에서 제외

### 2. 로그 필터링
```python
class PasswordFilter(logging.Filter):
    def filter(self, record):
        record.msg = record.msg.replace(config.LOGIN_PASSWORD, '***')
        return True
```

### 3. HTTPS 검증
```python
# SSL 인증서 검증
chrome_options.add_argument('--ignore-certificate-errors')  # 개발 환경만
```

---

## 모니터링 및 로깅

### 로그 레벨
- **DEBUG**: 상세한 디버깅 정보
- **INFO**: 일반적인 실행 흐름
- **WARNING**: 예상치 못한 상황
- **ERROR**: 기능 실패
- **CRITICAL**: 시스템 전체 실패

### 메트릭
- 크롤링 소요 시간
- 성공/실패 건수
- 재시도 횟수
- 메모리 사용량

---

## 테스트 전략

### 1. 단위 테스트
```python
# test_crawler.py
def test_should_click_next():
    crawler = KTourCrawler()
    assert crawler._should_click_next("December 2024", "January 2025") == True
```

### 2. 통합 테스트
```python
def test_login_flow():
    crawler = KTourCrawler(headless=True)
    crawler.setup_driver()
    crawler.login()
    # 로그인 성공 확인
```

### 3. E2E 테스트
```python
def test_full_crawl():
    # 전체 크롤링 프로세스 테스트
    pass
```

---

## 버전 관리 전략

### Semantic Versioning
- **Major**: 하위 호환성 깨지는 변경
- **Minor**: 기능 추가 (하위 호환)
- **Patch**: 버그 수정

### Git 브랜치 전략
- `main`: 프로덕션
- `develop`: 개발
- `feature/*`: 기능 개발
- `hotfix/*`: 긴급 수정

---

이 문서는 프로젝트의 발전에 따라 지속적으로 업데이트됩니다.

**최종 업데이트**: 2025-12-05
**버전**: 1.0.0
