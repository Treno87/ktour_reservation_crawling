"""
KTour 예약 현황 크롤러
"""

import time
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import config
from utils import retry, PasswordFilter


class KTourCrawler:
    """KTour 예약 현황 크롤러 클래스"""

    def __init__(self, headless=False):
        """
        크롤러 초기화

        Args:
            headless (bool): 헤드리스 모드 사용 여부
        """
        self.driver = None
        self.wait = None
        self.headless = headless
        self.reservations = []

        # 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('crawler.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # 패스워드 필터 추가
        password_filter = PasswordFilter()
        for handler in logging.root.handlers:
            handler.addFilter(password_filter)

    def setup_driver(self):
        """Selenium WebDriver 설정"""
        try:
            chrome_options = Options()

            if self.headless:
                chrome_options.add_argument('--headless')

            # 일반적인 크롬 옵션
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # User-Agent 설정
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # WebDriver 초기화
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # 대기 시간 설정
            self.driver.implicitly_wait(config.IMPLICIT_WAIT)
            self.driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
            self.wait = WebDriverWait(self.driver, config.EXPLICIT_WAIT)

            # 창 크기 최대화
            self.driver.maximize_window()

            self.logger.info("WebDriver 설정 완료")

        except Exception as e:
            self.logger.error(f"WebDriver 설정 실패: {e}")
            raise

    @retry(max_attempts=3, delay=2, exceptions=(TimeoutException, NoSuchElementException))
    def login(self):
        """사이트 로그인"""
        try:
            self.logger.info(f"로그인 시도: {config.BASE_URL}")
            self.driver.get(config.BASE_URL)
            time.sleep(config.MEDIUM_DELAY)

            # 로그인 페이지인지 확인 및 로그인 수행
            # 실제 로그인 필드의 셀렉터를 찾아야 합니다
            # 아래는 일반적인 예시입니다

            # 이메일 입력 필드 찾기 (실제 셀렉터로 수정 필요)
            email_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"], input[name="email"], input[id*="email"]'))
            )
            email_input.clear()
            email_input.send_keys(config.LOGIN_ID)
            time.sleep(config.SHORT_DELAY)

            # 비밀번호 입력 필드 찾기 (실제 셀렉터로 수정 필요)
            password_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
            password_input.clear()
            password_input.send_keys(config.LOGIN_PASSWORD)
            time.sleep(config.SHORT_DELAY)

            # 로그인 버튼 클릭 (실제 셀렉터로 수정 필요)
            login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()

            time.sleep(config.LONG_DELAY)

            self.logger.info("로그인 완료")

        except Exception as e:
            self.logger.error(f"로그인 실패: {e}")
            raise

    @retry(max_attempts=3, delay=1, exceptions=(TimeoutException, NoSuchElementException))
    def click_date_picker(self):
        """날짜 선택기 클릭"""
        try:
            # 날짜 표시 요소 클릭
            date_element = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'p.MuiTypography-root.MuiTypography-body1.css-1a5pbt3'))
            )
            date_element.click()
            time.sleep(config.SHORT_DELAY)

            self.logger.info("날짜 선택기 열기 완료")

        except Exception as e:
            self.logger.error(f"날짜 선택기 클릭 실패: {e}")
            raise

    def select_month(self, year, month):
        """
        년월 선택

        Args:
            year (int): 연도
            month (int): 월 (1-12)
        """
        try:
            month_names = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            target_month = f"{month_names[month-1]} {year}"

            # 현재 표시된 년월 확인
            current_month_element = self.driver.find_element(
                By.CSS_SELECTOR,
                'div.MuiPickersCalendarHeader-label.css-1v994a0'
            )
            current_month = current_month_element.text

            # 목표 년월과 다르면 화살표 클릭
            max_attempts = 24  # 최대 2년치
            attempts = 0

            while current_month != target_month and attempts < max_attempts:
                if self._should_click_next(current_month, target_month):
                    # 다음 달 화살표 클릭
                    next_button = self.driver.find_element(
                        By.CSS_SELECTOR,
                        'button[aria-label="Next month"]'
                    )
                    next_button.click()
                else:
                    # 이전 달 화살표 클릭
                    prev_button = self.driver.find_element(
                        By.CSS_SELECTOR,
                        'button[aria-label="Previous month"]'
                    )
                    prev_button.click()

                time.sleep(0.5)
                current_month_element = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'div.MuiPickersCalendarHeader-label.css-1v994a0'
                )
                current_month = current_month_element.text
                attempts += 1

            self.logger.info(f"년월 선택 완료: {target_month}")

        except Exception as e:
            self.logger.error(f"년월 선택 실패: {e}")
            raise

    def _should_click_next(self, current, target):
        """다음 달 화살표를 클릭해야 하는지 판단"""
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        current_parts = current.split()
        target_parts = target.split()

        current_year = int(current_parts[1])
        target_year = int(target_parts[1])

        current_month_idx = months.index(current_parts[0])
        target_month_idx = months.index(target_parts[0])

        if target_year > current_year:
            return True
        elif target_year < current_year:
            return False
        else:
            return target_month_idx > current_month_idx

    def select_day(self, day):
        """
        특정 날짜 선택

        Args:
            day (int): 일 (1-31)
        """
        try:
            # 선택 가능한 날짜 버튼 찾기
            day_buttons = self.driver.find_elements(
                By.CSS_SELECTOR,
                'button.MuiButtonBase-root.MuiPickersDay-root.MuiPickersDay-dayWithMargin'
            )

            for button in day_buttons:
                if button.text == str(day) and 'MuiPickersDay-hiddenDaySpacingFiller' not in button.get_attribute('class'):
                    button.click()
                    time.sleep(config.SHORT_DELAY)
                    self.logger.info(f"날짜 선택 완료: {day}일")
                    return

            raise Exception(f"{day}일을 찾을 수 없습니다")

        except Exception as e:
            self.logger.error(f"날짜 선택 실패: {e}")
            raise

    def click_ok_button(self):
        """OK 버튼 클릭"""
        try:
            ok_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//button[text()="OK"]'))
            )
            ok_button.click()
            time.sleep(config.MEDIUM_DELAY)

            self.logger.info("OK 버튼 클릭 완료")

        except Exception as e:
            self.logger.error(f"OK 버튼 클릭 실패: {e}")
            raise

    def click_store(self, store_name="마리엠헤어", timeout=None):
        """
        상호 클릭

        Args:
            store_name (str): 클릭할 상호명
            timeout (int): 대기 시간 (초), None이면 기본값 사용

        Raises:
            TimeoutException: 상호 요소를 찾지 못한 경우 (예약 없음)
            NoSuchElementException: 상호 요소가 없는 경우 (예약 없음)
        """
        wait_time = timeout if timeout is not None else config.EXPLICIT_WAIT
        wait = WebDriverWait(self.driver, wait_time)
        
        store_element = wait.until(
            EC.element_to_be_clickable((By.XPATH, f'//h6[text()="{store_name}"]'))
        )
        store_element.click()
        time.sleep(config.MEDIUM_DELAY)

        self.logger.info(f"상호 클릭 완료: {store_name}")

    def get_team_list(self):
        """팀 목록 가져오기"""
        try:
            # 팀 정보가 있는 li 요소들 찾기 (사용자 제공 XPath 기반)
            # MuiListSubheader-root 클래스를 가진 li 요소들
            team_elements = self.driver.find_elements(
                By.XPATH,
                '//ul/li[contains(@class, "MuiListSubheader-root")]'
            )

            teams = []
            for element in team_elements:
                try:
                    # li 내부에서 팀 이름 찾기
                    team_chips = element.find_elements(By.CSS_SELECTOR, 'span.MuiChip-label')
                    if team_chips:
                        team_name = team_chips[0].text
                        teams.append({'name': team_name, 'element': element})
                except:
                    continue

            self.logger.info(f"팀 목록 가져오기 완료: {len(teams)}개")
            return teams

        except Exception as e:
            self.logger.error(f"팀 목록 가져오기 실패: {e}")
            return []

    def click_team(self, team_element):
        """팀 클릭"""
        try:
            # li 요소 내부의 펼치기 버튼 찾기
            expand_button = team_element.find_element(
                By.XPATH,
                './/button[contains(@class, "MuiIconButton-root")]'
            )
            expand_button.click()
            time.sleep(config.MEDIUM_DELAY)
            self.logger.info("팀 펼치기 완료")

        except Exception as e:
            self.logger.error(f"팀 펼치기 실패: {e}")
            raise

    def extract_reservation_details(self, target_date, team_name):
        """
        예약 상세 정보 추출 (특정 팀 이름에 해당하는 섹션에서 데이터 추출)
        """
        # 암시적 대기 시간 임시 변경
        original_wait = config.IMPLICIT_WAIT
        self.driver.implicitly_wait(1)

        try:
            reservation = {
                'date': target_date,
                'team': team_name, # 팀 이름은 이미 알고 있으므로 바로 할당
                'customer_name': '',
                'reservation_number': '',
                'channel': '',
                'people_count': '',
                'country': '',
                'product': '',
                'time_request': ''
            }

            # 1. 현재 펼쳐진 영역(MuiCollapse-entered)을 찾음
            # MUI Accordion 구조상 펼쳐진 내용은 'MuiCollapse-entered' 클래스를 가짐
            try:
                # 펼쳐진 영역 찾기 (Transition 등이 있을 수 있으므로 잠시 대기할 수도 있음)
                # visible 상태인 collapse root를 찾습니다.
                container = self.driver.find_element(By.CSS_SELECTOR, 'div.MuiCollapse-entered')
            except:
                # 만약 entered가 없다면 아직 펼쳐지는 중일 수 있으니 vertical이나 visible 확인
                try:
                     container = self.driver.find_element(By.CSS_SELECTOR, 'div.MuiCollapse-root[style*="visible"]')
                except:
                     self.logger.warning(f"펼쳐진 예약 상세 영역을 찾을 수 없음: {team_name}")
                     return None

            # 2. 컨테이너 내부의 모든 예약 항목(ListItemButton)을 찾음
            # 제공된 HTML 구조: div.MuiListItemButton-root ...
            reservation_items = container.find_elements(By.CSS_SELECTOR, 'div.MuiListItemButton-root')
            
            extracted_reservations = []

            for item in reservation_items:
                try:
                    reservation = {
                        'date': target_date,
                        'team': team_name,
                        'customer_name': '',
                        'reservation_number': '',
                        'channel': '',
                        'people_count': '',
                        'country': '',
                        'product': '',
                        'time_request': ''
                    }

                    def get_text_from_item(xpath_suffix):
                        try:
                            return item.find_element(By.XPATH, xpath_suffix).text
                        except:
                            return ''

                    # 고객명: MuiListItemText-primary 내부의 h6
                    reservation['customer_name'] = get_text_from_item(
                        './/div[contains(@class, "MuiListItemText-primary")]//h6[contains(@class, "MuiTypography-subtitle1")]'
                    )

                    # 예약번호: MuiChip-label 내부의 h6 (예: YYA187985)
                    reservation['reservation_number'] = get_text_from_item(
                        './/span[contains(@class, "MuiChip-label")]//h6[contains(@class, "MuiTypography-subtitle2")]'
                    )
                    
                    # 예약번호가 없으면 이전 방식 시도 (Reservation Number 패턴 매칭)
                    if not reservation['reservation_number']:
                        try:
                            elements = item.find_elements(By.XPATH, './/h6')
                            for el in elements:
                                txt = el.text
                                # 대문자 영문 + 숫자 조합이고 길이가 5 이상인 경우 예약번호로 추정
                                if txt and len(txt) > 5 and any(c.isalpha() for c in txt) and any(c.isdigit() for c in txt):
                                    reservation['reservation_number'] = txt
                                    break
                        except:
                            pass

                    # 채널약자
                    reservation['channel'] = get_text_from_item(
                        './/div[contains(@class, "MuiChip-avatar")]'
                    )

                    # 인원구분 및 수 (예: Ad: 1 Kd: 0 Bb: 0)
                    reservation['people_count'] = get_text_from_item(
                        './/p[contains(@class, "MuiTypography-subtitle2") and contains(text(), "Ad:")]'
                    )

                    # 국가
                    reservation['country'] = get_text_from_item(
                        './/span[contains(@class, "MuiTypography-subtitle2") and contains(@class, "css-xcju41")]'
                    )
                    # 국기가 별도 span이나 이모지로 있을 수 있으므로 국가명만 추출 시도할 수도 있음

                    # 예약상품
                    product_text = get_text_from_item(
                        './/div[contains(@class, "MuiGrid-grid-xs-10")]//p[contains(@class, "MuiTypography-subtitle2")]'
                    )
                    if ':' in product_text:
                        product_text = product_text.split(':', 1)[1].strip()
                    reservation['product'] = product_text

                    # 예약시간 (Time Request: 11:30 또는 그냥 10:00)
                    import re
                    time_text = ''
                    # 모든 p 태그를 뒤져서 시간 형식이 있는지 확인
                    p_elements = item.find_elements(By.XPATH, './/p[contains(@class, "MuiTypography-subtitle2")]')
                    for p in p_elements:
                        txt = p.text
                        # HH:MM 형식 찾기 (Time Request: 포함 여부 무관, 전각 콜론 포함)
                        match = re.search(r'(\d{1,2}[:：]\d{2})', txt)
                        if match:
                            # 2025 같은 연도나 예약번호랑 헷갈리지 않게, : 앞뒤가 숫자인지 확인됨
                            # 추가 검증: Time Request나 Session 등이 있거나, 길이가 짧은 경우
                            if any(keyword in txt for keyword in ['Time Request', 'Session', 'Time']):
                                time_text = match.group(1).replace('：', ':') # 정규화
                                break
                            elif len(txt.strip()) < 15 and match.group(1) in txt: # 짧은 텍스트
                                time_text = match.group(1).replace('：', ':')
                                break
                    
                    reservation['time_request'] = time_text

                    if reservation['reservation_number']:
                        extracted_reservations.append(reservation)
                        self.logger.info(f"예약 정보 추출 성공 ({team_name}): {reservation['customer_name']} / {reservation['reservation_number']}")
                
                except Exception as e:
                    self.logger.error(f"개별 예약 항목 추출 중 오류: {e}")
                    continue

            return extracted_reservations

        except Exception as e:
            self.logger.error(f"예약 정보 추출 실패: {e}")
            return []

        finally:
            # 대기 시간 원복
            self.driver.implicitly_wait(original_wait)


    def crawl_date(self, target_date):
        """
        특정 날짜의 예약 정보 크롤링

        Args:
            target_date (str): 크롤링할 날짜 (YYYY-MM-DD)
        """
        try:
            self.logger.info(f"날짜 크롤링 시작: {target_date}")

            # 날짜 파싱
            date_obj = datetime.strptime(target_date, '%Y-%m-%d')
            year = date_obj.year
            month = date_obj.month
            day = date_obj.day

            # 월요일(0) 체크: 월요일은 휴무이므로 스킵
            if date_obj.weekday() == 0:
                self.logger.info(f"{target_date}는 월요일(휴무)이므로 건너뜁니다.")
                return

            # 날짜 선택 프로세스
            self.click_date_picker()
            self.select_month(year, month)
            self.select_day(day)
            self.click_ok_button()

            # 상호 클릭 시도
            # 상호 클릭 시도 (예약 확인용이므로 짧게 3초만 대기)
            try:
                self.click_store(timeout=3)
            except (TimeoutException, NoSuchElementException) as e:
                self.logger.info(f"날짜 {target_date}에 예약이 없습니다 (상호 없음)")
                return  # 예약이 없는 경우 정상 종료

            # 팀 목록 가져오기
            teams = self.get_team_list()

            # 팀이 없으면 예약 없음
            if not teams:
                self.logger.info(f"날짜 {target_date}에 예약이 없습니다 (팀 없음)")
                return

            # 각 팀별로 예약 정보 수집 (stale element 방지)
            for idx in range(len(teams)):
                try:
                    # 최신 팀 리스트를 가져옵니다
                    fresh_teams = self.get_team_list()

                    # 팀 목록이 없으면 상호 클릭 시도 (목록이 닫혔거나 로드되지 않은 경우)
                    if not fresh_teams:
                        self.logger.info("팀 목록이 없어 상호를 다시 클릭합니다.")
                        self.click_store()
                        time.sleep(config.MEDIUM_DELAY)
                        fresh_teams = self.get_team_list()

                    if idx >= len(fresh_teams):
                        self.logger.warning(f"인덱스 {idx}가 최신 팀 리스트 범위를 초과합니다, 중단합니다.")
                        break
                    team_info = fresh_teams[idx]
                    team_name = team_info.get('name', 'UNKNOWN')
                    self.logger.info(f"팀 {idx+1}/{len(teams)} 처리 시작: {team_name}")
                    self.click_team(team_info['element'])

                    # 예약 상세 정보 추출 (리스트 반환됨)
                    reservations_list = self.extract_reservation_details(target_date, team_name)
                    if reservations_list:
                        self.reservations.extend(reservations_list)

                    # 팀 닫기 (중복 추출 방지)
                    self.click_team(team_info['element'])
                    self.logger.info("팀 닫기 완료")

                except Exception as e:
                    self.logger.error(f"팀 처리 중 오류: {e}")
                    continue
                    self.logger.error(f"팀 처리 중 오류: {e}")
                    continue

            self.logger.info(f"날짜 크롤링 완료: {target_date}")

        except Exception as e:
            self.logger.error(f"날짜 크롤링 실패 ({target_date}): {e}")

    def crawl_date_range(self, start_date, end_date):
        """
        날짜 범위의 예약 정보 크롤링

        Args:
            start_date (str): 시작 날짜 (YYYY-MM-DD)
            end_date (str): 종료 날짜 (YYYY-MM-DD)
        """
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')

            current = start
            while current <= end:
                # 각 날짜마다 메인 페이지로 이동하여 상태 초기화
                if current != start:  # 첫 날짜가 아니면 메인 페이지로 이동
                    self.logger.info("다음 날짜를 위해 메인 페이지로 이동")
                    try:
                        self.driver.get(config.BASE_URL)
                    except Exception as e:
                        # Alert로 인한 에러 발생 시 Alert 처리
                        self.logger.warning(f"페이지 로드 중 에러 발생 (Alert 가능성): {e}")
                        try:
                            alert = self.driver.switch_to.alert
                            alert_text = alert.text
                            alert.dismiss()
                            self.logger.info(f"Alert 팝업 닫기 완료: {alert_text}")
                            time.sleep(config.SHORT_DELAY)
                            # Alert 닫은 후 다시 페이지 로드
                            self.driver.get(config.BASE_URL)
                        except:
                            pass

                    time.sleep(config.MEDIUM_DELAY)

                date_str = current.strftime('%Y-%m-%d')
                self.crawl_date(date_str)
                current += timedelta(days=1)

            self.logger.info(f"날짜 범위 크롤링 완료: {start_date} ~ {end_date}")

        except Exception as e:
            self.logger.error(f"날짜 범위 크롤링 실패: {e}")

    def close(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()
            self.logger.info("브라우저 종료")

    def get_reservations(self):
        """수집된 예약 정보 반환"""
        return self.reservations


if __name__ == "__main__":
    crawler = KTourCrawler(headless=False)

    try:
        # WebDriver 설정
        crawler.setup_driver()

        # 로그인
        crawler.login()

        # 특정 날짜 크롤링
        crawler.crawl_date("2025-12-05")

        # 또는 날짜 범위 크롤링
        # crawler.crawl_date_range(config.START_DATE, config.END_DATE)

        # 결과 출력
        reservations = crawler.get_reservations()
        print(f"\n총 {len(reservations)}개의 예약 정보 수집")

        for idx, res in enumerate(reservations, 1):
            print(f"\n[{idx}] {res}")

    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")

    finally:
        crawler.close()
