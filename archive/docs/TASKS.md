# KTour 예약 크롤러 태스크 및 워크플로우 문서

## 목차
1. [프로젝트 설정](#프로젝트-설정)
2. [실행 워크플로우](#실행-워크플로우)
3. [개발 태스크](#개발-태스크)
4. [운영 태스크](#운영-태스크)
5. [문제 해결](#문제-해결)
6. [유지보수 체크리스트](#유지보수-체크리스트)
7. [배포 프로세스](#배포-프로세스)

---

## 프로젝트 설정

### 초기 설정 태스크

#### Task 1: 개발 환경 준비

**소요 시간**: 10-15분

**체크리스트**:
- [ ] Python 3.8 이상 설치 확인
  ```bash
  python --version
  # 또는
  python3 --version
  ```

- [ ] Chrome 브라우저 설치 확인
  ```bash
  google-chrome --version  # Linux
  # 또는 Windows/Mac에서 브라우저 열어서 확인
  ```

- [ ] Git 설치 확인 (선택사항)
  ```bash
  git --version
  ```

- [ ] IDE 설치 (VS Code 권장)

---

#### Task 2: 프로젝트 클론 또는 다운로드

**방법 A: Git 사용**
```bash
git clone <repository-url>
cd ktour_reservation_crawling
```

**방법 B: 직접 다운로드**
- ZIP 파일 다운로드
- 압축 해제
- 디렉토리로 이동

---

#### Task 3: 가상 환경 설정 (권장)

**소요 시간**: 5분

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**확인**:
```bash
which python  # macOS/Linux
where python  # Windows
# 가상환경 경로가 표시되어야 함
```

---

#### Task 4: 의존성 패키지 설치

**소요 시간**: 3-5분

```bash
pip install -r requirements.txt
```

**확인**:
```bash
pip list
# selenium, pandas, webdriver-manager 등이 목록에 있어야 함
```

**문제 발생 시**:
```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 개별 설치
pip install selenium==4.15.2
pip install pandas==2.1.3
pip install webdriver-manager==4.0.1
pip install python-dotenv==1.0.0
pip install openpyxl==3.1.2
```

---

#### Task 5: 환경 변수 설정

**소요 시간**: 2분

1. `.env.example` 파일을 `.env`로 복사
   ```bash
   cp .env.example .env  # macOS/Linux
   copy .env.example .env  # Windows
   ```

2. `.env` 파일 편집
   ```bash
   # .env
   LOGIN_ID=your_actual_email@example.com
   LOGIN_PASSWORD=your_actual_password
   START_DATE=2025-12-05
   END_DATE=2025-12-31
   ```

3. **중요**: `.env` 파일이 `.gitignore`에 포함되어 있는지 확인

---

#### Task 6: 설정 파일 확인 및 수정

**파일**: `config.py`

**확인 항목**:
```python
# 사이트 URL 확인
BASE_URL = "https://guide.ktourstory.com/"

# 대기 시간 조정 (필요시)
IMPLICIT_WAIT = 10
EXPLICIT_WAIT = 15

# 출력 디렉토리
OUTPUT_DIR = "output"
```

---

#### Task 7: 초기 테스트 실행

**소요 시간**: 2-3분

```bash
# 간단한 테스트
python main.py --date 2025-12-05
```

**예상 결과**:
- 브라우저 창이 열림
- 로그인 시도
- 날짜 선택
- 데이터 수집
- `output/` 디렉토리에 파일 생성

---

## 실행 워크플로우

### 일반 실행 워크플로우

```
시작
  │
  ├─→ [1] 가상환경 활성화
  │     source venv/bin/activate
  │
  ├─→ [2] 설정 확인
  │     - config.py 확인
  │     - .env 파일 확인
  │
  ├─→ [3] 실행 명령어 작성
  │     python main.py [옵션]
  │
  ├─→ [4] 실행
  │
  ├─→ [5] 모니터링
  │     - 로그 확인
  │     - 브라우저 동작 확인
  │
  ├─→ [6] 결과 확인
  │     - output/ 디렉토리 확인
  │     - 로그 파일 확인
  │
  └─→ [7] 후처리
        - 데이터 검증
        - 필요시 재실행
```

---

### 사용 사례별 워크플로우

#### Case 1: 특정 날짜 1일치 크롤링

**목적**: 특정 날짜의 예약 현황만 빠르게 수집

**명령어**:
```bash
python main.py --date 2025-12-05
```

**워크플로우**:
1. 브라우저 시작 (3초)
2. 로그인 (2초)
3. 날짜 선택 (1초)
4. 상호 클릭 (1초)
5. 팀 목록 수집 (2초)
6. 각 팀 상세 크롤링 (팀당 2초)
7. 데이터 저장 (1초)

**예상 소요 시간**: 약 15-30초 (팀 수에 따라 달라짐)

**출력 파일**:
- `output/reservations_20251205_HHMMSS.csv`
- `output/summary_20251205_HHMMSS.json`

---

#### Case 2: 날짜 범위 크롤링

**목적**: 여러 날짜의 예약 현황을 일괄 수집

**명령어**:
```bash
python main.py --start-date 2025-12-01 --end-date 2025-12-31
```

**워크플로우**:
1. 브라우저 시작
2. 로그인
3. **각 날짜마다**:
   - 날짜 선택
   - 데이터 수집
   - 다음 날짜로 이동
4. 전체 데이터 저장

**예상 소요 시간**: 날짜당 15-30초 × 날짜 수
- 30일치: 약 10-15분

**주의사항**:
- 긴 범위는 중간에 끊길 수 있음
- 헤드리스 모드 권장
- 주기적으로 중간 저장 고려

---

#### Case 3: 헤드리스 모드 (서버 환경)

**목적**: 백그라운드에서 자동 실행

**명령어**:
```bash
python main.py --headless --start-date 2025-12-01 --end-date 2025-12-31
```

**장점**:
- GUI 불필요
- 서버에서 실행 가능
- 리소스 절약 (~30%)

**사용 시나리오**:
- cron 스케줄링
- 원격 서버 실행
- CI/CD 파이프라인

---

#### Case 4: Excel 형식으로 저장

**목적**: Excel 형식의 보고서 생성

**명령어**:
```bash
python main.py --date 2025-12-05 --output-format excel --output-file daily_report.xlsx
```

**출력**:
- `output/daily_report.xlsx`
- 자동 열 너비 조정
- 필터 기능 사용 가능

---

#### Case 5: JSON 형식으로 저장 (API 연동용)

**목적**: 다른 시스템과 데이터 연동

**명령어**:
```bash
python main.py --date 2025-12-05 --output-format json
```

**출력**:
```json
[
  {
    "date": "2025-12-05",
    "team": "TEAM 1",
    "customer_name": "Sara He (1)",
    "reservation_number": "KCW680912",
    ...
  }
]
```

---

## 개발 태스크

### 코드 수정 태스크

#### Task: 로그인 셀렉터 수정

**시나리오**: 사이트 구조 변경으로 로그인 실패

**파일**: `crawler.py`

**수정 위치**: `login()` 메서드 (87-120줄)

**절차**:
1. Chrome 개발자 도구 열기 (F12)
2. Elements 탭에서 로그인 필드 확인
3. 셀렉터 복사 (우클릭 → Copy → Copy selector)
4. `crawler.py` 수정:
   ```python
   # 수정 전
   email_input = self.wait.until(
       EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
   )

   # 수정 후 (실제 셀렉터로)
   email_input = self.wait.until(
       EC.presence_of_element_located((By.ID, 'login-email-field'))
   )
   ```
5. 테스트 실행

---

#### Task: 새로운 필드 추가

**시나리오**: 예약 상세에서 추가 정보 수집 필요

**절차**:

1. **데이터 스키마 수정**
   ```python
   # crawler.py - extract_reservation_details()
   reservation = {
       'date': target_date,
       # ... 기존 필드들
       'new_field': '',  # 새 필드 추가
   }
   ```

2. **크롤링 로직 추가**
   ```python
   # 새 필드 추출
   try:
       new_field = self.driver.find_element(
           By.CSS_SELECTOR,
           'span.new-field-class'
       )
       reservation['new_field'] = new_field.text
   except:
       pass
   ```

3. **테스트**
   ```bash
   python main.py --date 2025-12-05
   ```

4. **출력 확인**
   - CSV/Excel에 새 컬럼 추가 확인

---

#### Task: 상호명 동적 설정

**시나리오**: 여러 상호를 크롤링해야 함

**수정 방안**:

1. **config.py 수정**
   ```python
   # 단일 상호
   STORE_NAME = "마리엠헤어"

   # 또는 여러 상호
   STORES = ["마리엠헤어", "다른상호1", "다른상호2"]
   ```

2. **crawler.py 수정**
   ```python
   def crawl_all_stores(self, target_date):
       """모든 상호의 예약 정보 크롤링"""
       for store in config.STORES:
           self.logger.info(f"상호 크롤링: {store}")
           self.click_store(store)
           teams = self.get_team_list()
           # ... 크롤링 로직
   ```

3. **main.py 수정**
   ```python
   # 기존
   crawler.crawl_date(args.date)

   # 수정
   crawler.crawl_all_stores(args.date)
   ```

---

#### Task: 에러 재시도 로직 추가

**시나리오**: 네트워크 오류 시 자동 재시도

**구현**:

1. **데코레이터 생성**
   ```python
   # utils.py (새 파일)
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
                       print(f"재시도 {attempt + 1}/{max_attempts}: {e}")
                       time.sleep(delay)
               return wrapper
       return decorator
   ```

2. **적용**
   ```python
   from utils import retry

   @retry(max_attempts=3, delay=2)
   def click_store(self, store_name):
       # ... 기존 로직
   ```

---

### 테스트 태스크

#### Task: 단위 테스트 작성

**파일**: `test_crawler.py` (새로 생성)

```python
import unittest
from crawler import KTourCrawler

class TestKTourCrawler(unittest.TestCase):

    def test_should_click_next_same_year(self):
        """같은 년도에서 다음 달 클릭 판단 테스트"""
        crawler = KTourCrawler()
        result = crawler._should_click_next("November 2025", "December 2025")
        self.assertTrue(result)

    def test_should_click_next_different_year(self):
        """다른 년도 클릭 판단 테스트"""
        crawler = KTourCrawler()
        result = crawler._should_click_next("December 2024", "January 2025")
        self.assertTrue(result)

    def test_should_click_previous(self):
        """이전 달 클릭 판단 테스트"""
        crawler = KTourCrawler()
        result = crawler._should_click_next("March 2025", "January 2025")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
```

**실행**:
```bash
python -m unittest test_crawler.py
```

---

#### Task: 통합 테스트

**파일**: `test_integration.py`

```python
import unittest
from crawler import KTourCrawler
from data_saver import DataSaver

class TestIntegration(unittest.TestCase):

    def test_full_workflow(self):
        """전체 워크플로우 테스트"""
        crawler = KTourCrawler(headless=True)
        saver = DataSaver()

        try:
            crawler.setup_driver()
            crawler.login()
            crawler.crawl_date("2025-12-05")

            reservations = crawler.get_reservations()
            self.assertGreater(len(reservations), 0, "예약 데이터가 없습니다")

            filepath = saver.save_to_csv(reservations)
            self.assertIsNotNone(filepath, "파일 저장 실패")

        finally:
            crawler.close()

if __name__ == '__main__':
    unittest.main()
```

---

## 운영 태스크

### 정기 실행 태스크

#### Task: Cron 스케줄링 (Linux/macOS)

**목적**: 매일 자동으로 예약 현황 수집

**설정**:
```bash
# crontab 편집
crontab -e

# 매일 오전 9시 실행
0 9 * * * cd /path/to/ktour_reservation_crawling && /path/to/venv/bin/python main.py --headless --date $(date +\%Y-\%m-\%d) >> /path/to/logs/cron.log 2>&1

# 매주 월요일 오전 9시에 한 주치 크롤링
0 9 * * 1 cd /path/to/ktour_reservation_crawling && /path/to/venv/bin/python main.py --headless --start-date $(date +\%Y-\%m-\%d) --end-date $(date -d '+6 days' +\%Y-\%m-\%d) >> /path/to/logs/cron.log 2>&1
```

**확인**:
```bash
# cron 목록 확인
crontab -l

# 로그 확인
tail -f /path/to/logs/cron.log
```

---

#### Task: Windows 작업 스케줄러

**설정 방법**:

1. 작업 스케줄러 열기
2. "기본 작업 만들기" 클릭
3. 이름: "KTour 크롤러"
4. 트리거: "매일" → 시간 설정
5. 작업: "프로그램 시작"
   - 프로그램: `C:\path\to\venv\Scripts\python.exe`
   - 인수: `main.py --headless --date %date:~0,10%`
   - 시작 위치: `C:\path\to\ktour_reservation_crawling`
6. 완료

---

#### Task: 데이터 백업

**일일 백업 스크립트**:
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d)

# output 디렉토리 백업
cp -r output "$BACKUP_DIR/output_$DATE"

# 7일 이상 된 백업 삭제
find "$BACKUP_DIR" -name "output_*" -mtime +7 -exec rm -rf {} \;

echo "백업 완료: $DATE"
```

**실행**:
```bash
chmod +x backup.sh
./backup.sh
```

**Cron 등록**:
```bash
# 매일 오후 11시 백업
0 23 * * * /path/to/backup.sh
```

---

#### Task: 로그 로테이션

**설정**: `logrotate` 사용 (Linux)

```bash
# /etc/logrotate.d/ktour-crawler
/path/to/ktour_reservation_crawling/crawler.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
    create 0644 user user
}
```

**수동 실행**:
```bash
logrotate -f /etc/logrotate.d/ktour-crawler
```

---

### 모니터링 태스크

#### Task: 로그 모니터링

**실시간 로그 확인**:
```bash
tail -f crawler.log
```

**에러만 필터링**:
```bash
grep ERROR crawler.log
```

**오늘 날짜 로그만**:
```bash
grep "2025-12-05" crawler.log
```

**통계**:
```bash
# 크롤링 건수 확인
grep "크롤링 완료" crawler.log | wc -l

# 에러 건수 확인
grep ERROR crawler.log | wc -l
```

---

#### Task: 디스크 공간 모니터링

**확인**:
```bash
# output 디렉토리 크기
du -sh output/

# 파일 개수
ls -l output/ | wc -l
```

**자동 정리 스크립트**:
```bash
#!/bin/bash
# cleanup.sh

# 30일 이상 된 파일 삭제
find output/ -name "*.csv" -mtime +30 -delete
find output/ -name "*.xlsx" -mtime +30 -delete
find output/ -name "*.json" -mtime +30 -delete

echo "정리 완료"
```

---

## 문제 해결

### 일반적인 문제 해결 프로세스

```
문제 발생
    │
    ├─→ [1] 로그 확인
    │     tail -50 crawler.log
    │
    ├─→ [2] 에러 메시지 분석
    │     - TimeoutException?
    │     - NoSuchElementException?
    │     - LoginFailure?
    │
    ├─→ [3] 재현 시도
    │     python main.py --date 2025-12-05
    │
    ├─→ [4] 디버그 모드 실행
    │     - headless=False로 실행
    │     - 브라우저 동작 확인
    │
    ├─→ [5] 해결 방법 적용
    │     - 셀렉터 수정
    │     - 대기 시간 증가
    │     - 로직 수정
    │
    └─→ [6] 테스트 및 검증
```

---

### 문제별 해결 태스크

#### Problem 1: 로그인 실패

**증상**:
```
ERROR - 로그인 실패: Message: no such element: Unable to locate element
```

**해결 Task**:

1. **셀렉터 확인**
   ```bash
   # headless 끄고 실행
   python main.py --date 2025-12-05
   ```

2. **브라우저 개발자 도구 열기** (F12)

3. **로그인 필드 찾기**
   - Elements 탭
   - 이메일 입력 필드 우클릭
   - Copy → Copy selector

4. **crawler.py 수정**
   ```python
   # 87-120줄 login() 메서드
   email_input = self.wait.until(
       EC.presence_of_element_located((By.CSS_SELECTOR, '새로운_셀렉터'))
   )
   ```

5. **테스트**

---

#### Problem 2: Timeout 발생

**증상**:
```
ERROR - TimeoutException: Message:
```

**해결 Task**:

1. **대기 시간 증가**
   ```python
   # config.py
   EXPLICIT_WAIT = 30  # 15 → 30
   IMPLICIT_WAIT = 15  # 10 → 15
   ```

2. **네트워크 속도 확인**

3. **명시적 대기 추가**
   ```python
   # 특정 요소에 더 긴 대기
   from selenium.webdriver.support.ui import WebDriverWait
   long_wait = WebDriverWait(self.driver, 60)
   element = long_wait.until(EC.presence_of_element_located(...))
   ```

---

#### Problem 3: ChromeDriver 버전 불일치

**증상**:
```
selenium.common.exceptions.SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version XX
```

**해결 Task**:

1. **Chrome 버전 확인**
   ```bash
   google-chrome --version
   ```

2. **ChromeDriver 재설치**
   ```bash
   pip uninstall webdriver-manager
   pip install webdriver-manager --upgrade
   ```

3. **캐시 삭제**
   ```bash
   # Linux/macOS
   rm -rf ~/.wdm

   # Windows
   rmdir /s %USERPROFILE%\.wdm
   ```

4. **재실행**

---

#### Problem 4: 데이터가 수집되지 않음

**증상**:
```
INFO - 크롤링 완료: 총 0건의 예약 정보 수집
```

**해결 Task**:

1. **headless 모드 끄기**
   ```bash
   python main.py --date 2025-12-05
   # (--headless 제거)
   ```

2. **브라우저 동작 관찰**
   - 로그인 성공?
   - 날짜 선택 성공?
   - 팀 목록 표시?

3. **로그 상세 확인**
   ```bash
   grep -A 5 "팀 목록" crawler.log
   ```

4. **셀렉터 검증**
   - 개발자 도구에서 요소 확인
   - `get_team_list()` 메서드의 셀렉터 수정

---

#### Problem 5: 메모리 부족

**증상**:
```
MemoryError: Unable to allocate ...
```

**해결 Task**:

1. **헤드리스 모드 사용**
   ```bash
   python main.py --headless
   ```

2. **날짜 범위 축소**
   ```bash
   # 한 달치를 주 단위로 분할
   python main.py --start-date 2025-12-01 --end-date 2025-12-07
   python main.py --start-date 2025-12-08 --end-date 2025-12-14
   ```

3. **주기적 드라이버 재시작**
   ```python
   # crawler.py 수정
   def crawl_date_range(self, start_date, end_date):
       for i, date in enumerate(date_list):
           self.crawl_date(date)

           # 10일마다 재시작
           if (i + 1) % 10 == 0:
               self.driver.quit()
               self.setup_driver()
               self.login()
   ```

---

## 유지보수 체크리스트

### 주간 체크리스트

- [ ] 로그 파일 확인
  ```bash
  tail -100 crawler.log
  ```

- [ ] 에러 발생 여부 확인
  ```bash
  grep ERROR crawler.log | tail -20
  ```

- [ ] 수집 데이터 건수 확인
  ```bash
  wc -l output/*.csv
  ```

- [ ] 디스크 공간 확인
  ```bash
  df -h
  du -sh output/
  ```

---

### 월간 체크리스트

- [ ] 패키지 업데이트 확인
  ```bash
  pip list --outdated
  ```

- [ ] Chrome 버전 확인
  ```bash
  google-chrome --version
  ```

- [ ] 셀렉터 유효성 검증
  - 사이트 구조 변경 여부 확인
  - 테스트 실행

- [ ] 백업 확인
  ```bash
  ls -lh /path/to/backups/
  ```

- [ ] 로그 아카이브
  ```bash
  gzip crawler.log.old
  mv crawler.log.old.gz archive/
  ```

---

### 분기별 체크리스트

- [ ] 보안 패치 확인
  ```bash
  pip-audit
  ```

- [ ] 성능 테스트
  - 크롤링 소요 시간 측정
  - 최적화 필요 여부 판단

- [ ] 코드 리뷰
  - 불필요한 코드 제거
  - 리팩토링 기회 검토

- [ ] 문서 업데이트
  - README.md
  - ARCHITECTURE.md
  - TECH_STACK.md
  - TASKS.md

---

## 배포 프로세스

### 로컬 개발 → 프로덕션 배포

#### Phase 1: 로컬 테스트

```bash
# 1. 가상환경 활성화
source venv/bin/activate

# 2. 최신 코드로 업데이트
git pull origin main

# 3. 의존성 업데이트
pip install -r requirements.txt --upgrade

# 4. 테스트 실행
python main.py --date $(date +%Y-%m-%d)

# 5. 결과 확인
ls -lh output/
```

---

#### Phase 2: 서버 배포 (SSH)

```bash
# 1. 서버 접속
ssh user@server-ip

# 2. 프로젝트 디렉토리로 이동
cd /opt/ktour_reservation_crawling

# 3. 최신 코드 가져오기
git pull origin main

# 4. 가상환경 활성화
source venv/bin/activate

# 5. 의존성 업데이트
pip install -r requirements.txt

# 6. 테스트 실행 (헤드리스)
python main.py --headless --date $(date +%Y-%m-%d)

# 7. Cron 재시작 (필요시)
sudo systemctl restart cron
```

---

#### Phase 3: Docker 배포

**빌드**:
```bash
# 이미지 빌드
docker build -t ktour-crawler:latest .

# 태그 추가
docker tag ktour-crawler:latest myrepo/ktour-crawler:1.0.0
```

**푸시**:
```bash
# Docker Hub에 푸시
docker push myrepo/ktour-crawler:1.0.0
```

**서버에서 실행**:
```bash
# 이미지 가져오기
docker pull myrepo/ktour-crawler:1.0.0

# 실행
docker run -d \
  --name ktour-crawler \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/.env:/app/.env \
  myrepo/ktour-crawler:1.0.0
```

---

## 긴급 대응 프로세스

### 크롤러 작동 중지 시

**1단계: 문제 확인**
```bash
# 로그 확인
tail -50 crawler.log

# 프로세스 확인
ps aux | grep python
```

**2단계: 긴급 재시작**
```bash
# 프로세스 종료
pkill -f "python main.py"

# 재시작
nohup python main.py --headless --date $(date +%Y-%m-%d) &
```

**3단계: 모니터링**
```bash
# 로그 실시간 확인
tail -f crawler.log
```

**4단계: 관리자 알림**
- 이메일 발송
- Slack 메시지
- SMS (심각한 경우)

---

## 스크립트 모음

### 유틸리티 스크립트

**health_check.sh**:
```bash
#!/bin/bash
# 크롤러 상태 확인

LOG_FILE="crawler.log"
OUTPUT_DIR="output"

echo "=== KTour Crawler Health Check ==="
echo ""

# 최근 로그 확인
echo "최근 로그 (5줄):"
tail -5 $LOG_FILE
echo ""

# 에러 확인
ERROR_COUNT=$(grep ERROR $LOG_FILE | wc -l)
echo "총 에러 건수: $ERROR_COUNT"
echo ""

# 오늘 수집 건수
TODAY=$(date +%Y-%m-%d)
TODAY_FILES=$(ls -1 $OUTPUT_DIR/*$TODAY* 2>/dev/null | wc -l)
echo "오늘 생성된 파일: $TODAY_FILES개"
echo ""

# 디스크 사용량
echo "디스크 사용량:"
du -sh $OUTPUT_DIR
echo ""

echo "=== Health Check 완료 ==="
```

**실행**:
```bash
chmod +x health_check.sh
./health_check.sh
```

---

**최종 업데이트**: 2025-12-05
**문서 버전**: 1.0.0
