
import requests
import json
import logging
import os
from datetime import datetime

class SlackNotifier:
    """슬랙 알림 전송 클래스"""
    
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        self.logger = logging.getLogger(__name__)

    def send_message(self, message):
        """
        슬랙 메시지 전송
        
        Args:
            message (str): 전송할 메시지 내용
            
        Returns:
            bool: 전송 성공 여부
        """
        if not self.webhook_url:
            self.logger.warning("Slack Webhook URL이 설정되지 않아 알림을 보낼 수 없습니다.")
            return False
            
        try:
            payload = {'text': message}
            response = requests.post(
                self.webhook_url, 
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                self.logger.info("슬랙 알림 전송 성공")
                return True
            else:
                self.logger.error(f"슬랙 알림 전송 실패: HTML status code {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"슬랙 알림 전송 중 오류 발생: {e}")
            return False
            
    def format_reservation_message(self, reservations, title="예약 알림", include_date=False, mark_new=True, notify_everyone=False, sheet_url=None):
        """
        예약 리스트를 슬랙 메시지 포맷으로 변환 (세미-카드형)

        Args:
            reservations (list): 예약 정보 리스트
            title (str): 메시지 제목
            include_date (bool): 라인에 날짜 포함 여부
            mark_new (bool): 신규 예약 강조 표시 여부
            notify_everyone (bool): @channel 알림 포함 여부
            sheet_url (str): 구글 시트 URL (선택)

        Returns:
            str: 포맷팅된 메시지
        """
        if not reservations:
            return f"*{title}*\n해당하는 예약이 없습니다."

        message = []

        # @channel 알림
        if notify_everyone:
            message.append("<!channel>")

        # 제목
        message.append(f"📅 *{title}*\n")

        # 신규/기존 예약 분리
        new_reservations = [r for r in reservations if mark_new and r.get('is_new', False)]
        existing_reservations = [r for r in reservations if not (mark_new and r.get('is_new', False))]

        idx = 1

        # 신규 예약 섹션
        if new_reservations:
            message.append("━━━━━━━━━━━━━━━━━━")
            message.append(f"🚨 *[신규 예약 {len(new_reservations)}건]*\n")

            for res in new_reservations:
                # 고객명
                name = res.get('customer_name', '고객')
                team = res.get('team', '')
                if team and team != 'TEAM 1':
                    name_line = f"*{idx}. {name}* ({team})"
                else:
                    name_line = f"*{idx}. {name}*"
                message.append(name_line)

                # 시간, 채널, 인원
                time = res.get('time_request', '시간미정')
                channel = res.get('channel', '-')
                people = res.get('people_count', '-')

                # 날짜 포함 여부
                if include_date:
                    date = res.get('date', '')
                    message.append(f"📅 {date} | 🕐 {time} | 🧭 {channel} | 👤 {people}")
                else:
                    message.append(f"🕐 {time} | 🧭 {channel} | 👤 {people}")

                # 서비스 및 가격
                product = res.get('product', '-')
                price = res.get('price', 0)
                message.append(f"✂️ {product}")
                message.append(f"💰 {price:,}원")

                if idx < len(new_reservations):
                    message.append("")  # 빈 줄

                idx += 1

            message.append("━━━━━━━━━━━━━━━━━━\n")

        # 기존 예약 섹션
        if existing_reservations:
            message.append(f"*[기존 예약 {len(existing_reservations)}건]*\n")

            for res in existing_reservations:
                # 고객명
                name = res.get('customer_name', '고객')
                team = res.get('team', '')
                if team and team != 'TEAM 1':
                    name_line = f"*{idx}. {name}* ({team})"
                else:
                    name_line = f"*{idx}. {name}*"
                message.append(name_line)

                # 시간, 채널, 인원
                time = res.get('time_request', '시간미정')
                channel = res.get('channel', '-')
                people = res.get('people_count', '-')

                # 날짜 포함 여부
                if include_date:
                    date = res.get('date', '')
                    message.append(f"📅 {date} | 🕐 {time} | 🧭 {channel} | 👤 {people}")
                else:
                    message.append(f"🕐 {time} | 🧭 {channel} | 👤 {people}")

                # 서비스 및 가격 (한 줄로)
                product = res.get('product', '-')
                price = res.get('price', 0)
                message.append(f"✂️ {product} | 💰 {price:,}원\n")

                idx += 1

        # 총 매출 계산
        total_price = sum(r.get('price', 0) for r in reservations)

        # 하단 요약
        message.append("━━━━━━━━━━━━━━━━━━")
        message.append(f"💵 오늘 총 매출: *{total_price:,}원*")

        # 시트 바로가기
        if sheet_url:
            message.append(f"🔗 <{sheet_url}|시트 바로가기>")

        return "\n".join(message)
