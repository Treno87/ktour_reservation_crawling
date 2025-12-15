import logging
import calendar
from datetime import datetime, timedelta
from crawler import KTourCrawler
from google_sheets_manager import GoogleSheetsManager
from slack_notifier import SlackNotifier
from utils import load_prices, calculate_price
import config
import os
from dotenv import load_dotenv
import pandas as pd

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_sync.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_date_range():
    """오늘부터 이번 달 말일까지의 날짜 범위를 반환"""
    today = datetime.now()
    _, last_day = calendar.monthrange(today.year, today.month)
    last_date = today.replace(day=last_day)
    
    start_str = today.strftime("%Y-%m-%d")
    end_str = last_date.strftime("%Y-%m-%d")
    return start_str, end_str

def main():
    logger.info("Daily Synchronization Started")
    
    # Slack 알림 초기화
    slack = SlackNotifier()

    # 1. 날짜 범위 계산
    start_date, end_date = get_date_range()
    today_str = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"Sync Range: {start_date} ~ {end_date}")

    # 2. 크롤링 실행
    crawler = KTourCrawler(headless=True)
    crawled_reservations = []
    
    try:
        crawler.setup_driver()
        crawler.login()
        crawler.crawl_date_range(start_date, end_date)
        crawled_reservations = crawler.get_reservations()
        logger.info(f"Crawled {len(crawled_reservations)} reservations.")

    except Exception as e:
        logger.error(f"Crawling failed: {e}")
        slack.send_message(f"🚨 크롤링 배치 작업 실패: {e}")
        return
    finally:
        crawler.close()

    if not crawled_reservations:
        logger.info("No reservations found to sync.")
        slack.send_message(f"📅 *{today_str}* 예약 현황 알림\n\n크롤링된 예약이 없습니다 (휴무일 제외).")
        return

    # 3. 가격 정보 계산
    price_table = load_prices('prices.json')
    for res in crawled_reservations:
        res['price'] = calculate_price(res.get('product', ''), price_table)

    # 4. 기존 데이터 가져오기 (중복/신규 판별용)
    sheet_url = os.getenv('GOOGLE_SHEETS_URL') or config.GOOGLE_SHEETS_URL
    if not sheet_url:
        logger.error("Google Sheets URL is missing.")
        return

    manager = GoogleSheetsManager(config.GOOGLE_SHEETS_CREDENTIALS)
    
    # 시트 연결 및 기존 데이터 로드
    existing_reservation_numbers = set()
    try:
        spreadsheet = manager.open_sheet(sheet_url)
        if spreadsheet:
            worksheet = manager.get_or_create_worksheet(spreadsheet, config.GOOGLE_SHEETS_WORKSHEET)
            existing_df = manager.get_existing_data(worksheet)
            
            if not existing_df.empty and '예약번호' in existing_df.columns:
                existing_reservation_numbers = set(existing_df['예약번호'].astype(str).tolist())
    except Exception as e:
        logger.warning(f"기존 데이터 로드 실패 (신규 여부 판단 불가): {e}")

    # 5. 신규 예약 식별
    new_reservation_count = 0
    for res in crawled_reservations:
        res['is_new'] = False
        res_num = str(res.get('reservation_number', ''))
        if res_num and res_num not in existing_reservation_numbers:
            res['is_new'] = True
            new_reservation_count += 1
            
    logger.info(f"Found {new_reservation_count} new reservations.")

    # 6. 구글 시트 동기화 (전체 데이터 덮어쓰기 or 병합)
    # google_sheets_manager.append_data는 내부적으로 deduplication을 수행하므로 전체를 넘겨도 안전함
    # 다만 'is_new' 플래그는 시트에 저장할 필요가 없으므로 그대로 두거나 제거해도 무방 (헤더에 없으면 무시됨)
    try:
        success = manager.append_data(sheet_url, crawled_reservations, config.GOOGLE_SHEETS_WORKSHEET)
        if success:
            logger.info("Google Sheets sync completed successfully.")
        else:
            logger.error("Failed to sync with Google Sheets.")
            slack.send_message("⚠️ 구글 시트 동기화 실패")
    except Exception as e:
        logger.error(f"Error during Google Sheets sync: {e}")

    # 7. Slack 알림 전송
    
    # 7-1. 당일(오늘) 예약 현황 (전체 표시 + 신규 표시)
    today_reservations = [r for r in crawled_reservations if r['date'] == today_str]
    today_msg = slack.format_reservation_message(
        today_reservations, 
        title=f"📅 오늘({today_str}) 예약 현황",
        include_date=False, # 당일은 날짜 생략
        mark_new=True,      # 신규 예약 강조
        notify_everyone=True # 채널 전체 알림
    )
    slack.send_message(today_msg)
    
    # 7-2. 익일~말일 신규 예약 알림 (신규만 표시)
    future_new_reservations = [
        r for r in crawled_reservations 
        if r['date'] > today_str and r.get('is_new')
    ]
    
    if future_new_reservations:
        future_msg = slack.format_reservation_message(
            future_new_reservations,
            title=f"🚨 [NEW] 미래({start_date} 이후) 신규 예약 알림",
            include_date=True, # 미래 예약은 날짜 필수
            mark_new=False,    # 이미 전체가 New이므로 개별 강조 생략
            notify_everyone=True # 채널 전체 알림
        )
        slack.send_message(future_msg)
    else:
        logger.info("No new future reservations to notify.")

if __name__ == "__main__":
    main()
