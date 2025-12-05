# 프로젝트 개선 로드맵

## 📋 문서 정보

**작성일**: 2025-12-05
**버전**: 1.0.0
**대상**: KTour 예약 크롤러 프로젝트
**목적**: 안정성, 성능, 유지보수성 개선

---

## 🎯 개선 목표

| 항목 | 현재 | 목표 | 개선률 |
|------|------|------|--------|
| 안정성 | 60% | 95% | +35% |
| 유지보수 시간 | 100% | 30% | -70% |
| 크롤링 속도 | 기준 | 150% | +50% |
| 에러 복구율 | 20% | 80% | +60% |

---

## 📅 Phase 1: 안정성 강화 (필수, 1주)

### 목표
- 사이트 구조 변경에 대한 탄력성 확보
- 대용량 크롤링 안정성 보장
- 자동 에러 복구 시스템 구축

### 세부 작업

---

## Task 1.1: 셀렉터 중앙 관리 시스템

**소요 시간**: 1일
**우선순위**: 🔴 최우선
**난이도**: ⭐⭐⭐

### 현재 문제점

```python
# 현재: crawler.py에 하드코딩
email_input = self.wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
)

# 문제:
# 1. 사이트 변경 시 코드 수정 필요
# 2. 셀렉터가 여러 곳에 흩어짐
# 3. fallback 메커니즘 없음
```

### 해결 방안

#### Step 1: 디렉토리 구조 생성 (5분)

```bash
mkdir -p config
```

#### Step 2: 셀렉터 YAML 파일 생성 (30분)

**파일**: `config/selectors.yaml`

```yaml
# 셀렉터 정의 파일
# 각 셀렉터는 우선순위대로 fallback 제공

version: "1.0"
updated_at: "2025-12-05"

# 로그인 관련 셀렉터
login:
  email_input:
    primary: 'input[type="email"]'
    fallback1: 'input[name="email"]'
    fallback2: '#email'
    fallback3: '[data-testid="email-input"]'
    wait_time: 10
    description: "이메일 입력 필드"

  password_input:
    primary: 'input[type="password"]'
    fallback1: 'input[name="password"]'
    fallback2: '#password'
    wait_time: 10
    description: "비밀번호 입력 필드"

  submit_button:
    primary: 'button[type="submit"]'
    fallback1: 'button:contains("로그인")'
    fallback2: '#login-button'
    wait_time: 5
    description: "로그인 버튼"

# 날짜 선택 관련 셀렉터
date_picker:
  current_date:
    primary: 'p.MuiTypography-root.MuiTypography-body1.css-1a5pbt3'
    fallback1: '[data-testid="current-date"]'
    fallback2: '.calendar-current-date'
    wait_time: 5
    description: "현재 날짜 표시 (클릭하여 달력 열기)"

  month_header:
    primary: 'div#\\:r6\\:-grid-label.MuiPickersCalendarHeader-label.css-1v994a0'
    fallback1: '.MuiPickersCalendarHeader-label'
    fallback2: '[data-testid="month-header"]'
    wait_time: 5
    description: "년/월 표시 헤더"

  day_button_template:
    primary: 'button.MuiButtonBase-root.MuiPickersDay-root'
    wait_time: 3
    description: "날짜 버튼 (텍스트로 필터링 필요)"

  ok_button:
    primary: 'button:contains("OK")'
    fallback1: 'button[type="button"]:contains("확인")'
    fallback2: '[data-testid="date-ok-button"]'
    wait_time: 3
    description: "날짜 선택 확인 버튼"

# 상호 및 팀 관련 셀렉터
store:
  name_header:
    primary: 'h6.MuiTypography-root.MuiTypography-h6.css-18fet9p'
    fallback1: 'h6:contains("{store_name}")'
    fallback2: '[data-testid="store-name"]'
    wait_time: 5
    description: "상호명 헤더 (클릭하여 상세 진입)"

  team_container:
    primary: 'div.MuiBox-root.css-k008qs'
    fallback1: '[data-testid="team-container"]'
    wait_time: 5
    description: "팀 정보 컨테이너"

  team_label:
    primary: 'span.MuiChip-label.MuiChip-labelSmall.css-19imqg1'
    fallback1: '.MuiChip-label'
    wait_time: 3
    description: "팀 라벨 (TEAM 1, TEAM 2...)"

# 예약 상세 정보 셀렉터
reservation:
  customer_name:
    primary: 'h6.MuiTypography-root.MuiTypography-subtitle1.css-qdk4z1'
    fallback1: '[data-testid="customer-name"]'
    wait_time: 3
    description: "고객명"

  reservation_number:
    primary: 'h6.MuiTypography-root.MuiTypography-subtitle2.css-1r042ka'
    fallback1: '[data-testid="reservation-number"]'
    wait_time: 3
    description: "예약번호"

  channel:
    primary: 'div.MuiAvatar-root.MuiAvatar-circular.MuiChip-avatar.css-1buxfho'
    fallback1: '[data-testid="channel"]'
    wait_time: 3
    description: "채널 약자"

  people_count:
    primary: 'p.MuiTypography-root.MuiTypography-subtitle2.css-mdkayp'
    fallback1: '[data-testid="people-count"]'
    wait_time: 3
    description: "인원구분"

  country:
    primary: 'span.MuiTypography-root.MuiTypography-subtitle2.css-xcju41'
    fallback1: '[data-testid="country"]'
    wait_time: 3
    description: "국가"

  product:
    primary: 'p.MuiTypography-root.MuiTypography-subtitle2.css-1q5lgor'
    fallback1: '[data-testid="product"]'
    wait_time: 3
    description: "예약상품"

  time_request:
    primary: 'p.MuiTypography-root.MuiTypography-subtitle2.css-17exa0r'
    fallback1: '[data-testid="time-request"]'
    wait_time: 3
    description: "예약시간"
```

