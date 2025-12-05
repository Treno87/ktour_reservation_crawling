# KTour 예약 현황 크롤러

KTour 사이트의 예약 현황을 자동으로 크롤링하는 Python 프로젝트입니다.

## 주요 기능

- 자동 로그인
- 날짜별 예약 정보 수집
- 팀별 예약 상세 정보 추출
- CSV, Excel, JSON 형식으로 데이터 저장
- 요약 통계 생성
- 로깅 기능

## 설치 방법

### 1. 필수 요구사항

- Python 3.8 이상
- Chrome 브라우저

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

## 사용 방법

### 1. 설정 파일 수정

`config.py` 파일에서 필요한 설정을 수정합니다:

- 로그인 정보 (보안을 위해 환경변수 사용 권장)
- 크롤링할 날짜 범위
- 출력 디렉토리 등

### 2. 실행

#### 기본 실행 (config.py의 날짜 범위 사용)

```bash
python main.py
```

#### 특정 날짜 크롤링

```bash
python main.py --date 2025-12-05
```

#### 날짜 범위 크롤링

```bash
python main.py --start-date 2025-12-01 --end-date 2025-12-31
```

#### 출력 형식 지정

```bash
# CSV 출력 (기본값)
python main.py --date 2025-12-05 --output-format csv

# Excel 출력
python main.py --date 2025-12-05 --output-format excel

# JSON 출력
python main.py --date 2025-12-05 --output-format json
```

#### 헤드리스 모드 실행

```bash
python main.py --headless
```

#### 출력 파일명 지정

```bash
python main.py --date 2025-12-05 --output-file my_reservations.csv
```

### 3. 명령줄 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--date` | 단일 날짜 크롤링 (YYYY-MM-DD) | `--date 2025-12-05` |
| `--start-date` | 시작 날짜 (YYYY-MM-DD) | `--start-date 2025-12-01` |
| `--end-date` | 종료 날짜 (YYYY-MM-DD) | `--end-date 2025-12-31` |
| `--headless` | 헤드리스 모드 실행 | `--headless` |
| `--output-format` | 출력 형식 (csv, excel, json) | `--output-format excel` |
| `--output-file` | 출력 파일명 | `--output-file result.csv` |

## 프로젝트 구조

```
ktour_reservation_crawling/
├── crawler.py              # 메인 크롤러 클래스
├── data_saver.py          # 데이터 저장 모듈
├── main.py                # 실행 스크립트
├── config.py              # 설정 파일
├── requirements.txt       # 필수 패키지 목록
├── info_requirements.md   # 사이트 정보 및 요구사항
├── README.md              # 프로젝트 설명서
├── output/                # 출력 디렉토리 (자동 생성)
│   ├── reservations_*.csv
│   ├── reservations_*.xlsx
│   ├── reservations_*.json
│   └── summary_*.json
└── crawler.log            # 로그 파일

```

## 출력 데이터 형식

### 예약 정보 필드

| 필드 | 설명 |
|------|------|
| date | 예약 날짜 |
| team | 팀 정보 |
| customer_name | 고객명 |
| reservation_number | 예약번호 |
| channel | 채널 약자 |
| people_count | 인원구분 및 수 (Ad/Kd/Bb) |
| country | 국가 |
| product | 예약 상품 |
| time_request | 예약 시간 |

### 요약 통계

`summary_*.json` 파일에는 다음 정보가 포함됩니다:

- 총 예약 건수
- 날짜 범위
- 날짜별 예약 건수
- 팀별 예약 건수
- 채널별 예약 건수
- 국가별 예약 건수

## 주의사항

### 1. 로그인 정보 보안

`config.py`에 직접 로그인 정보를 저장하는 것은 보안상 권장되지 않습니다. 환경변수나 `.env` 파일을 사용하는 것이 좋습니다.

**.env 파일 사용 예시:**

```bash
# .env 파일 생성
LOGIN_ID=your_email@example.com
LOGIN_PASSWORD=your_password
```

```python
# config.py에서 환경변수 사용
import os
from dotenv import load_dotenv

load_dotenv()

LOGIN_ID = os.getenv('LOGIN_ID')
LOGIN_PASSWORD = os.getenv('LOGIN_PASSWORD')
```

### 2. 크롤링 속도

서버에 과도한 부하를 주지 않도록 적절한 지연 시간을 설정하세요. `config.py`의 `SHORT_DELAY`, `MEDIUM_DELAY`, `LONG_DELAY` 값을 조정할 수 있습니다.

### 3. 법적 고려사항

- 웹사이트의 이용약관을 확인하세요
- robots.txt를 준수하세요
- 과도한 요청으로 서비스에 부담을 주지 마세요

### 4. 셀렉터 변경

웹사이트의 HTML 구조가 변경되면 `crawler.py`의 CSS 셀렉터를 업데이트해야 할 수 있습니다.

## 트러블슈팅

### 로그인 실패

- 로그인 정보가 올바른지 확인
- 로그인 페이지의 HTML 구조가 변경되었는지 확인
- `crawler.py`의 `login()` 메서드에서 셀렉터 확인

### 요소를 찾을 수 없음

- 페이지 로딩 시간이 충분한지 확인
- `config.py`의 대기 시간 값을 증가
- CSS 셀렉터가 올바른지 확인

### ChromeDriver 오류

```bash
# ChromeDriver 재설치
pip uninstall webdriver-manager
pip install webdriver-manager
```

## 로그 확인

`crawler.log` 파일에서 상세한 실행 로그를 확인할 수 있습니다.

## 라이선스

이 프로젝트는 교육 및 개인 사용 목적으로 제작되었습니다.

## 개발 정보

- Python 3.8+
- Selenium 4.15.2
- Chrome WebDriver

## 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.
