"""
구글 시트 연동 모듈
예약 데이터를 구글 시트에 저장하고 관리
"""

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import logging
from datetime import datetime


class GoogleSheetsManager:
    """구글 시트 관리 클래스"""

    def __init__(self, credentials_file='credentials.json'):
        """
        초기화

        Args:
            credentials_file (str): 서비스 계정 인증 파일 경로
        """
        self.credentials_file = credentials_file
        self.client = None
        self.logger = logging.getLogger(__name__)

        # 구글 시트 API 스코프
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

    def authenticate(self):
        """구글 시트 인증"""
        try:
            creds = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=self.scopes
            )
            self.client = gspread.authorize(creds)
            self.logger.info("구글 시트 인증 성공")
            return True

        except FileNotFoundError:
            self.logger.error(f"인증 파일을 찾을 수 없습니다: {self.credentials_file}")
            return False

        except Exception as e:
            self.logger.error(f"구글 시트 인증 실패: {e}")
            return False

    def open_sheet(self, spreadsheet_url_or_id):
        """
        스프레드시트 열기

        Args:
            spreadsheet_url_or_id (str): 스프레드시트 URL 또는 ID

        Returns:
            gspread.Spreadsheet: 스프레드시트 객체
        """
        try:
            # 인증이 안 되어 있으면 인증
            if not self.client:
                if not self.authenticate():
                    return None

            # URL에서 ID 추출
            if 'docs.google.com/spreadsheets' in spreadsheet_url_or_id:
                # URL 형식: https://docs.google.com/spreadsheets/d/{ID}/edit
                sheet_id = spreadsheet_url_or_id.split('/d/')[1].split('/')[0]
            else:
                sheet_id = spreadsheet_url_or_id

            spreadsheet = self.client.open_by_key(sheet_id)
            self.logger.info(f"스프레드시트 열기 성공: {spreadsheet.title}")
            return spreadsheet

        except Exception as e:
            self.logger.error(f"스프레드시트 열기 실패: {e}")
            return None

    def get_or_create_worksheet(self, spreadsheet, worksheet_name='예약현황'):
        """
        워크시트 가져오기 또는 생성

        Args:
            spreadsheet: 스프레드시트 객체
            worksheet_name (str): 워크시트 이름

        Returns:
            gspread.Worksheet: 워크시트 객체
        """
        try:
            # 기존 워크시트 찾기
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
                self.logger.info(f"기존 워크시트 사용: {worksheet_name}")
            except gspread.WorksheetNotFound:
                # 없으면 새로 생성
                worksheet = spreadsheet.add_worksheet(
                    title=worksheet_name,
                    rows=1000,
                    cols=20
                )
                self.logger.info(f"새 워크시트 생성: {worksheet_name}")

                # 헤더 추가
                headers = [
                    '날짜', '팀', '고객명', '예약번호', '채널',
                    '인원구분', '국가', '예약상품', '예약시간'
                ]
                worksheet.append_row(headers)
                self.logger.info("헤더 추가 완료")

            return worksheet

        except Exception as e:
            self.logger.error(f"워크시트 처리 실패: {e}")
            return None

    def get_existing_data(self, worksheet):
        """
        기존 데이터 가져오기

        Args:
            worksheet: 워크시트 객체

        Returns:
            pd.DataFrame: 기존 데이터
        """
        try:
            # 모든 데이터 가져오기
            all_values = worksheet.get_all_values()

            if len(all_values) <= 1:
                # 헤더만 있거나 데이터 없음
                return pd.DataFrame()

            # DataFrame 생성 (첫 번째 행을 헤더로)
            df = pd.DataFrame(all_values[1:], columns=all_values[0])

            self.logger.info(f"기존 데이터 {len(df)}건 로드")
            return df

        except Exception as e:
            self.logger.error(f"기존 데이터 가져오기 실패: {e}")
            return pd.DataFrame()

    def remove_duplicates_and_sort(self, existing_df, new_data):
        """
        중복 제거 및 정렬

        Args:
            existing_df (pd.DataFrame): 기존 데이터
            new_data (list): 새 데이터 (딕셔너리 리스트)

        Returns:
            pd.DataFrame: 중복 제거 및 정렬된 데이터
        """
        try:
            # 새 데이터를 DataFrame으로 변환
            new_df = pd.DataFrame(new_data)

            # 컬럼명 통일 (기존 데이터와 매칭)
            column_mapping = {
                'date': '날짜',
                'team': '팀',
                'customer_name': '고객명',
                'reservation_number': '예약번호',
                'channel': '채널',
                'people_count': '인원구분',
                'country': '국가',
                'product': '예약상품',
                'time_request': '예약시간'
            }
            new_df = new_df.rename(columns=column_mapping)

            # 기존 데이터와 새 데이터 병합
            if existing_df.empty:
                combined_df = new_df
            else:
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)

            # 예약번호 기준 중복 제거 (최신 것만 유지)
            if '예약번호' in combined_df.columns:
                # 예약번호가 비어있지 않은 것만 중복 제거
                mask = combined_df['예약번호'].notna() & (combined_df['예약번호'] != '')
                duplicated = combined_df[mask].duplicated(subset=['예약번호'], keep='last')
                combined_df = combined_df[~duplicated | ~mask]

                self.logger.info(f"중복 제거 후: {len(combined_df)}건")

            # 날짜 기준 정렬
            if '날짜' in combined_df.columns:
                combined_df = combined_df.sort_values(by='날짜', ascending=True)
                self.logger.info("날짜순 정렬 완료")

            return combined_df

        except Exception as e:
            self.logger.error(f"중복 제거 및 정렬 실패: {e}")
            return pd.DataFrame()

    def update_worksheet(self, worksheet, df):
        """
        워크시트 업데이트

        Args:
            worksheet: 워크시트 객체
            df (pd.DataFrame): 업데이트할 데이터

        Returns:
            bool: 성공 여부
        """
        try:
            # 기존 데이터 모두 삭제 (헤더 제외)
            worksheet.clear()

            # 헤더 추가
            headers = df.columns.tolist()
            worksheet.append_row(headers)

            # 데이터 추가
            if not df.empty:
                # DataFrame을 리스트로 변환
                values = df.fillna('').values.tolist()

                # 배치로 추가 (속도 향상)
                worksheet.append_rows(values)

            self.logger.info(f"워크시트 업데이트 완료: {len(df)}건")
            return True

        except Exception as e:
            self.logger.error(f"워크시트 업데이트 실패: {e}")
            return False

    def append_data(self, spreadsheet_url_or_id, new_data, worksheet_name='예약현황'):
        """
        데이터 추가 (중복 제거 및 정렬 포함)

        Args:
            spreadsheet_url_or_id (str): 스프레드시트 URL 또는 ID
            new_data (list): 새 데이터 (딕셔너리 리스트)
            worksheet_name (str): 워크시트 이름

        Returns:
            bool: 성공 여부
        """
        try:
            # 스프레드시트 열기
            spreadsheet = self.open_sheet(spreadsheet_url_or_id)
            if not spreadsheet:
                return False

            # 워크시트 가져오기
            worksheet = self.get_or_create_worksheet(spreadsheet, worksheet_name)
            if not worksheet:
                return False

            # 기존 데이터 가져오기
            existing_df = self.get_existing_data(worksheet)

            # 중복 제거 및 정렬
            merged_df = self.remove_duplicates_and_sort(existing_df, new_data)

            # 워크시트 업데이트
            success = self.update_worksheet(worksheet, merged_df)

            if success:
                self.logger.info(f"구글 시트 업데이트 완료: {len(merged_df)}건")
                return True
            else:
                return False

        except Exception as e:
            self.logger.error(f"데이터 추가 실패: {e}")
            return False

    def format_worksheet(self, worksheet):
        """
        워크시트 서식 설정

        Args:
            worksheet: 워크시트 객체
        """
        try:
            # 헤더 행 서식 (굵게, 배경색)
            worksheet.format('1', {
                'backgroundColor': {
                    'red': 0.2,
                    'green': 0.4,
                    'blue': 0.9
                },
                'textFormat': {
                    'foregroundColor': {
                        'red': 1.0,
                        'green': 1.0,
                        'blue': 1.0
                    },
                    'fontSize': 11,
                    'bold': True
                },
                'horizontalAlignment': 'CENTER'
            })

            # 고정 행 설정 (헤더 고정)
            worksheet.freeze(rows=1)

            self.logger.info("워크시트 서식 설정 완료")

        except Exception as e:
            self.logger.error(f"워크시트 서식 설정 실패: {e}")

    def get_sheet_url(self, spreadsheet):
        """
        스프레드시트 URL 가져오기

        Args:
            spreadsheet: 스프레드시트 객체

        Returns:
            str: 스프레드시트 URL
        """
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}/edit"