#### Step 3: SelectorManager 클래스 생성 (2시간)

**파일**: `src/utils/selector_manager.py`

```python
"""
셀렉터 중앙 관리 모듈
YAML에서 셀렉터를 로드하고 fallback 처리
"""

import yaml
import logging
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SelectorManager:
    """셀렉터 관리 클래스"""

    def __init__(self, selectors_file='config/selectors.yaml'):
        """
        초기화

        Args:
            selectors_file (str): 셀렉터 YAML 파일 경로
        """
        self.logger = logging.getLogger(__name__)
        self.selectors_file = selectors_file
        self.selectors = self._load_selectors()

    def _load_selectors(self):
        """YAML 파일에서 셀렉터 로드"""
        try:
            with open(self.selectors_file, 'r', encoding='utf-8') as f:
                selectors = yaml.safe_load(f)
            self.logger.info(f"셀렉터 로드 완료: {self.selectors_file}")
            return selectors
        except FileNotFoundError:
            self.logger.error(f"셀렉터 파일을 찾을 수 없습니다: {self.selectors_file}")
            raise
        except Exception as e:
            self.logger.error(f"셀렉터 로드 실패: {e}")
            raise

    def get_selector_config(self, category, name):
        """
        셀렉터 설정 가져오기

        Args:
            category (str): 카테고리 (예: 'login', 'date_picker')
            name (str): 셀렉터 이름 (예: 'email_input')

        Returns:
            dict: 셀렉터 설정
        """
        try:
            return self.selectors[category][name]
        except KeyError:
            self.logger.error(f"셀렉터를 찾을 수 없습니다: {category}.{name}")
            raise

    def find_element(self, driver, category, name, **kwargs):
        """
        요소 찾기 (fallback 포함)

        Args:
            driver: Selenium WebDriver
            category (str): 카테고리
            name (str): 셀렉터 이름
            **kwargs: 추가 인자 (예: store_name)

        Returns:
            WebElement: 찾은 요소

        Raises:
            NoSuchElementException: 모든 셀렉터 실패 시
        """
        config = self.get_selector_config(category, name)
        wait_time = config.get('wait_time', 10)

        # 우선순위대로 시도
        selectors = [
            config.get('primary'),
            config.get('fallback1'),
            config.get('fallback2'),
            config.get('fallback3')
        ]

        # None 제거
        selectors = [s for s in selectors if s]

        # kwargs로 셀렉터 포맷팅 (예: {store_name} 치환)
        selectors = [s.format(**kwargs) if kwargs else s for s in selectors]

        wait = WebDriverWait(driver, wait_time)

        for idx, selector in enumerate(selectors):
            try:
                self.logger.debug(f"시도 중: {selector}")
                element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )

                if idx > 0:
                    # fallback이 사용된 경우 경고
                    self.logger.warning(
                        f"Primary 셀렉터 실패, fallback{idx} 사용: "
                        f"{category}.{name} → {selector}"
                    )
                    # TODO: Slack 알림 전송

                return element

            except TimeoutException:
                if idx == len(selectors) - 1:
                    # 마지막 시도도 실패
                    error_msg = (
                        f"모든 셀렉터 실패: {category}.{name}\n"
                        f"시도한 셀렉터: {selectors}\n"
                        f"설명: {config.get('description', 'N/A')}"
                    )
                    self.logger.error(error_msg)

                    # 스크린샷 저장
                    self._save_error_screenshot(driver, category, name)

                    raise NoSuchElementException(error_msg)
                else:
                    # 다음 fallback 시도
                    continue

    def find_elements(self, driver, category, name, **kwargs):
        """
        여러 요소 찾기 (find_element의 복수형)

        Returns:
            list: WebElement 리스트
        """
        config = self.get_selector_config(category, name)
        wait_time = config.get('wait_time', 10)

        selectors = [
            config.get('primary'),
            config.get('fallback1'),
            config.get('fallback2')
        ]
        selectors = [s for s in selectors if s]
        selectors = [s.format(**kwargs) if kwargs else s for s in selectors]

        wait = WebDriverWait(driver, wait_time)

        for selector in selectors:
            try:
                elements = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                )
                return elements
            except TimeoutException:
                continue

        self.logger.error(f"요소들을 찾을 수 없습니다: {category}.{name}")
        return []

    def click_element(self, driver, category, name, **kwargs):
        """
        요소 찾아서 클릭

        Returns:
            bool: 성공 여부
        """
        try:
            element = self.find_element(driver, category, name, **kwargs)

            # 클릭 가능할 때까지 대기
            config = self.get_selector_config(category, name)
            wait_time = config.get('wait_time', 10)
            wait = WebDriverWait(driver, wait_time)

            clickable_element = wait.until(
                EC.element_to_be_clickable(element)
            )
            clickable_element.click()

            self.logger.info(f"클릭 성공: {category}.{name}")
            return True

        except Exception as e:
            self.logger.error(f"클릭 실패: {category}.{name} - {e}")
            return False

    def get_element_text(self, driver, category, name, **kwargs):
        """
        요소의 텍스트 가져오기

        Returns:
            str: 텍스트 (실패 시 빈 문자열)
        """
        try:
            element = self.find_element(driver, category, name, **kwargs)
            return element.text.strip()
        except Exception as e:
            self.logger.warning(f"텍스트 가져오기 실패: {category}.{name} - {e}")
            return ""

    def _save_error_screenshot(self, driver, category, name):
        """에러 발생 시 스크린샷 저장"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"logs/error_{category}_{name}_{timestamp}.png"

            Path("logs").mkdir(exist_ok=True)
            driver.save_screenshot(filename)

            self.logger.info(f"에러 스크린샷 저장: {filename}")
        except Exception as e:
            self.logger.error(f"스크린샷 저장 실패: {e}")

    def reload_selectors(self):
        """셀렉터 재로드 (hot reload)"""
        self.logger.info("셀렉터 재로드 중...")
        self.selectors = self._load_selectors()
```

