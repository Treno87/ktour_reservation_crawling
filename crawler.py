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

    def click_store(self, store_name="마리엠헤어"):
        """
        상호 클릭

        Args:
            store_name (str): 클릭할 상호명

        Raises:
            TimeoutException: 상호 요소를 찾지 못한 경우 (예약 없음)
            NoSuchElementException: 상호 요소가 없는 경우 (예약 없음)
        """
        store_element = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, f'//h6[text()="{store_name}"]'))
        )
        store_element.click()
        time.sleep(config.MEDIUM_DELAY)

        self.logger.info(f"상호 클릭 완료: {store_name}")

    def get_team_list(self):
        """팀 목록 가져오기"""
        try:
            # 팀 정보가 있는 요소들 찾기
            team_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                'div.MuiBox-root.css-k008qs'
            )

            teams = []
            for element in team_elements:
                try:
                    team_chips = element.find_elements(By.CSS_SELECTOR, 'div.MuiChip-root')
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
            team_element.click()
            time.sleep(config.MEDIUM_DELAY)
            self.logger.info("팀 클릭 완료")

        except Exception as e:
            self.logger.error(f"팀 클릭 실패: {e}")
            raise

    def extract_reservation_details(self, target_date):
        """
        예약 상세 정보 추출

        Args:
            target_date (str): 예약 날짜 (YYYY-MM-DD)

        Returns:
            dict: 예약 정보
        """
        try:
            reservation = {
                'date': target_date,
                'team': '',
                'customer_name': '',
                'reservation_number': '',
                'channel': '',
                'people_count': '',
                'country': '',
                'product': '',
                'time_request': ''
            }

            # 팀 정보
            try:
                team_label = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'span.MuiChip-label.MuiChip-labelSmall.css-19imqg1'
                )
                reservation['team'] = team_label.text
            except:
                pass

            # 고객명
            try:
                customer_name = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'h6.MuiTypography-root.MuiTypography-subtitle1.css-qdk4z1'
                )
                reservation['customer_name'] = customer_name.text
            except:
                pass

            # 예약번호
            try:
                reservation_number = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'h6.MuiTypography-root.MuiTypography-subtitle2.css-1r042ka'
                )
                reservation['reservation_number'] = reservation_number.text
            except:
                pass

            # 채널약자
            try:
                channel = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'div.MuiAvatar-root.MuiAvatar-circular.MuiAvatar-colorDefault.MuiChip-avatar.MuiChip-avatarSmall.MuiChip-avatarColorPrimary.css-1buxfho'
                )
                reservation['channel'] = channel.text
            except:
                pass

            # 인원구분 및 수
            try:
                people_count = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'p.MuiTypography-root.MuiTypography-subtitle2.css-mdkayp'
                )
                reservation['people_count'] = people_count.text.strip()
            except:
                pass

            # 국가
            try:
                country = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'span.MuiTypography-root.MuiTypography-subtitle2.css-xcju41'
                )
                reservation['country'] = country.text
            except:
                pass

            # 예약상품
            try:
                product = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'p.MuiTypography-root.MuiTypography-subtitle2.css-1q5lgor'
                )
                product_text = product.text
                # "AB: " 제거 (대소문자 구분 없이)
                if ':' in product_text:
                    product_text = product_text.split(':', 1)[1].strip()
                reservation['product'] = product_text
            except:
                pass

            # 예약시간
            try:
                time_request = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'p.MuiTypography-root.MuiTypography-subtitle2.css-17exa0r'
                )
                time_text = time_request.text
                # "Time Request: " 제거
                if ':' in time_text:
                    time_text = time_text.split(':', 1)[1].strip()
                reservation['time_request'] = time_text
            except:
                pass

            self.logger.info(f"예약 정보 추출 완료: {reservation['reservation_number']}")
            return reservation

        except Exception as e:
            self.logger.error(f"예약 정보 추출 실패: {e}")
            return None

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

            # 날짜 선택 프로세스
            self.click_date_picker()
            self.select_month(year, month)
            self.select_day(day)
            self.click_ok_button()

            # 상호 클릭 시도
            try:
                self.click_store()
            except (TimeoutException, NoSuchElementException) as e:
                self.logger.info(f"날짜 {target_date}에 예약이 없습니다 (상호 없음)")
                return  # 예약이 없는 경우 정상 종료

            # 팀 목록 가져오기
            teams = self.get_team_list()

            # 팀이 없으면 예약 없음
            if not teams:
                self.logger.info(f"날짜 {target_date}에 예약이 없습니다 (팀 없음)")
                return

            # 각 팀별로 예약 정보 수집
            for team_info in teams:
                try:
                    self.click_team(team_info['element'])

                    # 예약 상세 정보 추출
                    reservation = self.extract_reservation_details(target_date)
                    if reservation:
                        self.reservations.append(reservation)

                    # 뒤로 가기 (다음 팀을 위해)
                    self.driver.back()
                    time.sleep(config.SHORT_DELAY)

                except Exception as e:
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
                    self.driver.get(config.BASE_URL)
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
