# 테스트 가이드

## 📋 개요

개선 작업을 시작하기 전에 **현재 코드가 정상 동작하는지** 반드시 확인해야 합니다.
이 문서는 단계별 테스트 절차와 체크리스트를 제공합니다.

---

## 🎯 테스트 목표

1. ✅ 현재 코드의 정상 동작 확인
2. ✅ 각 기능별 독립 테스트
3. ✅ 통합 시나리오 테스트
4. ✅ 문제점 사전 파악

---

## 📝 사전 준비 체크리스트

### 환경 설정 확인

- [ ] Python 버전 확인
  ```bash
  python --version
  # 예상 출력: Python 3.8.x 이상
  ```

- [ ] 패키지 설치 확인
  ```bash
  pip list | grep -E "(selenium|pandas|flask|gspread)"
  # 모든 패키지가 설치되어 있어야 함
  ```

- [ ] 인증 파일 확인
  ```bash
  ls credentials.json
  # 구글 시트 사용 시 필수
  ```

- [ ] 설정 파일 확인
  ```bash
  cat config.py
  # LOGIN_ID, LOGIN_PASSWORD 확인
  ```

---

## 🧪 Level 1: 기본 기능 테스트 (필수)

### Test 1.1: 패키지 임포트 테스트

**목적**: 모든 모듈이 정상적으로 임포트되는지 확인

**실행**:
```bash
python -c "
from crawler import KTourCrawler
from data_saver import DataSaver
from google_sheets_manager import GoogleSheetsManager
import config
print('✅ 모든 모듈 임포트 성공')
"
```

**예상 결과**:
```
✅ 모든 모듈 임포트 성공
```

**실패 시 조치**:
- ImportError 발생 → 해당 패키지 설치 확인
- SyntaxError 발생 → 파이썬 버전 확인

---

### Test 1.2: WebDriver 초기화 테스트

**목적**: Selenium WebDriver가 정상적으로 실행되는지 확인

**테스트 스크립트**: `tests/test_webdriver.py`
```python
"""WebDriver 초기화 테스트"""
import sys
from crawler import KTourCrawler

def test_webdriver_setup():
    print("WebDriver 초기화 테스트 시작...")

    try:
        # 크롤러 초기화
        crawler = KTourCrawler(headless=True)
        print("✓ 크롤러 객체 생성 성공")

        # WebDriver 설정
        crawler.setup_driver()
        print("✓ WebDriver 설정 성공")

        # 테스트 페이지 접속
        crawler.driver.get("https://www.google.com")
        print("✓ 테스트 페이지 접속 성공")

        # 브라우저 종료
        crawler.close()
        print("✓ 브라우저 종료 성공")

        print("\n✅ WebDriver 초기화 테스트 통과")
        return True

    except Exception as e:
        print(f"\n❌ WebDriver 초기화 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    success = test_webdriver_setup()
    sys.exit(0 if success else 1)
```

**실행**:
```bash
python tests/test_webdriver.py
```

**예상 소요 시간**: 10-15초

**실패 시 조치**:
- ChromeDriver 관련 에러 → Chrome 브라우저 업데이트
- Timeout 에러 → 인터넷 연결 확인

---

### Test 1.3: 로그인 테스트

**목적**: KTour 사이트 로그인이 정상 작동하는지 확인

**⚠️ 주의**: 실제 사이트에 접속하므로 신중히 진행

**테스트 스크립트**: `tests/test_login.py`
```python
"""로그인 기능 테스트"""
import sys
import time
from crawler import KTourCrawler
import config

def test_login():
    print("로그인 테스트 시작...")
    print(f"사이트: {config.BASE_URL}")
    print(f"계정: {config.LOGIN_ID}")

    crawler = None

    try:
        # 크롤러 초기화
        crawler = KTourCrawler(headless=False)  # 화면 보면서 테스트
        crawler.setup_driver()
        print("✓ WebDriver 설정 완료")

        # 로그인 시도
        crawler.login()
        print("✓ 로그인 완료")

        # 3초 대기 (로그인 화면 확인)
        time.sleep(3)

        # 현재 URL 확인
        current_url = crawler.driver.current_url
        print(f"✓ 현재 URL: {current_url}")

        # 로그인 성공 여부 확인
        # (로그인 후 URL이 변경되거나 특정 요소가 나타나는지 확인)
        if "login" in current_url.lower():
            print("⚠️  경고: 여전히 로그인 페이지에 있습니다")
            print("    로그인 정보를 확인하세요")
            return False
        else:
            print("✓ 로그인 성공으로 판단됨")

        print("\n✅ 로그인 테스트 통과")
        return True

    except Exception as e:
        print(f"\n❌ 로그인 테스트 실패: {e}")
        print("\n디버깅 정보:")
        if crawler and crawler.driver:
            print(f"  현재 URL: {crawler.driver.current_url}")
            print(f"  페이지 제목: {crawler.driver.title}")

            # 스크린샷 저장
            screenshot_path = "logs/login_error.png"
            crawler.driver.save_screenshot(screenshot_path)
            print(f"  스크린샷 저장: {screenshot_path}")

        return False

    finally:
        if crawler:
            # 10초 대기 (화면 확인용)
            print("\n화면을 확인하세요. 10초 후 브라우저가 닫힙니다...")
            time.sleep(10)
            crawler.close()

if __name__ == "__main__":
    success = test_login()
    sys.exit(0 if success else 1)
```