#### Step 4: crawler.py 리팩토링 (3시간)

**파일 수정**: `crawler.py`

```python
# 파일 상단에 추가
from src.utils.selector_manager import SelectorManager

class KTourCrawler:
    def __init__(self, headless=False):
        # 기존 코드...

        # SelectorManager 추가
        self.selector_manager = SelectorManager()

    def login(self):
        """사이트 로그인 (리팩토링)"""
        try:
            self.logger.info(f"로그인 시도: {config.BASE_URL}")
            self.driver.get(config.BASE_URL)
            time.sleep(config.MEDIUM_DELAY)

            # 기존 코드:
            # email_input = self.wait.until(...)

            # 새 코드:
            email_input = self.selector_manager.find_element(
                self.driver, 'login', 'email_input'
            )
            email_input.clear()
            email_input.send_keys(config.LOGIN_ID)
            time.sleep(config.SHORT_DELAY)

            password_input = self.selector_manager.find_element(
                self.driver, 'login', 'password_input'
            )
            password_input.clear()
            password_input.send_keys(config.LOGIN_PASSWORD)
            time.sleep(config.SHORT_DELAY)

            # 클릭은 편의 메서드 사용
            self.selector_manager.click_element(
                self.driver, 'login', 'submit_button'
            )

            time.sleep(config.LONG_DELAY)
            self.logger.info("로그인 완료")

        except Exception as e:
            self.logger.error(f"로그인 실패: {e}")
            raise

    def click_date_picker(self):
        """날짜 선택기 클릭 (리팩토링)"""
        try:
            self.selector_manager.click_element(
                self.driver, 'date_picker', 'current_date'
            )
            time.sleep(config.SHORT_DELAY)
            self.logger.info("날짜 선택기 열기 완료")

        except Exception as e:
            self.logger.error(f"날짜 선택기 클릭 실패: {e}")
            raise

    # 나머지 메서드도 동일하게 리팩토링...
```

#### Step 5: 테스트 (1시간)

