"""
데이터 저장 모듈
"""

import os
import json
import pandas as pd
from datetime import datetime
import logging


class DataSaver:
    """데이터 저장 클래스"""

    def __init__(self, output_dir="output"):
        """
        초기화

        Args:
            output_dir (str): 출력 디렉토리
        """
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)

        # 출력 디렉토리 생성
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.logger.info(f"출력 디렉토리 생성: {output_dir}")

    def save_to_csv(self, data, filename=None):
        """
        CSV 파일로 저장

        Args:
            data (list): 저장할 데이터 (딕셔너리 리스트)
            filename (str): 파일명 (없으면 자동 생성)

        Returns:
            str: 저장된 파일 경로
        """
        try:
            if not data:
                self.logger.warning("저장할 데이터가 없습니다")
                return None

            # 파일명 생성
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"reservations_{timestamp}"

            # 확장자 자동 추가
            if not filename.endswith('.csv'):
                filename = filename + '.csv'

            filepath = os.path.join(self.output_dir, filename)

            # DataFrame 생성 및 저장
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')

            self.logger.info(f"CSV 저장 완료: {filepath} ({len(data)}건)")
            return filepath

        except Exception as e:
            self.logger.error(f"CSV 저장 실패: {e}")
            return None

    def save_to_excel(self, data, filename=None):
        """
        Excel 파일로 저장

        Args:
            data (list): 저장할 데이터 (딕셔너리 리스트)
            filename (str): 파일명 (없으면 자동 생성)

        Returns:
            str: 저장된 파일 경로
        """
        try:
            if not data:
                self.logger.warning("저장할 데이터가 없습니다")
                return None

            # 파일명 생성
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"reservations_{timestamp}"

            # 확장자 자동 추가
            if not filename.endswith('.xlsx'):
                filename = filename + '.xlsx'

            filepath = os.path.join(self.output_dir, filename)

            # DataFrame 생성 및 저장
            df = pd.DataFrame(data)

            # Excel 작성
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Reservations')

                # 워크시트 가져오기
                worksheet = writer.sheets['Reservations']

                # 열 너비 자동 조정
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(str(col))
                    )
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)

            self.logger.info(f"Excel 저장 완료: {filepath} ({len(data)}건)")
            return filepath

        except Exception as e:
            self.logger.error(f"Excel 저장 실패: {e}")
            return None

    def save_to_json(self, data, filename=None):
        """
        JSON 파일로 저장

        Args:
            data (list): 저장할 데이터 (딕셔너리 리스트)
            filename (str): 파일명 (없으면 자동 생성)

        Returns:
            str: 저장된 파일 경로
        """
        try:
            if not data:
                self.logger.warning("저장할 데이터가 없습니다")
                return None

            # 파일명 생성
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"reservations_{timestamp}"

            # 확장자 자동 추가
            if not filename.endswith('.json'):
                filename = filename + '.json'

            filepath = os.path.join(self.output_dir, filename)

            # JSON 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"JSON 저장 완료: {filepath} ({len(data)}건)")
            return filepath

        except Exception as e:
            self.logger.error(f"JSON 저장 실패: {e}")
            return None

    def append_to_csv(self, data, filename):
        """
        기존 CSV 파일에 데이터 추가

        Args:
            data (list): 추가할 데이터 (딕셔너리 리스트)
            filename (str): 파일명

        Returns:
            str: 저장된 파일 경로
        """
        try:
            if not data:
                self.logger.warning("추가할 데이터가 없습니다")
                return None

            filepath = os.path.join(self.output_dir, filename)

            # DataFrame 생성
            df_new = pd.DataFrame(data)

            # 기존 파일이 있으면 추가, 없으면 새로 생성
            if os.path.exists(filepath):
                df_existing = pd.read_csv(filepath, encoding='utf-8-sig')
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                df_combined.to_csv(filepath, index=False, encoding='utf-8-sig')
                self.logger.info(f"CSV 추가 완료: {filepath} (+{len(data)}건)")
            else:
                df_new.to_csv(filepath, index=False, encoding='utf-8-sig')
                self.logger.info(f"CSV 생성 완료: {filepath} ({len(data)}건)")

            return filepath

        except Exception as e:
            self.logger.error(f"CSV 추가 실패: {e}")
            return None

    def get_summary_statistics(self, data):
        """
        데이터 요약 통계

        Args:
            data (list): 분석할 데이터

        Returns:
            dict: 통계 정보
        """
        try:
            if not data:
                return {}

            df = pd.DataFrame(data)

            summary = {
                'total_count': len(df),
                'date_range': {
                    'start': df['date'].min() if 'date' in df.columns else None,
                    'end': df['date'].max() if 'date' in df.columns else None
                },
                'by_date': df.groupby('date').size().to_dict() if 'date' in df.columns else {},
                'by_team': df.groupby('team').size().to_dict() if 'team' in df.columns else {},
                'by_channel': df.groupby('channel').size().to_dict() if 'channel' in df.columns else {},
                'by_country': df.groupby('country').size().to_dict() if 'country' in df.columns else {}
            }

            return summary

        except Exception as e:
            self.logger.error(f"통계 생성 실패: {e}")
            return {}

    def save_summary(self, data, filename=None):
        """
        요약 통계를 JSON 파일로 저장

        Args:
            data (list): 분석할 데이터
            filename (str): 파일명 (없으면 자동 생성)

        Returns:
            str: 저장된 파일 경로
        """
        try:
            summary = self.get_summary_statistics(data)

            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"summary_{timestamp}.json"

            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)

            self.logger.info(f"요약 통계 저장 완료: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"요약 통계 저장 실패: {e}")
            return None