# 간편 함수
def save_to_google_sheets(data, spreadsheet_url, credentials_file='credentials.json', worksheet_name='예약현황'):
    """
    구글 시트에 데이터 저장 (간편 함수)

    Args:
        data (list): 저장할 데이터 (딕셔너리 리스트)
        spreadsheet_url (str): 스프레드시트 URL
        credentials_file (str): 인증 파일 경로
        worksheet_name (str): 워크시트 이름

    Returns:
        bool: 성공 여부
    """
    manager = GoogleSheetsManager(credentials_file)
    return manager.append_data(spreadsheet_url, data, worksheet_name)


if __name__ == "__main__":
    # 테스트 코드
    import logging
    logging.basicConfig(level=logging.INFO)

    # 샘플 데이터
    sample_data = [
        {
            'date': '2025-12-05',
            'team': 'TEAM 1',
            'customer_name': 'Sara He (1)',
            'reservation_number': 'KCW680912',
            'channel': 'L',
            'people_count': 'Ad: 1 Kd: 0 Bb: 0',
            'country': 'NEW ZEALAND',
            'product': 'PERSONAL STYLE CONSULTING + CUT + STYLING X 1',
            'time_request': 'Time Request: 12:00'
        }
    ]

    # 구글 시트에 저장
    manager = GoogleSheetsManager()

    # 스프레드시트 URL 또는 ID 입력 필요
    # spreadsheet_url = "YOUR_SPREADSHEET_URL_HERE"
    # success = manager.append_data(spreadsheet_url, sample_data)

    print("GoogleSheetsManager 모듈 준비 완료")
    print("실제 사용 시 credentials.json 파일과 스프레드시트 URL이 필요합니다")