```bash
# 1. 셀렉터 로드 테스트
python -c "from src.utils.selector_manager import SelectorManager; sm = SelectorManager(); print('✓ 셀렉터 로드 성공')"

# 2. 로그인 테스트
python main.py --date 2025-12-05

# 3. 셀렉터 변경 시뮬레이션
# config/selectors.yaml에서 primary를 잘못된 값으로 변경
# → fallback이 작동하는지 확인
```

### 체크리스트

- [ ] `config/` 디렉토리 생성
- [ ] `config/selectors.yaml` 파일 작성
- [ ] `src/utils/selector_manager.py` 파일 작성
- [ ] `crawler.py` 리팩토링
  - [ ] `login()` 메서드
  - [ ] `click_date_picker()` 메서드
  - [ ] `select_month()` 메서드
  - [ ] `select_day()` 메서드
  - [ ] `click_store()` 메서드
  - [ ] `extract_reservation_details()` 메서드
- [ ] 테스트 실행
- [ ] 로그 확인 (fallback 작동 여부)
- [ ] 문서 업데이트

### 예상 효과

- ✅ 사이트 변경 시 YAML만 수정 (5분)
- ✅ 3단계 fallback으로 안정성 향상
- ✅ 에러 발생 시 스크린샷 자동 저장
- ✅ 셀렉터 변경 이력 Git으로 추적
- ✅ 향후 다른 사이트 추가 용이

---

## Task 1.2: 체크포인트 시스템

**소요 시간**: 2일
**우선순위**: 🔴 필수
**난이도**: ⭐⭐⭐⭐

### 현재 문제점

```python
# 30일 크롤링 중 20일째 실패하면...
# → 30일 모두 다시 크롤링해야 함
# → 시간 낭비 (10-15분)
```

### 해결 방안

#### Step 1: 디렉토리 생성 (1분)

```bash
mkdir -p data/checkpoints
```

#### Step 2: Checkpoint 모델 생성 (30분)

**파일**: `src/models/checkpoint.py`

```python
"""
체크포인트 모델
크롤링 진행 상황 저장 및 복구
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class CrawlingCheckpoint:
    """크롤링 체크포인트"""

    # 작업 정보
    task_id: str  # 예: 20251205_143022
    store_name: str
    start_date: str
    end_date: str
    mode: str  # daily, weekly, monthly

    # 진행 상황
    completed_dates: List[str]  # 완료된 날짜 목록
    failed_dates: List[str]  # 실패한 날짜 목록
    skipped_dates: List[str]  # 건너뛴 날짜 목록

    # 수집 데이터
    total_reservations: int  # 수집된 예약 건수

    # 메타 정보
    created_at: str
    updated_at: str
    status: str  # running, completed, interrupted, failed

    # 에러 정보
    last_error: Optional[str] = None
    error_count: int = 0

    def to_dict(self):
        """딕셔너리로 변환"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 생성"""
        return cls(**data)

    def save(self, checkpoint_dir='data/checkpoints'):
        """체크포인트 저장"""
        Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)

        filepath = Path(checkpoint_dir) / f"{self.task_id}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

        return str(filepath)

    @classmethod
    def load(cls, task_id, checkpoint_dir='data/checkpoints'):
        """체크포인트 로드"""
        filepath = Path(checkpoint_dir) / f"{task_id}.json"

        if not filepath.exists():
            raise FileNotFoundError(f"체크포인트를 찾을 수 없습니다: {task_id}")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return cls.from_dict(data)

    @classmethod
    def list_checkpoints(cls, checkpoint_dir='data/checkpoints'):
        """모든 체크포인트 목록"""
        checkpoint_path = Path(checkpoint_dir)

        if not checkpoint_path.exists():
            return []

        checkpoints = []
        for file in checkpoint_path.glob('*.json'):
            try:
                checkpoint = cls.load(file.stem, checkpoint_dir)
                checkpoints.append(checkpoint)
            except:
                continue

        # 최신순 정렬
        checkpoints.sort(key=lambda x: x.created_at, reverse=True)
        return checkpoints

    def get_remaining_dates(self, all_dates):
        """남은 날짜 목록"""
        completed_set = set(self.completed_dates)
        remaining = [d for d in all_dates if d not in completed_set]
        return remaining

    def mark_completed(self, date):
        """날짜 완료 표시"""
        if date not in self.completed_dates:
            self.completed_dates.append(date)
        if date in self.failed_dates:
            self.failed_dates.remove(date)
        self.updated_at = datetime.now().isoformat()

    def mark_failed(self, date, error=None):
        """날짜 실패 표시"""
        if date not in self.failed_dates:
            self.failed_dates.append(date)
        if error:
            self.last_error = str(error)
        self.error_count += 1
        self.updated_at = datetime.now().isoformat()

    def update_status(self, status):
        """상태 업데이트"""
        self.status = status
        self.updated_at = datetime.now().isoformat()
```

