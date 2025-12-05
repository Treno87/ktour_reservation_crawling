"""
KTour 예약 크롤러 웹 인터페이스
"""

from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime, timedelta
import os
import threading
import json

from crawler import KTourCrawler
from data_saver import DataSaver
from google_sheets_manager import GoogleSheetsManager
import config

app = Flask(__name__)

# 크롤링 상태 관리
crawling_status = {
    'is_running': False,
    'progress': 0,
    'total': 0,
    'current_date': '',
    'message': '',
    'result_file': None
}


def generate_date_range(start_date, end_date, mode='daily'):
    """
    날짜 범위 생성

    Args:
        start_date (str): 시작 날짜 (YYYY-MM-DD)
        end_date (str): 종료 날짜 (YYYY-MM-DD)
        mode (str): daily, weekly, monthly

    Returns:
        list: 크롤링할 날짜 리스트
    """
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')

    dates = []

    if mode == 'daily':
        current = start
        while current <= end:
            dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)

    elif mode == 'weekly':
        current = start
        while current <= end:
            dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(weeks=1)

    elif mode == 'monthly':
        current = start
        while current <= end:
            dates.append(current.strftime('%Y-%m-%d'))
            # 다음 달 같은 날
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

    return dates


def run_crawler_task(store_name, start_date, end_date, mode, output_format, google_sheets=False, sheets_url=''):
    """
    백그라운드에서 크롤러 실행

    Args:
        store_name (str): 상호명
        start_date (str): 시작 날짜
        end_date (str): 종료 날짜
        mode (str): daily, weekly, monthly
        output_format (str): csv, excel, json
        google_sheets (bool): 구글 시트 저장 여부
        sheets_url (str): 구글 시트 URL
    """
    global crawling_status

    crawler = None

    try:
        # 상태 초기화
        crawling_status['is_running'] = True
        crawling_status['progress'] = 0
        crawling_status['message'] = '크롤러 초기화 중...'

        # 날짜 범위 생성
        dates = generate_date_range(start_date, end_date, mode)
        crawling_status['total'] = len(dates)

        # 크롤러 초기화
        crawler = KTourCrawler(headless=True)
        saver = DataSaver(output_dir=config.OUTPUT_DIR)

        crawling_status['message'] = 'WebDriver 설정 중...'
        crawler.setup_driver()

        crawling_status['message'] = '로그인 중...'
        crawler.login()

        # 각 날짜 크롤링
        for idx, date in enumerate(dates):
            crawling_status['current_date'] = date
            crawling_status['message'] = f'{date} 크롤링 중...'

            try:
                # 날짜 크롤링
                crawler.crawl_date(date)

                crawling_status['progress'] = idx + 1

            except Exception as e:
                crawling_status['message'] = f'{date} 크롤링 실패: {str(e)}'
                continue

        # 데이터 저장
        crawling_status['message'] = '데이터 저장 중...'
        reservations = crawler.get_reservations()

        if reservations:
            # 파일명 생성
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reservations_{store_name}_{start_date}_to_{end_date}_{timestamp}"

            # 형식에 따라 저장
            if output_format == 'csv':
                result_file = saver.save_to_csv(reservations, f"{filename}.csv")
            elif output_format == 'excel':
                result_file = saver.save_to_excel(reservations, f"{filename}.xlsx")
            elif output_format == 'json':
                result_file = saver.save_to_json(reservations, f"{filename}.json")

            # 요약 통계도 저장
            saver.save_summary(reservations, f"summary_{filename}.json")

            # 구글 시트에 저장
            if google_sheets and sheets_url:
                crawling_status['message'] = '구글 시트에 저장 중...'
                try:
                    sheets_manager = GoogleSheetsManager(config.GOOGLE_SHEETS_CREDENTIALS)
                    success = sheets_manager.append_data(
                        sheets_url,
                        reservations,
                        config.GOOGLE_SHEETS_WORKSHEET
                    )
                    if success:
                        # 서식 적용
                        spreadsheet = sheets_manager.open_sheet(sheets_url)
                        if spreadsheet:
                            worksheet = spreadsheet.worksheet(config.GOOGLE_SHEETS_WORKSHEET)
                            sheets_manager.format_worksheet(worksheet)
                        crawling_status['message'] = f'완료! {len(reservations)}건 수집 (구글 시트 저장 완료)'
                    else:
                        crawling_status['message'] = f'완료! {len(reservations)}건 수집 (구글 시트 저장 실패)'
                except Exception as e:
                    crawling_status['message'] = f'완료! {len(reservations)}건 수집 (구글 시트 오류: {str(e)})'
            else:
                crawling_status['message'] = f'완료! {len(reservations)}건 수집'

            crawling_status['result_file'] = result_file
        else:
            crawling_status['message'] = '수집된 데이터가 없습니다'
            crawling_status['result_file'] = None

    except Exception as e:
        crawling_status['message'] = f'오류 발생: {str(e)}'
        crawling_status['result_file'] = None

    finally:
        if crawler:
            crawler.close()

        crawling_status['is_running'] = False
        crawling_status['progress'] = crawling_status['total']


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