**실행**:
```bash
python tests/test_login.py
```

**예상 소요 시간**: 15-20초

**체크 포인트**:
- [ ] 브라우저가 열리는가?
- [ ] 로그인 페이지가 로드되는가?
- [ ] 이메일/비밀번호가 자동 입력되는가?
- [ ] 로그인 버튼이 클릭되는가?
- [ ] 로그인 후 메인 페이지로 이동하는가?

**실패 시 조치**:
1. `logs/login_error.png` 스크린샷 확인
2. `config.py`의 LOGIN_ID, LOGIN_PASSWORD 확인
3. 셀렉터가 변경되었는지 확인 (개발자 도구 F12)

---

## 🧪 Level 2: 크롤링 기능 테스트 (필수)

### Test 2.1: 단일 날짜 크롤링 테스트

**목적**: 오늘 날짜의 예약 정보를 정상적으로 크롤링하는지 확인

**테스트 스크립트**: `tests/test_single_date.py`
```python
"""단일 날짜 크롤링 테스트"""
import sys
from datetime import datetime
from crawler import KTourCrawler
from data_saver import DataSaver
import config

def test_single_date_crawling():
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"단일 날짜 크롤링 테스트 시작: {today}")

    crawler = None

    try:
        # 크롤러 초기화
        crawler = KTourCrawler(headless=False)
        crawler.setup_driver()
        print("✓ WebDriver 설정 완료")

        # 로그인
        crawler.login()
        print("✓ 로그인 완료")

        # 크롤링
        crawler.crawl_date(today)
        print("✓ 크롤링 완료")

        # 결과 확인
        reservations = crawler.get_reservations()
        print(f"✓ 수집된 예약: {len(reservations)}건")

        if len(reservations) > 0:
            print("\n첫 번째 예약 샘플:")
            print(reservations[0])
        else:
            print("\n⚠️  예약 데이터가 없습니다")
            print("    (오늘 예약이 없을 수도 있습니다)")

        # 데이터 저장 테스트
        saver = DataSaver()
        saved_file = saver.save_to_csv(reservations, f"test_{today}.csv")
        print(f"✓ 파일 저장: {saved_file}")

        print("\n✅ 단일 날짜 크롤링 테스트 통과")
        return True

    except Exception as e:
        print(f"\n❌ 단일 날짜 크롤링 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if crawler:
            crawler.close()

if __name__ == "__main__":
    success = test_single_date_crawling()
    sys.exit(0 if success else 1)
```

**실행**:
```bash
python tests/test_single_date.py
```

**예상 소요 시간**: 30-60초

**체크 포인트**:
- [ ] 로그인 성공
- [ ] 날짜 선택 성공
- [ ] 상호 클릭 성공
- [ ] 팀 목록 수집 성공
- [ ] 예약 상세 추출 성공
- [ ] CSV 파일 생성 성공

---

### Test 2.2: 데이터 저장 테스트

**목적**: CSV, Excel, JSON 저장이 정상 작동하는지 확인

**테스트 스크립트**: `tests/test_data_saver.py`
```python
"""데이터 저장 기능 테스트"""
import sys
from data_saver import DataSaver

def test_data_saver():
    print("데이터 저장 테스트 시작...")

    # 샘플 데이터
    sample_data = [
        {
            'date': '2025-12-05',
            'team': 'TEAM 1',
            'customer_name': 'Test Customer (1)',
            'reservation_number': 'TEST123',
            'channel': 'T',
            'people_count': 'Ad: 1 Kd: 0 Bb: 0',
            'country': 'KOREA',
            'product': 'Test Product',
            'time_request': '12:00'
        }
    ]

    saver = DataSaver()

    try:
        # CSV 저장 테스트
        csv_file = saver.save_to_csv(sample_data, "test_output.csv")
        print(f"✓ CSV 저장 성공: {csv_file}")

        # Excel 저장 테스트
        excel_file = saver.save_to_excel(sample_data, "test_output.xlsx")
        print(f"✓ Excel 저장 성공: {excel_file}")

        # JSON 저장 테스트
        json_file = saver.save_to_json(sample_data, "test_output.json")
        print(f"✓ JSON 저장 성공: {json_file}")

        # 통계 생성 테스트
        summary = saver.get_summary_statistics(sample_data)
        print(f"✓ 통계 생성 성공: {summary}")

        print("\n✅ 데이터 저장 테스트 통과")
        return True

    except Exception as e:
        print(f"\n❌ 데이터 저장 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_saver()
    sys.exit(0 if success else 1)
```