#### Step 3: CheckpointService 생성 (2시간)

**파일**: `src/services/checkpoint_service.py`

```python
"""
체크포인트 관리 서비스
"""

import logging
from datetime import datetime
from typing import List, Optional
from src.models.checkpoint import CrawlingCheckpoint


class CheckpointService:
    """체크포인트 관리 서비스"""

    def __init__(self, checkpoint_dir='data/checkpoints'):
        self.checkpoint_dir = checkpoint_dir
        self.logger = logging.getLogger(__name__)

    def create_checkpoint(self, store_name, start_date, end_date, mode, all_dates):
        """새 체크포인트 생성"""
        task_id = datetime.now().strftime('%Y%m%d_%H%M%S')

        checkpoint = CrawlingCheckpoint(
            task_id=task_id,
            store_name=store_name,
            start_date=start_date,
            end_date=end_date,
            mode=mode,
            completed_dates=[],
            failed_dates=[],
            skipped_dates=[],
            total_reservations=0,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            status='running'
        )

        checkpoint.save(self.checkpoint_dir)
        self.logger.info(f"체크포인트 생성: {task_id}")

        return checkpoint

    def update_checkpoint(self, checkpoint):
        """체크포인트 업데이트"""
        checkpoint.updated_at = datetime.now().isoformat()
        checkpoint.save(self.checkpoint_dir)

    def find_resumable_checkpoint(self, store_name, start_date, end_date):
        """재개 가능한 체크포인트 찾기"""
        checkpoints = CrawlingCheckpoint.list_checkpoints(self.checkpoint_dir)

        for cp in checkpoints:
            if (cp.store_name == store_name and
                cp.start_date == start_date and
                cp.end_date == end_date and
                cp.status in ['interrupted', 'running']):
                return cp

        return None

    def get_resumable_checkpoints(self):
        """재개 가능한 모든 체크포인트"""
        checkpoints = CrawlingCheckpoint.list_checkpoints(self.checkpoint_dir)
        return [cp for cp in checkpoints if cp.status in ['interrupted', 'running']]

    def cleanup_old_checkpoints(self, keep_days=30):
        """오래된 체크포인트 정리"""
        # TODO: 구현
        pass
```

#### Step 4: Crawler에 통합 (3시간)

**파일 수정**: `crawler.py`

```python
from src.services.checkpoint_service import CheckpointService

class KTourCrawler:
    def __init__(self, headless=False):
        # 기존 코드...
        self.checkpoint_service = CheckpointService()
        self.current_checkpoint = None

    def crawl_date_range_with_checkpoint(self, start_date, end_date, mode='daily', resume=False):
        """
        체크포인트 기능이 있는 날짜 범위 크롤링

        Args:
            start_date (str): 시작 날짜
            end_date (str): 종료 날짜
            mode (str): 크롤링 모드
            resume (bool): 중단된 작업 재개 여부
        """
        try:
            # 날짜 목록 생성
            all_dates = self._generate_date_list(start_date, end_date, mode)

            # 재개 모드 확인
            if resume:
                checkpoint = self.checkpoint_service.find_resumable_checkpoint(
                    config.STORE_NAME,  # 또는 파라미터로 받기
                    start_date,
                    end_date
                )
                if checkpoint:
                    self.logger.info(f"체크포인트 발견: {checkpoint.task_id}")
                    self.logger.info(f"완료: {len(checkpoint.completed_dates)}일, "
                                   f"실패: {len(checkpoint.failed_dates)}일")

                    # 남은 날짜만 크롤링
                    dates_to_crawl = checkpoint.get_remaining_dates(all_dates)
                    self.current_checkpoint = checkpoint
                else:
                    self.logger.info("재개 가능한 체크포인트 없음. 새로 시작합니다.")
                    dates_to_crawl = all_dates
                    self.current_checkpoint = self.checkpoint_service.create_checkpoint(
                        config.STORE_NAME, start_date, end_date, mode, all_dates
                    )
            else:
                # 새 체크포인트 생성
                dates_to_crawl = all_dates
                self.current_checkpoint = self.checkpoint_service.create_checkpoint(
                    config.STORE_NAME, start_date, end_date, mode, all_dates
                )

            self.logger.info(f"크롤링 시작: {len(dates_to_crawl)}일")

            # 각 날짜 크롤링
            for date in dates_to_crawl:
                try:
                    self.logger.info(f"크롤링 중: {date}")
                    self.crawl_date(date)

                    # 성공 시 체크포인트 업데이트
                    self.current_checkpoint.mark_completed(date)
                    self.current_checkpoint.total_reservations = len(self.reservations)
                    self.checkpoint_service.update_checkpoint(self.current_checkpoint)

                except Exception as e:
                    self.logger.error(f"{date} 크롤링 실패: {e}")

                    # 실패 표시
                    self.current_checkpoint.mark_failed(date, e)
                    self.checkpoint_service.update_checkpoint(self.current_checkpoint)

                    # 계속 진행 (다음 날짜로)
                    continue

            # 완료 상태로 변경
            self.current_checkpoint.update_status('completed')
            self.checkpoint_service.update_checkpoint(self.current_checkpoint)

            self.logger.info("크롤링 완료")

        except KeyboardInterrupt:
            # Ctrl+C로 중단 시
            self.logger.warning("사용자에 의해 중단됨")
            if self.current_checkpoint:
                self.current_checkpoint.update_status('interrupted')
                self.checkpoint_service.update_checkpoint(self.current_checkpoint)
                self.logger.info(f"체크포인트 저장됨: {self.current_checkpoint.task_id}")
                self.logger.info("다음 실행 시 --resume 옵션으로 재개 가능합니다")

        except Exception as e:
            self.logger.error(f"치명적 오류: {e}")
            if self.current_checkpoint:
                self.current_checkpoint.update_status('failed')
                self.current_checkpoint.last_error = str(e)
                self.checkpoint_service.update_checkpoint(self.current_checkpoint)
            raise

    def _generate_date_list(self, start_date, end_date, mode):
        """날짜 목록 생성 (기존 로직 분리)"""
        # web_app.py의 generate_date_range 로직과 동일
        from datetime import datetime, timedelta

        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        dates = []
        # ... 기존 로직
        return dates
```

