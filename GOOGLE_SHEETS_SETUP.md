# 구글 시트 연동 설정 가이드

## 목차
1. [개요](#개요)
2. [구글 클라우드 프로젝트 생성](#구글-클라우드-프로젝트-생성)
3. [서비스 계정 생성](#서비스-계정-생성)
4. [인증 파일 다운로드](#인증-파일-다운로드)
5. [구글 시트 권한 설정](#구글-시트-권한-설정)
6. [설정 확인](#설정-확인)
7. [사용 방법](#사용-방법)
8. [문제 해결](#문제-해결)

---

## 개요

크롤링한 예약 데이터를 구글 시트에 자동으로 저장하고, 예약번호 기준으로 중복을 제거하며 날짜순으로 정렬하는 기능입니다.

### 주요 기능
- ✅ 예약번호 기준 자동 중복 제거
- ✅ 날짜순 자동 정렬
- ✅ 기존 데이터와 병합
- ✅ 헤더 서식 자동 적용

---

## 구글 클라우드 프로젝트 생성

### 1. Google Cloud Console 접속

https://console.cloud.google.com/

### 2. 새 프로젝트 생성

1. 상단의 프로젝트 선택 드롭다운 클릭
2. **새 프로젝트** 클릭
3. 프로젝트 이름 입력 (예: "ktour-crawler")
4. **만들기** 클릭

### 3. API 활성화

1. 좌측 메뉴에서 **API 및 서비스** → **라이브러리** 클릭
2. 다음 API 검색 및 활성화:

**Google Sheets API**
- 검색창에 "Google Sheets API" 입력
- 클릭 → **사용** 버튼 클릭

**Google Drive API**
- 검색창에 "Google Drive API" 입력
- 클릭 → **사용** 버튼 클릭

---

## 서비스 계정 생성

### 1. 서비스 계정 페이지 이동

1. 좌측 메뉴에서 **API 및 서비스** → **사용자 인증 정보** 클릭
2. 상단의 **사용자 인증 정보 만들기** 클릭
3. **서비스 계정** 선택

### 2. 서비스 계정 정보 입력

1. **서비스 계정 이름**: ktour-crawler-sa (또는 원하는 이름)
2. **서비스 계정 ID**: 자동 생성됨
3. **서비스 계정 설명**: KTour 예약 크롤러 (선택사항)
4. **만들기 및 계속하기** 클릭

### 3. 역할 선택 (선택사항)

- 이 단계는 건너뛰어도 됩니다
- **계속** 클릭

### 4. 사용자 액세스 권한

- 이 단계도 건너뛰어도 됩니다
- **완료** 클릭

---

## 인증 파일 다운로드

### 1. 서비스 계정 키 생성

1. 생성된 서비스 계정 목록에서 방금 만든 계정 클릭
2. 상단의 **키** 탭 클릭
3. **키 추가** → **새 키 만들기** 클릭
4. 키 유형: **JSON** 선택
5. **만들기** 클릭

### 2. 파일 저장

- JSON 파일이 자동으로 다운로드됩니다
- 파일명 예시: `ktour-crawler-sa-xxxxxxxxxxxx.json`

### 3. 프로젝트 폴더로 이동

다운로드한 JSON 파일을 프로젝트 루트 디렉토리로 이동:

```bash
# Windows
move C:\Users\YourName\Downloads\ktour-crawler-sa-*.json D:\FullStackDeveloper\ktour_reservation_crawling\credentials.json

# macOS/Linux
mv ~/Downloads/ktour-crawler-sa-*.json /path/to/ktour_reservation_crawling/credentials.json
```

**중요**: 파일명을 정확히 `credentials.json`으로 변경해야 합니다!

---

## 구글 시트 권한 설정

### 1. 구글 시트 생성

1. https://sheets.google.com 접속
2. **+ 새로 만들기** 클릭하여 새 스프레드시트 생성
3. 원하는 이름으로 변경 (예: "KTour 예약 현황")

### 2. 서비스 계정에 편집 권한 부여

1. 구글 시트에서 우측 상단의 **공유** 버튼 클릭
2. 서비스 계정 이메일 주소 입력
   - `credentials.json` 파일을 열어 `client_email` 필드 확인
   - 형식: `ktour-crawler-sa@project-name.iam.gserviceaccount.com`
3. 권한: **편집자** 선택
4. **전송** 클릭

### 3. 스프레드시트 URL 복사

브라우저 주소창의 URL을 복사합니다:
```
https://docs.google.com/spreadsheets/d/1abc...xyz/edit
```

---

## 설정 확인

### 1. credentials.json 파일 확인

프로젝트 루트에 `credentials.json` 파일이 있는지 확인:

```bash
ls credentials.json
```

### 2. config.py 설정 (선택사항)

자동으로 구글 시트에 저장하려면 `config.py` 수정:

```python
# 구글 시트 설정
GOOGLE_SHEETS_ENABLED = True  # True로 변경
GOOGLE_SHEETS_CREDENTIALS = "credentials.json"
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"  # 실제 URL 입력
GOOGLE_SHEETS_WORKSHEET = "예약현황"
```

### 3. 테스트 실행

```bash
python -c "from google_sheets_manager import GoogleSheetsManager; gm = GoogleSheetsManager(); print('인증 성공!' if gm.authenticate() else '인증 실패')"
```

**성공 시 출력:**
```
INFO:google_sheets_manager:구글 시트 인증 성공
인증 성공!
```

---

## 사용 방법

### 방법 1: 웹 인터페이스

1. 웹 인터페이스 실행:
   ```bash
   python web_app.py
   ```

2. 브라우저에서 http://localhost:5000 접속

3. 크롤링 설정 폼에서:
   - ✅ **구글 시트에 자동 저장** 체크박스 선택
   - 구글 시트 URL 입력
   - 크롤링 시작

### 방법 2: CLI (명령줄)

```bash
python main.py \
  --date 2025-12-05 \
  --google-sheets \
  --sheets-url "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
```

### 방법 3: config.py 설정 (자동)

`config.py`에서 `GOOGLE_SHEETS_ENABLED = True`로 설정하면 매번 자동으로 저장:

```bash
python main.py --date 2025-12-05
```

---

## 데이터 구조

### 구글 시트 컬럼

| 컬럼명 | 설명 | 예시 |
|--------|------|------|
| 날짜 | 예약 날짜 | 2025-12-05 |
| 팀 | 팀 정보 | TEAM 1 |
| 고객명 | 고객 이름 | Sara He (1) |
| 예약번호 | 예약 번호 (중복 제거 기준) | KCW680912 |
| 채널 | 예약 채널 약자 | L |
| 인원구분 | 성인/아동/유아 수 | Ad: 1 Kd: 0 Bb: 0 |
| 국가 | 국가명 | NEW ZEALAND |
| 예약상품 | 상품 정보 | PERSONAL STYLE... |
| 예약시간 | 요청 시간 | Time Request: 12:00 |

### 중복 제거 로직

- **기준**: `예약번호` 컬럼
- **방식**: 같은 예약번호가 있으면 최신 데이터만 유지
- **정렬**: 날짜순 오름차순 (과거 → 최신)

---

## 실행 예시

### 예시 1: 오늘 데이터를 구글 시트에 저장

```bash
python main.py \
  --date 2025-12-05 \
  --google-sheets \
  --sheets-url "https://docs.google.com/spreadsheets/d/1abc...xyz/edit"
```

**결과:**
```
INFO - 크롤링 완료: 총 5건의 예약 정보 수집
INFO - 구글 시트에 저장 중...
INFO - 기존 데이터 10건 로드
INFO - 중복 제거 후: 13건
INFO - 날짜순 정렬 완료
INFO - 워크시트 업데이트 완료: 13건
INFO - 구글 시트 저장 완료: https://docs.google.com/...
```

### 예시 2: 한 달치 데이터 누적

```bash
# 첫 번째 실행 (12월 1-10일)
python main.py \
  --start-date 2025-12-01 \
  --end-date 2025-12-10 \
  --google-sheets \
  --sheets-url "https://docs.google.com/..."

# 두 번째 실행 (12월 11-20일)
# 기존 데이터와 자동 병합, 중복 제거
python main.py \
  --start-date 2025-12-11 \
  --end-date 2025-12-20 \
  --google-sheets \
  --sheets-url "https://docs.google.com/..."
```

---

## 문제 해결

### 1. "인증 파일을 찾을 수 없습니다"

**원인:** `credentials.json` 파일이 없거나 경로가 잘못됨

**해결:**
```bash
# 파일 존재 확인
ls credentials.json

# 없으면 다시 다운로드하고 이름 변경
mv ktour-crawler-sa-*.json credentials.json
```

### 2. "Permission denied" 또는 권한 오류

**원인:** 서비스 계정에 구글 시트 편집 권한이 없음

**해결:**
1. 구글 시트 열기
2. **공유** 버튼 클릭
3. 서비스 계정 이메일 추가 (편집자 권한)
4. `credentials.json`의 `client_email` 필드 확인

### 3. "Spreadsheet not found"

**원인:** 스프레드시트 URL이 잘못되었거나 권한이 없음

**해결:**
1. URL 형식 확인:
   ```
   https://docs.google.com/spreadsheets/d/SHEET_ID/edit
   ```
2. 브라우저에서 해당 URL로 접속되는지 확인
3. 서비스 계정에 공유했는지 확인

### 4. 중복이 제거되지 않음

**원인:** 예약번호가 비어있거나 형식이 다름

**확인:**
```python
# 데이터 확인
import pandas as pd
df = pd.read_csv('output/reservations_xxx.csv')
print(df['예약번호'].value_counts())
```

### 5. API 할당량 초과

**원인:** 너무 많은 요청

**해결:**
- 한 번에 크롤링하는 날짜 수를 줄이기
- 요청 간 지연 시간 추가
- Google Cloud Console에서 할당량 확인

---

## 보안 주의사항

### credentials.json 파일 보호

**중요:** 이 파일에는 민감한 인증 정보가 포함되어 있습니다!

1. **.gitignore에 추가되었는지 확인**
   ```bash
   grep credentials.json .gitignore
   ```

2. **GitHub에 업로드하지 않기**
   - 절대 공개 저장소에 커밋하지 마세요
   - `.gitignore`에 포함되어 있는지 확인

3. **파일 권한 설정** (Linux/macOS)
   ```bash
   chmod 600 credentials.json
   ```

4. **백업 시 주의**
   - 클라우드 스토리지에 업로드 시 암호화
   - 로컬 백업만 권장

---

## 고급 설정

### 여러 워크시트 사용

다른 워크시트에 저장하려면:

```python
# config.py
GOOGLE_SHEETS_WORKSHEET = "2025년_12월"  # 워크시트 이름 변경
```

또는 CLI:

```bash
python main.py \
  --date 2025-12-05 \
  --google-sheets \
  --sheets-url "URL"
  # 워크시트명은 config.py에서 설정
```

### 서식 커스터마이징

`google_sheets_manager.py`의 `format_worksheet()` 메서드 수정:

```python
def format_worksheet(self, worksheet):
    # 헤더 배경색 변경
    worksheet.format('1', {
        'backgroundColor': {
            'red': 0.1,    # 빨강
            'green': 0.5,  # 초록
            'blue': 0.2    # 파랑
        },
        # ...
    })
```

---

## FAQ

### Q: 구글 시트와 로컬 파일 둘 다 저장되나요?

**A:** 네, 구글 시트 옵션을 사용해도 로컬 파일(CSV/Excel/JSON)은 그대로 저장됩니다.

### Q: 기존 데이터는 어떻게 되나요?

**A:** 기존 데이터는 유지되고, 새 데이터가 병합됩니다. 예약번호가 중복되면 최신 데이터만 남습니다.

### Q: 여러 상호의 데이터를 하나의 시트에 저장할 수 있나요?

**A:** 네, 가능합니다. 상호별로 크롤링해도 모두 같은 시트에 누적됩니다.

### Q: 인증 파일 없이 사용할 수 있나요?

**A:** 아니요, 서비스 계정 인증 파일은 필수입니다.

### Q: 구글 계정으로 로그인하지 않나요?

**A:** 이 방식은 서비스 계정을 사용하므로 개인 구글 계정 로그인이 필요 없습니다.

---

**최종 업데이트**: 2025-12-05
**버전**: 1.0.0