**실행**:
```bash
python tests/test_data_saver.py
```

**확인 사항**:
- [ ] `output/test_output.csv` 생성됨
- [ ] `output/test_output.xlsx` 생성됨
- [ ] `output/test_output.json` 생성됨
- [ ] 파일을 열어서 데이터 확인

---

## 🧪 Level 3: 구글 시트 테스트 (선택)

### Test 3.1: 구글 시트 인증 테스트

**목적**: 구글 시트 API 인증이 정상 작동하는지 확인

**전제 조건**:
- [ ] `credentials.json` 파일 존재
- [ ] 구글 시트 생성 완료
- [ ] 서비스 계정에 편집 권한 부여

**테스트 스크립트**: `tests/test_google_sheets.py`
```python
"""구글 시트 연동 테스트"""
import sys
from google_sheets_manager import GoogleSheetsManager
import config

def test_google_sheets():
    print("구글 시트 연동 테스트 시작...")

    # 샘플 데이터
    sample_data = [
        {
            'date': '2025-12-05',
            'team': 'TEAM 1',
            'customer_name': 'Test Customer (1)',
            'reservation_number': 'TEST123',
            'channel': 'T',
            'people_count': 'Ad: 1 Kd: 0 Bb: 0',
            'country': 'KOREA',
            'product': 'Test Product',
            'time_request': '12:00'
        }
    ]

    try:
        # 인증 테스트
        manager = GoogleSheetsManager()
        auth_success = manager.authenticate()

        if not auth_success:
            print("❌ 구글 시트 인증 실패")
            return False

        print("✓ 구글 시트 인증 성공")

        # 스프레드시트 열기 테스트
        sheets_url = config.GOOGLE_SHEETS_URL
        if not sheets_url:
            print("⚠️  GOOGLE_SHEETS_URL이 설정되지 않았습니다")
            print("    config.py에서 설정하세요")
            return False

        print(f"✓ 스프레드시트 URL: {sheets_url}")

        spreadsheet = manager.open_sheet(sheets_url)
        if not spreadsheet:
            print("❌ 스프레드시트 열기 실패")
            return False

        print(f"✓ 스프레드시트 열기 성공: {spreadsheet.title}")

        # 워크시트 확인
        worksheet = manager.get_or_create_worksheet(
            spreadsheet,
            config.GOOGLE_SHEETS_WORKSHEET
        )
        print(f"✓ 워크시트 확인: {worksheet.title}")

        # 테스트 데이터 저장
        print("테스트 데이터 저장 중...")
        success = manager.append_data(
            sheets_url,
            sample_data,
            config.GOOGLE_SHEETS_WORKSHEET
        )

        if success:
            print(f"✓ 테스트 데이터 저장 성공")
            print(f"✓ 구글 시트 확인: {sheets_url}")
        else:
            print("❌ 테스트 데이터 저장 실패")
            return False

        print("\n✅ 구글 시트 연동 테스트 통과")
        return True

    except FileNotFoundError as e:
        print(f"❌ credentials.json 파일을 찾을 수 없습니다: {e}")
        print("\n해결 방법:")
        print("1. Google Cloud Console에서 서비스 계정 생성")
        print("2. JSON 키 다운로드")
        print("3. 프로젝트 루트에 credentials.json으로 저장")
        return False

    except Exception as e:
        print(f"\n❌ 구글 시트 연동 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_google_sheets()
    sys.exit(0 if success else 1)
```

**실행**:
```bash
python tests/test_google_sheets.py
```

**확인 사항**:
- [ ] 인증 성공
- [ ] 스프레드시트 열림
- [ ] 워크시트 생성/확인
- [ ] 테스트 데이터 저장 성공
- [ ] 실제 구글 시트에서 데이터 확인

---

## 🧪 Level 4: 웹 인터페이스 테스트 (선택)

### Test 4.1: 웹 서버 시작 테스트

**목적**: Flask 웹 서버가 정상 시작되는지 확인

**실행**:
```bash
python web_app.py
```

**예상 출력**:
```
============================================================
KTour 예약 크롤러 웹 인터페이스
============================================================

브라우저에서 http://localhost:5000 접속하세요

 * Running on http://0.0.0.0:5000
```