#### Step 5: CLI에 재개 옵션 추가 (30분)

**파일 수정**: `main.py`

```python
parser.add_argument('--resume', action='store_true',
                    help='중단된 크롤링 재개')
parser.add_argument('--list-checkpoints', action='store_true',
                    help='재개 가능한 체크포인트 목록 보기')

# ... 실행 부분
if args.list_checkpoints:
    from src.services.checkpoint_service import CheckpointService
    cp_service = CheckpointService()
    checkpoints = cp_service.get_resumable_checkpoints()

    print(f"\n재개 가능한 체크포인트: {len(checkpoints)}개\n")
    for cp in checkpoints:
        print(f"ID: {cp.task_id}")
        print(f"상호: {cp.store_name}")
        print(f"기간: {cp.start_date} ~ {cp.end_date}")
        print(f"진행: {len(cp.completed_dates)}/{len(cp.completed_dates) + len(cp.failed_dates)}일")
        print(f"상태: {cp.status}")
        print("-" * 50)
    exit(0)

# 크롤링 실행
if args.resume:
    crawler.crawl_date_range_with_checkpoint(
        start_date, end_date, mode='daily', resume=True
    )
else:
    crawler.crawl_date_range_with_checkpoint(
        start_date, end_date, mode='daily', resume=False
    )
```

### 체크리스트

- [ ] `data/checkpoints/` 디렉토리 생성
- [ ] `src/models/checkpoint.py` 작성
- [ ] `src/services/checkpoint_service.py` 작성
- [ ] `crawler.py`에 체크포인트 로직 통합
- [ ] `main.py`에 --resume 옵션 추가
- [ ] 테스트
  - [ ] 정상 완료 시나리오
  - [ ] 중간 실패 시나리오
  - [ ] Ctrl+C 중단 시나리오
  - [ ] --resume으로 재개
- [ ] 문서 업데이트

### 사용 예시

```bash
# 1. 크롤링 시작
python main.py --start-date 2025-12-01 --end-date 2025-12-31

# 2. 중간에 Ctrl+C로 중단
# → 체크포인트 자동 저장

# 3. 체크포인트 목록 확인
python main.py --list-checkpoints

# 4. 재개
python main.py --start-date 2025-12-01 --end-date 2025-12-31 --resume
```

### 예상 효과

- ✅ 30일 크롤링 중 실패해도 처음부터 다시 시작 불필요
- ✅ 시간 절약 (20일 완료 → 10일만 재크롤링)
- ✅ 네트워크 오류에 강함
- ✅ Ctrl+C로 안전하게 중단 가능

---

## Task 1.3: 지능형 재시도 & 에러 핸들링

**소요 시간**: 1일
**우선순위**: 🟡 권장
**난이도**: ⭐⭐⭐

### 현재 문제점

```python
# 일시적 네트워크 오류로 즉시 실패
# → 수동으로 다시 실행해야 함
```

### 해결 방안

#### Step 1: tenacity 라이브러리 설치 (1분)

