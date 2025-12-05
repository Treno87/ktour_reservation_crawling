# Issue Report: 날짜 범위 크롤링 실패

## 발견 일시
2025-12-05

## 문제 설명
`crawl_date_range()` 함수에서 여러 날짜를 크롤링할 때, 첫 번째 날짜는 성공하지만 두 번째 날짜부터 "날짜 선택기 클릭 실패" 에러가 발생합니다.

## 재현 방법
```python
crawler.crawl_date_range("2025-12-04", "2025-12-05")
```

## 에러 로그
```
2025-12-05 16:09:20,418 - ERROR - 날짜 선택기 클릭 실패: Message:
```

## 근본 원인
`crawler.py`의 `crawl_date_range()` 함수 (line 474-495):

1. **현재 로직**:
   ```python
   def crawl_date_range(self, start_date, end_date):
       current = start
       while current <= end:
           date_str = current.strftime('%Y-%m-%d')
           self.crawl_date(date_str)  # 여기서 문제 발생
           current += timedelta(days=1)
   ```

2. **문제점**:
   - 첫 번째 `crawl_date()`가 끝나면 브라우저는 마지막 팀 상세 페이지 상태
   - `driver.back()`으로 돌아가지만 완전히 초기 상태가 아님
   - 두 번째 `crawl_date()`에서 `click_date_picker()`가 날짜 선택기 요소를 찾지 못함

3. **상태 관리 문제**:
   ```
   [초기 페이지] → [날짜 선택] → [상호 선택] → [팀1 상세]
                                               ↓ back()
                                           [팀 목록]
                                               ↓ back()
                                           [상호 목록??]  ← 여기서 상태 불명확
   ```

## 해결 방안

### Option 1: 홈으로 돌아가기 (권장)
각 날짜 크롤링 시작 전에 메인 페이지로 이동:

```python
def crawl_date_range(self, start_date, end_date):
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        current = start
        while current <= end:
            # 각 날짜마다 메인 페이지로 이동
            self.driver.get(config.BASE_URL)
            time.sleep(config.MEDIUM_DELAY)

            date_str = current.strftime('%Y-%m-%d')
            self.crawl_date(date_str)
            current += timedelta(days=1)

        self.logger.info(f"날짜 범위 크롤링 완료: {start_date} ~ {end_date}")

    except Exception as e:
        self.logger.error(f"날짜 범위 크롤링 실패: {e}")
```

### Option 2: 상태 리셋 함수 추가
페이지 상태를 초기화하는 전용 함수:

```python
def reset_to_home(self):
    """메인 페이지로 돌아가기"""
    try:
        self.driver.get(config.BASE_URL)
        time.sleep(config.MEDIUM_DELAY)
        self.logger.info("메인 페이지로 이동 완료")
    except Exception as e:
        self.logger.error(f"메인 페이지 이동 실패: {e}")
        raise

def crawl_date_range(self, start_date, end_date):
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        current = start
        while current <= end:
            # 상태 리셋
            if current != start:  # 첫 날짜가 아니면
                self.reset_to_home()

            date_str = current.strftime('%Y-%m-%d')
            self.crawl_date(date_str)
            current += timedelta(days=1)

        self.logger.info(f"날짜 범위 크롤링 완료: {start_date} ~ {end_date}")

    except Exception as e:
        self.logger.error(f"날짜 범위 크롤링 실패: {e}")
```

### Option 3: 네비게이션 체인 백트래킹
`crawl_date()` 끝에서 정확히 초기 상태로 돌아가기:

```python
def crawl_date(self, target_date):
    try:
        self.logger.info(f"날짜 크롤링 시작: {target_date}")

        # ... (기존 로직)

        # 각 팀별로 예약 정보 수집
        for team_info in teams:
            try:
                self.click_team(team_info['element'])
                reservation = self.extract_reservation_details(target_date)
                if reservation:
                    self.reservations.append(reservation)

                # 뒤로 가기 (팀 목록으로)
                self.driver.back()
                time.sleep(config.SHORT_DELAY)

            except Exception as e:
                self.logger.error(f"팀 처리 중 오류: {e}")
                continue

        # 모든 팀 처리 후 초기 페이지로 돌아가기
        # 팀 목록 → 상호 선택 → 날짜 선택 → 메인
        self.driver.back()  # 상호 선택 화면으로
        time.sleep(config.SHORT_DELAY)
        self.driver.back()  # 날짜 선택 화면으로 (또는 메인)
        time.sleep(config.SHORT_DELAY)

        self.logger.info(f"날짜 크롤링 완료: {target_date}")

    except Exception as e:
        self.logger.error(f"날짜 크롤링 실패 ({target_date}): {e}")
```

## 권장 수정 사항

**Option 1**을 권장합니다:
- 가장 단순하고 안정적
- 페이지 상태가 명확함
- 약간의 성능 오버헤드가 있지만 안정성이 더 중요

## 구현 우선순위
- Phase 1의 Checkpoint System 구현 시 함께 수정
- 또는 즉시 수정하여 기능 테스트 완료

## 관련 파일
- `crawler.py`: line 474-495 (`crawl_date_range()`)
- `crawler.py`: line 423-472 (`crawl_date()`)

## 테스트 케이스
수정 후 다음 테스트 필요:
1. 단일 날짜 크롤링: `crawl_date("2025-12-04")` ✅ 통과
2. 2일 범위 크롤링: `crawl_date_range("2025-12-04", "2025-12-05")` ❌ 실패
3. 7일 범위 크롤링: `crawl_date_range("2025-12-01", "2025-12-07")`
4. 월 경계 크롤링: `crawl_date_range("2025-11-30", "2025-12-02")`
