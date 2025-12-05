"""
KTour 예약 현황 크롤러 메인 실행 스크립트
"""

import argparse
import logging
from datetime import datetime

from crawler import KTourCrawler
from data_saver import DataSaver
from google_sheets_manager import GoogleSheetsManager
from utils import PasswordFilter
import config


def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('crawler.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    # 패스워드 필터 추가
    password_filter = PasswordFilter()
    for handler in logging.root.handlers:
        handler.addFilter(password_filter)


def main():
    """메인 실행 함수"""
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(description='KTour 예약 현황 크롤러')
    parser.add_argument('--date', type=str, help='크롤링할 날짜 (YYYY-MM-DD)')
    parser.add_argument('--start-date', type=str, help='시작 날짜 (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='종료 날짜 (YYYY-MM-DD)')
    parser.add_argument('--headless', action='store_true', help='헤드리스 모드 실행')
    parser.add_argument('--output-format', type=str, choices=['csv', 'excel', 'json'],
                        default='csv', help='출력 형식 (기본값: csv)')
    parser.add_argument('--output-file', type=str, help='출력 파일명')
    parser.add_argument('--google-sheets', action='store_true', help='구글 시트에 저장')
    parser.add_argument('--sheets-url', type=str, help='구글 시트 URL')

    args = parser.parse_args()

    # 로깅 설정
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("=" * 80)
    logger.info("KTour 예약 현황 크롤러 시작")
    logger.info("=" * 80)

    # 크롤러 초기화
    crawler = KTourCrawler(headless=args.headless)
    saver = DataSaver(output_dir=config.OUTPUT_DIR)

    try:
        # WebDriver 설정
        crawler.setup_driver()

        # 로그인
        crawler.login()

        # 날짜 정보 파악 (파일명 생성용)
        start_date = None
        end_date = None

        # 크롤링 실행
        if args.date:
            # 단일 날짜 크롤링
            logger.info(f"단일 날짜 크롤링: {args.date}")
            crawler.crawl_date(args.date)
            start_date = end_date = args.date

        elif args.start_date and args.end_date:
            # 날짜 범위 크롤링
            logger.info(f"날짜 범위 크롤링: {args.start_date} ~ {args.end_date}")
            crawler.crawl_date_range(args.start_date, args.end_date)
            start_date = args.start_date
            end_date = args.end_date

        else:
            # 기본값: config 파일의 날짜 범위 사용
            logger.info(f"기본 날짜 범위 크롤링: {config.START_DATE} ~ {config.END_DATE}")
            crawler.crawl_date_range(config.START_DATE, config.END_DATE)
            start_date = config.START_DATE
            end_date = config.END_DATE

        # 수집된 데이터 가져오기
        reservations = crawler.get_reservations()

        logger.info("=" * 80)
        logger.info(f"크롤링 완료: 총 {len(reservations)}건의 예약 정보 수집")
        logger.info("=" * 80)

        # 데이터가 있으면 저장
        if reservations:
            # 날짜 기반 파일명 생성 (사용자가 지정하지 않은 경우)
            if args.output_file is None:
                if start_date == end_date:
                    base_filename = f"reservations_{start_date}"
                else:
                    base_filename = f"reservations_{start_date}_to_{end_date}"
            else:
                base_filename = args.output_file

            # 데이터 저장
            if args.output_format == 'csv':
                saved_file = saver.save_to_csv(reservations, base_filename)
            elif args.output_format == 'excel':
                saved_file = saver.save_to_excel(reservations, base_filename)
            elif args.output_format == 'json':
                saved_file = saver.save_to_json(reservations, base_filename)

            if saved_file:
                logger.info(f"데이터 저장 완료: {saved_file}")

            # 요약 통계 저장
            summary_file = saver.save_summary(reservations)
            if summary_file:
                logger.info(f"요약 통계 저장 완료: {summary_file}")

            # 구글 시트에 저장
            if args.google_sheets or config.GOOGLE_SHEETS_ENABLED:
                sheets_url = args.sheets_url or config.GOOGLE_SHEETS_URL
                if sheets_url:
                    logger.info("구글 시트에 저장 중...")
                    sheets_manager = GoogleSheetsManager(config.GOOGLE_SHEETS_CREDENTIALS)
                    success = sheets_manager.append_data(
                        sheets_url,
                        reservations,
                        config.GOOGLE_SHEETS_WORKSHEET
                    )
                    if success:
                        logger.info(f"구글 시트 저장 완료: {sheets_url}")
                        # 서식 적용
                        spreadsheet = sheets_manager.open_sheet(sheets_url)
                        if spreadsheet:
                            worksheet = spreadsheet.worksheet(config.GOOGLE_SHEETS_WORKSHEET)
                            sheets_manager.format_worksheet(worksheet)
                    else:
                        logger.error("구글 시트 저장 실패")
                else:
                    logger.warning("구글 시트 URL이 설정되지 않았습니다")

            # 요약 통계 출력
            summary = saver.get_summary_statistics(reservations)
            logger.info("\n" + "=" * 80)
            logger.info("요약 통계")
            logger.info("=" * 80)
            logger.info(f"총 예약 건수: {summary.get('total_count', 0)}")

            if summary.get('date_range'):
                logger.info(f"날짜 범위: {summary['date_range']['start']} ~ {summary['date_range']['end']}")

            if summary.get('by_date'):
                logger.info("\n날짜별 예약 건수:")
                for date, count in sorted(summary['by_date'].items()):
                    logger.info(f"  {date}: {count}건")

            if summary.get('by_team'):
                logger.info("\n팀별 예약 건수:")
                for team, count in summary['by_team'].items():
                    logger.info(f"  {team}: {count}건")

            if summary.get('by_channel'):
                logger.info("\n채널별 예약 건수:")
                for channel, count in summary['by_channel'].items():
                    logger.info(f"  {channel}: {count}건")

            logger.info("=" * 80)

        else:
            logger.warning("수집된 예약 정보가 없습니다")

    except Exception as e:
        logger.error(f"크롤링 중 오류 발생: {e}", exc_info=True)
        return 1

    finally:
        # 브라우저 종료
        crawler.close()
        logger.info("크롤러 종료")

    return 0


if __name__ == "__main__":
    exit(main())