```bash
pip install tenacity==8.2.3
```

**파일**: `requirements.txt`에 추가
```
tenacity==8.2.3
```

#### Step 2: Retry 데코레이터 생성 (1시간)

**파일**: `src/utils/retry_handler.py`

```python
"""
재시도 핸들러
"""

import time
import logging
from functools import wraps
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException
)


logger = logging.getLogger(__name__)


# 재시도 가능한 예외
RETRIABLE_EXCEPTIONS = (
    TimeoutException,
    WebDriverException,
)

# 재시도 불가능한 예외
NON_RETRIABLE_EXCEPTIONS = (
    KeyboardInterrupt,
    SystemExit,
)


def smart_retry(max_attempts=3, initial_wait=2, max_wait=10):
    """
    지능형 재시도 데코레이터

    Args:
        max_attempts (int): 최대 재시도 횟수
        initial_wait (int): 초기 대기 시간 (초)
        max_wait (int): 최대 대기 시간 (초)

    지수 백오프:
    1차 실패 → initial_wait초 대기
    2차 실패 → initial_wait*2초 대기
    3차 실패 → initial_wait*4초 대기 (max_wait 제한)
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(
            multiplier=1,
            min=initial_wait,
            max=max_wait
        ),
        retry=retry_if_exception_type(RETRIABLE_EXCEPTIONS),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )


def retry_on_failure(func):
    """
    실패 시 재시도하는 간단한 데코레이터

    Usage:
        @retry_on_failure
        def my_function():
            # ... 코드
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except RETRIABLE_EXCEPTIONS as e:
                if attempt == max_attempts:
                    logger.error(f"{func.__name__} 최종 실패: {e}")
                    raise

                wait_time = 2 ** attempt  # 2, 4, 8초
                logger.warning(
                    f"{func.__name__} 실패 (시도 {attempt}/{max_attempts}). "
                    f"{wait_time}초 후 재시도... 에러: {e}"
                )
                time.sleep(wait_time)
            except NON_RETRIABLE_EXCEPTIONS:
                logger.info(f"{func.__name__} 사용자 중단")
                raise
            except Exception as e:
                logger.error(f"{func.__name__} 치명적 오류: {e}")
                raise

    return wrapper


class ErrorClassifier:
    """에러 분류기"""

    @staticmethod
    def classify(error):
        """
        에러를 분류

        Returns:
            str: 'RECOVERABLE', 'CONFIGURATION', 'FATAL'
        """
        error_type = type(error).__name__
        error_msg = str(error).lower()

        # 복구 가능 (재시도)
        if isinstance(error, RETRIABLE_EXCEPTIONS):
            return 'RECOVERABLE'

        # 설정 오류 (셀렉터 변경 등)
        if isinstance(error, NoSuchElementException):
            return 'CONFIGURATION'

        # 치명적 오류
        return 'FATAL'

    @staticmethod
    def get_recommendation(error):
        """에러에 대한 권장 조치"""
        classification = ErrorClassifier.classify(error)

        recommendations = {
            'RECOVERABLE': "일시적 오류입니다. 자동으로 재시도됩니다.",
            'CONFIGURATION': (
                "셀렉터 설정을 확인하세요.\n"
                "1. config/selectors.yaml 파일 확인\n"
                "2. 사이트 구조 변경 여부 확인\n"
                "3. 브라우저 개발자 도구로 실제 셀렉터 확인"
            ),
            'FATAL': (
                "치명적 오류입니다.\n"
                "1. 로그 파일 확인 (crawler.log)\n"
                "2. 인터넷 연결 확인\n"
                "3. 로그인 정보 확인"
            )
        }

        return recommendations.get(classification, "알 수 없는 오류입니다.")
```

#### Step 3: Crawler에 적용 (2시간)

**파일 수정**: `crawler.py`

```python
from src.utils.retry_handler import smart_retry, retry_on_failure, ErrorClassifier

class KTourCrawler:

    @smart_retry(max_attempts=3, initial_wait=2, max_wait=10)
    def login(self):
        """사이트 로그인 (재시도 적용)"""
        # 기존 코드 그대로
        # 실패 시 자동으로 재시도됨

    @retry_on_failure
    def click_date_picker(self):
        """날짜 선택기 클릭 (재시도 적용)"""
        # 기존 코드 그대로

    @smart_retry(max_attempts=3)
    def crawl_date(self, target_date):
        """
        특정 날짜 크롤링 (재시도 적용)

        중요: 멱등성 보장 필요
        - 같은 날짜를 여러 번 크롤링해도 문제없도록
        """
        try:
            # 기존 크롤링 로직
            pass
        except Exception as e:
            # 에러 분류
            classification = ErrorClassifier.classify(e)
            recommendation = ErrorClassifier.get_recommendation(e)

            self.logger.error(
                f"에러 분류: {classification}\n"
                f"권장 조치:\n{recommendation}"
            )

            raise
```