**체크 포인트**:
- [ ] 에러 없이 서버 시작
- [ ] 브라우저에서 http://localhost:5000 접속 가능
- [ ] 메인 페이지 로드됨
- [ ] 폼 필드가 정상 표시됨

**테스트 시나리오**:
1. 오늘 날짜로 빠른 시작 버튼 클릭
2. 진행 상황 실시간 확인
3. 완료 후 결과 다운로드
4. 파일 목록에서 다운로드

---

## 📊 통합 테스트 시나리오

### Scenario 1: 전체 워크플로우 테스트

**목적**: 실제 업무 시나리오 시뮬레이션

**단계**:
1. CLI로 3일치 크롤링
   ```bash
   python main.py --start-date 2025-12-05 --end-date 2025-12-07
   ```

2. 결과 확인
   ```bash
   ls -lh output/
   ```

3. 구글 시트 저장 테스트 (설정 완료 시)
   ```bash
   python main.py --date 2025-12-05 --google-sheets --sheets-url "YOUR_URL"
   ```

4. 웹 UI로 동일 작업 수행
   - 웹 서버 시작
   - 브라우저에서 크롤링
   - 구글 시트 옵션 테스트

**예상 소요 시간**: 10-15분

---

## 📋 최종 테스트 체크리스트

### 필수 테스트 (반드시 통과해야 함)

- [ ] **Test 1.1**: 패키지 임포트 ✅
- [ ] **Test 1.2**: WebDriver 초기화 ✅
- [ ] **Test 1.3**: 로그인 ✅
- [ ] **Test 2.1**: 단일 날짜 크롤링 ✅
- [ ] **Test 2.2**: 데이터 저장 ✅

### 선택 테스트 (구글 시트 사용 시)

- [ ] **Test 3.1**: 구글 시트 인증 ✅
- [ ] **Test 3.1**: 구글 시트 저장 ✅

### 선택 테스트 (웹 UI 사용 시)

- [ ] **Test 4.1**: 웹 서버 시작 ✅
- [ ] **Test 4.2**: 웹 UI 크롤링 ✅

---

## 🐛 문제 발견 시 대응

### 문제 기록 템플릿

```markdown
## 발견된 문제

**테스트**: Test X.X - [테스트명]
**일시**: 2025-12-05 14:30
**증상**: [문제 설명]

**에러 메시지**:
```
[에러 로그 복사]
```

**스크린샷**: logs/error_xxx.png

**재현 방법**:
1. [단계 1]
2. [단계 2]

**임시 해결 방법**: [있다면 기록]

**근본 원인**: [분석 후 기록]

**해결 계획**: [해결 방법]
```

### 문제 우선순위

| 우선순위 | 설명 | 대응 |
|---------|------|------|
| 🔴 Critical | 프로그램 실행 불가 | 즉시 해결 필요 |
| 🟡 High | 주요 기능 동작 안 함 | 24시간 내 해결 |
| 🟢 Medium | 일부 기능 오작동 | 1주 내 해결 |
| ⚪ Low | 사소한 버그 | 여유 시 해결 |

---

## 📝 테스트 결과 보고서 템플릿

```markdown
# 테스트 결과 보고서

**테스트 일시**: 2025-12-05
**테스터**: [이름]
**환경**: Windows 10 / Python 3.9

## 테스트 요약

- 총 테스트: 7개
- 통과: 6개 ✅
- 실패: 1개 ❌
- 건너뜀: 0개

## 상세 결과

### ✅ 통과한 테스트
- Test 1.1: 패키지 임포트
- Test 1.2: WebDriver 초기화
- Test 1.3: 로그인
- Test 2.1: 단일 날짜 크롤링
- Test 2.2: 데이터 저장
- Test 3.1: 구글 시트 인증

### ❌ 실패한 테스트
- Test 4.1: 웹 서버 시작
  - 원인: Flask 미설치
  - 해결: pip install flask

## 결론

현재 코드는 **정상 동작**합니다.
Phase 1 개선 작업을 시작해도 됩니다.

## 다음 단계

1. Git 브랜치 생성
2. Task 1.1 시작 (셀렉터 중앙 관리)
```

---

## 🚀 테스트 완료 후

### 모든 테스트 통과 시

축하합니다! 개선 작업을 시작할 준비가 되었습니다.

**다음 단계**:
1. `docs/IMPROVEMENT_ROADMAP.md` 문서 확인
2. Git 브랜치 생성: `git checkout -b feature/phase1-stability`
3. Task 1.1 시작

### 일부 테스트 실패 시

개선 작업을 시작하기 전에 문제를 해결하세요.

**대응 방법**:
1. 실패한 테스트 상세 분석
2. 로그 및 스크린샷 확인
3. 문제 해결 후 재테스트
4. 모든 테스트 통과 확인

---

**작성일**: 2025-12-05
**버전**: 1.0.0