@app.route('/api/start', methods=['POST'])
def start_crawling():
    """크롤링 시작"""
    global crawling_status

    # 이미 실행 중이면 거부
    if crawling_status['is_running']:
        return jsonify({
            'success': False,
            'message': '이미 크롤링이 진행 중입니다'
        }), 400

    # 요청 데이터 파싱
    data = request.json
    store_name = data.get('store_name', '마리엠헤어')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    mode = data.get('mode', 'daily')  # daily, weekly, monthly
    output_format = data.get('output_format', 'csv')
    google_sheets = data.get('google_sheets', False)
    sheets_url = data.get('sheets_url', '')

    # 필수 필드 확인
    if not start_date or not end_date:
        return jsonify({
            'success': False,
            'message': '시작 날짜와 종료 날짜를 입력해주세요'
        }), 400

    # 날짜 유효성 검증
    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({
            'success': False,
            'message': '날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)'
        }), 400

    # 백그라운드 스레드로 크롤링 시작
    thread = threading.Thread(
        target=run_crawler_task,
        args=(store_name, start_date, end_date, mode, output_format, google_sheets, sheets_url)
    )
    thread.daemon = True
    thread.start()

    return jsonify({
        'success': True,
        'message': '크롤링이 시작되었습니다'
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """크롤링 상태 조회"""
    global crawling_status

    return jsonify({
        'is_running': crawling_status['is_running'],
        'progress': crawling_status['progress'],
        'total': crawling_status['total'],
        'current_date': crawling_status['current_date'],
        'message': crawling_status['message'],
        'result_file': crawling_status['result_file']
    })


@app.route('/api/download/<path:filename>')
def download_file(filename):
    """결과 파일 다운로드"""
    file_path = os.path.join(config.OUTPUT_DIR, filename)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({
            'success': False,
            'message': '파일을 찾을 수 없습니다'
        }), 404


@app.route('/api/files', methods=['GET'])
def list_files():
    """출력 파일 목록 조회"""
    try:
        output_dir = config.OUTPUT_DIR

        if not os.path.exists(output_dir):
            return jsonify({'files': []})

        files = []
        for filename in os.listdir(output_dir):
            filepath = os.path.join(output_dir, filename)

            if os.path.isfile(filepath):
                file_info = {
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'modified': datetime.fromtimestamp(
                        os.path.getmtime(filepath)
                    ).strftime('%Y-%m-%d %H:%M:%S')
                }
                files.append(file_info)

        # 수정 시간 기준 내림차순 정렬
        files.sort(key=lambda x: x['modified'], reverse=True)

        return jsonify({'files': files})

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'파일 목록 조회 실패: {str(e)}'
        }), 500


if __name__ == '__main__':
    # output 디렉토리 생성
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)

    print("=" * 60)
    print("KTour 예약 크롤러 웹 인터페이스")
    print("=" * 60)
    print("\n브라우저에서 http://localhost:5000 접속하세요\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