### 체크리스트

- [ ] `tenacity` 설치
- [ ] `src/utils/retry_handler.py` 작성
- [ ] `crawler.py`의 주요 메서드에 데코레이터 적용
- [ ] 에러 분류기 테스트
- [ ] 지수 백오프 동작 확인
- [ ] 문서 업데이트

### 테스트 시나리오

```python
# 1. 네트워크 일시 차단 시뮬레이션
# → 자동 재시도 확인

# 2. 셀렉터 오류 시뮬레이션
# → CONFIGURATION 에러로 분류되는지 확인
# → 재시도하지 않고 즉시 실패하는지 확인

# 3. 로그 출력 확인
# → "재시도 중..." 메시지 확인
# → 대기 시간 증가 확인 (2초 → 4초 → 8초)
```

### 예상 효과

- ✅ 일시적 네트워크 오류 자동 복구 (80%)
- ✅ 불필요한 재시도 방지 (치명적 오류는 즉시 실패)
- ✅ 명확한 에러 분류 및 해결 가이드
- ✅ 운영 부담 감소

---

## Phase 1 완료 체크리스트

### 최종 확인 사항

- [ ] **Task 1.1** 셀렉터 중앙 관리 완료
  - [ ] selectors.yaml 작성
  - [ ] SelectorManager 구현
  - [ ] crawler.py 리팩토링
  - [ ] fallback 동작 테스트

- [ ] **Task 1.2** 체크포인트 시스템 완료
  - [ ] Checkpoint 모델 구현
  - [ ] CheckpointService 구현
  - [ ] crawler.py 통합
  - [ ] --resume 옵션 테스트

- [ ] **Task 1.3** 재시도 시스템 완료
  - [ ] retry_handler 구현
  - [ ] 데코레이터 적용
  - [ ] 에러 분류 테스트

### 통합 테스트

```bash
# 1. 전체 플로우 테스트
python main.py --start-date 2025-12-01 --end-date 2025-12-05

# 2. 중단 후 재개 테스트
# 실행 중 Ctrl+C
python main.py --start-date 2025-12-01 --end-date 2025-12-05 --resume

# 3. 셀렉터 fallback 테스트
# selectors.yaml에서 primary를 잘못된 값으로 변경
# → fallback이 작동하는지 확인

# 4. 에러 처리 테스트
# 네트워크 일시 차단
# → 자동 재시도 확인
```

### 성공 기준

- ✅ 30일 크롤링 중 중단 후 재개 가능
- ✅ 셀렉터 1개 변경 시 YAML만 수정으로 해결
- ✅ 일시적 오류 80% 이상 자동 복구
- ✅ 모든 테스트 통과

---

## 📝 Phase 2 & 3 (간략)

### Phase 2: 성능 최적화 (선택사항)

- **Task 2.1**: 캐싱 시스템 (Redis/SQLite)
- **Task 2.2**: 데이터 모델 정의 (Dataclass)
- **Task 2.3**: 병렬 크롤링 (선택적)

### Phase 3: 운영 편의성 (여유시)

- **Task 3.1**: YAML 설정 전환
- **Task 3.2**: 알림 시스템 (Slack)
- **Task 3.3**: 스케줄러 통합
- **Task 3.4**: 대시보드 (매우 선택적)

---

## 📚 참고 자료

### Git 브랜치 전략

```bash
# 개선 작업용 브랜치
git checkout -b feature/phase1-stability

# Task별 커밋
git commit -m "feat: Add SelectorManager with YAML config"
git commit -m "feat: Add checkpoint system for resume capability"
git commit -m "feat: Add smart retry with exponential backoff"

# 완료 후 병합
git checkout main
git merge feature/phase1-stability
```

### 롤백 계획

만약 문제가 생기면:
```bash
# 이전 버전으로 복구
git checkout main
git revert HEAD

# 또는 특정 커밋으로
git reset --hard COMMIT_HASH
```

---

## 🎯 다음 단계

Phase 1 완료 후:

1. **2주 실사용**: 안정성 확인
2. **피드백 수집**: 불편한 점 파악
3. **Phase 2 검토**: 필요성 재평가
4. **선택적 구현**: 꼭 필요한 것만

---

**작성자**: Claude (AI Assistant)
**검토자**: [귀하의 이름]
**승인일**: [승인 날짜]

이 문서는 실제 구현 과정에서 지속적으로 업데이트됩니다.
