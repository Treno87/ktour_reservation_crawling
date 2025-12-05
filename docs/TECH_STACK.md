# KTour 예약 크롤러 기술 스택 문서

## 목차
1. [개요](#개요)
2. [코어 기술](#코어-기술)
3. [의존성 패키지](#의존성-패키지)
4. [개발 도구](#개발-도구)
5. [배포 환경](#배포-환경)
6. [버전 정보](#버전-정보)
7. [선택 이유](#선택-이유)
8. [대안 기술](#대안-기술)

---

## 개요

이 프로젝트는 Python 기반의 웹 크롤링 애플리케이션으로, Selenium을 활용한 동적 웹 페이지 자동화와 Pandas를 활용한 데이터 처리를 핵심으로 합니다.

---

## 코어 기술

### 1. Python 3.8+

**버전**: 3.8 이상
**공식 사이트**: https://www.python.org/

**선택 이유**:
- 웹 크롤링 및 자동화 라이브러리 생태계가 풍부
- Selenium, Pandas 등 주요 패키지와의 호환성
- 간결하고 읽기 쉬운 문법
- 크로스 플랫폼 지원

**주요 사용 기능**:
- 객체 지향 프로그래밍 (클래스, 메서드)
- 예외 처리 (try-except-finally)
- 타입 힌팅 (Type Hints)
- 리스트 컴프리헨션
- f-string 포매팅
- datetime 모듈을 통한 날짜 처리

---

## 의존성 패키지

### 1. Selenium 4.15.2

**공식 문서**: https://www.selenium.dev/documentation/
**PyPI**: https://pypi.org/project/selenium/

**역할**: 웹 브라우저 자동화 프레임워크

**주요 기능**:
- WebDriver를 통한 브라우저 제어
- 요소 검색 및 조작 (클릭, 입력, 스크롤)
- 명시적/암묵적 대기 (Wait)
- 다양한 셀렉터 지원 (CSS, XPath, ID 등)
- JavaScript 실행 가능

**사용 예시**:
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# WebDriver 초기화
driver = webdriver.Chrome()

# 요소 대기 및 클릭
element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "button"))
)
element.click()
```

**설정 옵션**:
```python
chrome_options = Options()
chrome_options.add_argument('--headless')           # 헤드리스 모드
chrome_options.add_argument('--no-sandbox')         # 샌드박스 비활성화
chrome_options.add_argument('--disable-dev-shm-usage')  # 메모리 최적화
```

---

### 2. WebDriver Manager 4.0.1

**PyPI**: https://pypi.org/project/webdriver-manager/

**역할**: ChromeDriver 자동 다운로드 및 관리

**주요 기능**:
- 브라우저 버전에 맞는 드라이버 자동 설치
- 드라이버 버전 관리
- 크로스 플랫폼 지원

**사용 예시**:
```python
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
```

**장점**:
- 수동 드라이버 다운로드 불필요
- 브라우저 업데이트 시 자동 대응
- 개발 환경 설정 간소화

---

### 3. Pandas 2.1.3

**공식 문서**: https://pandas.pydata.org/
**PyPI**: https://pypi.org/project/pandas/

**역할**: 데이터 분석 및 조작 라이브러리

**주요 기능**:
- DataFrame을 통한 구조화된 데이터 처리
- CSV, Excel, JSON 등 다양한 형식 지원
- 데이터 집계 및 그룹화
- 결측치 처리
- 데이터 변환 및 정제

**사용 예시**:
```python
import pandas as pd

# 리스트를 DataFrame으로 변환
df = pd.DataFrame(data)

# CSV 저장
df.to_csv('output.csv', index=False, encoding='utf-8-sig')

# 그룹별 집계
summary = df.groupby('date').size()
```

**주요 메서드**:
- `DataFrame()`: 데이터프레임 생성
- `to_csv()`: CSV 파일 저장
- `to_excel()`: Excel 파일 저장
- `groupby()`: 그룹화 집계
- `read_csv()`: CSV 파일 읽기

---

### 4. python-dotenv 1.0.0

**PyPI**: https://pypi.org/project/python-dotenv/

**역할**: 환경변수 관리

**주요 기능**:
- `.env` 파일에서 환경변수 로드
- 민감한 정보 보안 관리
- 개발/프로덕션 환경 분리

**사용 예시**:
```python
from dotenv import load_dotenv
import os

load_dotenv()

LOGIN_ID = os.getenv('LOGIN_ID')
LOGIN_PASSWORD = os.getenv('LOGIN_PASSWORD')
```

**.env 파일 예시**:
```bash
LOGIN_ID=user@example.com
LOGIN_PASSWORD=secure_password
START_DATE=2025-12-01
```

---

### 5. openpyxl 3.1.2

**공식 문서**: https://openpyxl.readthedocs.io/
**PyPI**: https://pypi.org/project/openpyxl/

**역할**: Excel 파일 읽기/쓰기 라이브러리

**주요 기능**:
- .xlsx 파일 생성 및 편집
- 셀 스타일링 (폰트, 색상, 테두리)
- 워크시트 관리
- 열 너비 자동 조정

**사용 예시**:
```python
# Pandas와 함께 사용
with pd.ExcelWriter('output.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='Reservations')

    # 열 너비 조정
    worksheet = writer.sheets['Reservations']
    worksheet.column_dimensions['A'].width = 20
```

**지원 형식**:
- `.xlsx` (Excel 2010 이상)
- 수식, 차트, 이미지 지원

---

## Python 표준 라이브러리

### 1. logging

**역할**: 로깅 시스템

**주요 기능**:
```python
import logging

# 기본 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("크롤링 시작")
logger.error("오류 발생", exc_info=True)
```

**로그 레벨**:
- DEBUG (10): 상세 디버깅 정보
- INFO (20): 일반 정보
- WARNING (30): 경고
- ERROR (40): 에러
- CRITICAL (50): 치명적 오류

---

### 2. datetime

**역할**: 날짜 및 시간 처리

**주요 기능**:
```python
from datetime import datetime, timedelta

# 문자열을 날짜로 변환
date_obj = datetime.strptime('2025-12-05', '%Y-%m-%d')

# 날짜 연산
next_day = date_obj + timedelta(days=1)

# 타임스탬프 생성
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
```

---

### 3. os

**역할**: 운영체제 인터페이스

**주요 기능**:
```python
import os

# 디렉토리 생성
if not os.path.exists('output'):
    os.makedirs('output')

# 파일 경로 결합
filepath = os.path.join('output', 'data.csv')

# 환경변수 접근
db_url = os.getenv('DATABASE_URL')
```

---

### 4. argparse

**역할**: 명령줄 인자 파싱

**주요 기능**:
```python
import argparse

parser = argparse.ArgumentParser(description='크롤러')
parser.add_argument('--date', type=str, help='날짜')
parser.add_argument('--headless', action='store_true')

args = parser.parse_args()
```

---

### 5. json

**역할**: JSON 데이터 처리

**주요 기능**:
```python
import json

# 저장
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 로드
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
```

---

## 개발 도구

### 1. Git

**버전**: 2.x
**역할**: 버전 관리 시스템

**주요 사용**:
```bash
git init
git add .
git commit -m "메시지"
git push origin main
```

---

### 2. VS Code (권장 IDE)

**확장 프로그램**:
- Python (Microsoft)
- Pylance
- Python Docstring Generator
- GitLens

**설정**:
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "autopep8"
}
```

---

### 3. pip

**버전**: 최신
**역할**: Python 패키지 관리자

**주요 명령어**:
```bash
# 패키지 설치
pip install -r requirements.txt

# 패키지 업데이트
pip install --upgrade selenium

# 설치된 패키지 목록
pip list

# 패키지 정보
pip show selenium
```

---

## 배포 환경

### 1. 로컬 개발 환경

**요구사항**:
- Windows 10/11 또는 macOS 11+ 또는 Linux
- Python 3.8+
- Chrome 브라우저 최신 버전
- 4GB RAM 이상
- 1GB 이상 디스크 공간

---

### 2. 프로덕션 환경 (서버)

**권장 스펙**:
- Linux (Ubuntu 20.04 LTS+)
- Python 3.9+
- Headless Chrome
- 8GB RAM
- 10GB 디스크 공간

**추가 요구사항**:
```bash
# Ubuntu에서 필요한 패키지
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    chromium-browser \
    chromium-chromedriver \
    xvfb
```

**헤드리스 실행**:
```bash
# Xvfb를 사용한 가상 디스플레이
xvfb-run python main.py --headless
```

---

### 3. Docker (선택사항)

**Dockerfile 예시**:
```dockerfile
FROM python:3.9-slim

# Chrome 설치
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py", "--headless"]
```

**실행**:
```bash
docker build -t ktour-crawler .
docker run -v $(pwd)/output:/app/output ktour-crawler
```

---

## 버전 정보

### 현재 스택 버전

| 패키지 | 버전 | 최신 안정 버전 | 업데이트 필요 |
|--------|------|----------------|---------------|
| Python | 3.8+ | 3.12 | 선택적 |
| selenium | 4.15.2 | 4.16.0 | 아니오 |
| webdriver-manager | 4.0.1 | 4.0.1 | 아니오 |
| pandas | 2.1.3 | 2.1.4 | 선택적 |
| python-dotenv | 1.0.0 | 1.0.0 | 아니오 |
| openpyxl | 3.1.2 | 3.1.2 | 아니오 |

**업데이트 확인**:
```bash
pip list --outdated
```

---

## 선택 이유

### Selenium vs 다른 크롤링 도구

| 도구 | 장점 | 단점 | 선택 이유 |
|------|------|------|-----------|
| **Selenium** | - 동적 페이지 지원<br>- JavaScript 실행<br>- 실제 브라우저 사용 | - 느림<br>- 리소스 많이 사용 | ✅ KTour는 React 기반 SPA |
| BeautifulSoup | - 빠름<br>- 간단함 | - 정적 페이지만 지원<br>- JavaScript 미지원 | ❌ 동적 콘텐츠 처리 불가 |
| Scrapy | - 빠름<br>- 강력한 기능 | - 학습 곡선<br>- 동적 페이지 제한적 | ❌ 과도한 기능 |
| Playwright | - 빠름<br>- 현대적 API | - 상대적으로 신생 | 🔄 대안으로 고려 가능 |

---

### Pandas vs 다른 데이터 처리 도구

| 도구 | 장점 | 단점 | 선택 이유 |
|------|------|------|-----------|
| **Pandas** | - 강력한 기능<br>- 다양한 형식 지원<br>- 생태계 풍부 | - 메모리 사용량 높음 | ✅ 종합적으로 최적 |
| csv 모듈 | - 가벼움<br>- 표준 라이브러리 | - 기능 제한적 | ❌ Excel 지원 부족 |
| polars | - 빠름<br>- 메모리 효율적 | - 생태계 작음 | 🔄 향후 고려 |

---

## 대안 기술

### 1. Playwright (Selenium 대안)

**장점**:
- Selenium보다 빠름
- 현대적인 API
- 네트워크 가로채기 기능
- 자동 대기 기능 향상

**마이그레이션 예시**:
```python
# Selenium
from selenium import webdriver
driver = webdriver.Chrome()
driver.get('https://example.com')

# Playwright
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://example.com')
```

---

### 2. Requests + BeautifulSoup (API 직접 호출)

**사용 시나리오**: API 엔드포인트 발견 시

```python
import requests

# 네트워크 탭에서 발견한 API
response = requests.post(
    'https://guide.ktourstory.com/api/reservations',
    headers={'Authorization': f'Bearer {token}'},
    json={'date': '2025-12-05'}
)

data = response.json()
```

**장점**:
- 훨씬 빠름 (10-100배)
- 리소스 적게 사용
- 안정적

---

### 3. Polars (Pandas 대안)

**벤치마크**:
- Pandas 대비 5-10배 빠름
- 메모리 효율적

```python
import polars as pl

# Pandas
df = pd.DataFrame(data)
df.to_csv('output.csv')

# Polars
df = pl.DataFrame(data)
df.write_csv('output.csv')
```

---

## 성능 및 벤치마크

### 예상 성능 지표

| 작업 | 시간 | 메모리 |
|------|------|--------|
| WebDriver 초기화 | ~3초 | ~100MB |
| 로그인 | ~2초 | - |
| 날짜 선택 | ~1초 | - |
| 예약 1건 추출 | ~2초 | ~1KB |
| CSV 저장 (100건) | ~0.1초 | ~10KB |
| Excel 저장 (100건) | ~0.5초 | ~50KB |

### 최적화 팁

1. **헤드리스 모드 사용**:
   ```python
   crawler = KTourCrawler(headless=True)  # ~30% 빠름
   ```

2. **암묵적 대기 최소화**:
   ```python
   driver.implicitly_wait(2)  # 기본값 10초 → 2초
   ```

3. **선택적 필드만 추출**:
   ```python
   # 필요한 필드만 추출
   fields = ['customer_name', 'reservation_number']
   ```

---

## 라이선스

### 오픈소스 라이선스

| 패키지 | 라이선스 | 상업적 이용 |
|--------|----------|-------------|
| Python | PSF | ✅ 가능 |
| Selenium | Apache 2.0 | ✅ 가능 |
| Pandas | BSD 3-Clause | ✅ 가능 |
| openpyxl | MIT | ✅ 가능 |
| python-dotenv | BSD 3-Clause | ✅ 가능 |

모든 의존성 패키지는 상업적 이용이 가능한 오픈소스 라이선스를 사용합니다.

---

## 보안 고려사항

### 1. 의존성 보안 스캔

```bash
# pip-audit 설치
pip install pip-audit

# 보안 취약점 스캔
pip-audit
```

### 2. 업데이트 정책

- **주요 버전**: 신중하게 테스트 후 업데이트
- **마이너 버전**: 분기별 업데이트 검토
- **패치 버전**: 보안 패치 즉시 적용

### 3. 알려진 취약점

현재 사용 중인 패키지에는 **critical** 등급의 알려진 취약점이 없습니다. (2025-12-05 기준)

---

## 참고 자료

### 공식 문서
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Python Documentation](https://docs.python.org/3/)

### 튜토리얼
- [Real Python - Web Scraping](https://realpython.com/tutorials/web-scraping/)
- [Selenium with Python](https://selenium-python.readthedocs.io/)

### 커뮤니티
- [Stack Overflow - Selenium Tag](https://stackoverflow.com/questions/tagged/selenium)
- [r/webscraping](https://www.reddit.com/r/webscraping/)

---

**최종 업데이트**: 2025-12-05
**문서 버전**: 1.0.0
