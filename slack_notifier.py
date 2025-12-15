
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
            
    def format_reservation_message(self, reservations, title="예약 알림", include_date=False, mark_new=True, notify_everyone=False):
        """
        예약 리스트를 슬랙 메시지 포맷으로 변환
        
        Args:
            reservations (list): 예약 정보 리스트
            title (str): 메시지 제목
            include_date (bool): 라인에 날짜 포함 여부
            mark_new (bool): 신규 예약 강조 표시 여부 (아이콘 및 볼드)
            notify_everyone (bool): @channel 알림 포함 여부
            
        Returns:
            str: 포맷팅된 메시지
        """
        if not reservations:
            return f"*{title}*\n해당하는 예약이 없습니다."
            
        message = []
        if notify_everyone:
            message.append("<!channel>")
            
        message.append(f"*{title}* (총 {len(reservations)}건)\n")
        
        for idx, res in enumerate(reservations, 1):
            # 신규 예약 표시 prefix
            is_new = res.get('is_new', False)
            prefix = ""
            if mark_new and is_new:
                prefix = "🚨 *[NEW]* "
            
            # 데이터 구성
            date_part = f"*{res.get('date', '')}* " if include_date else ""
            time = res.get('time_request', '시간미정')
            channel = res.get('channel', '-')
            name = res.get('customer_name', '고객')
            product = res.get('product', '')
            price = f"{res.get('price', 0):,}원"
            
            # 번호 추가: "1. " 형태
            line = f"{idx}. {prefix}{date_part}{time} | {channel} | {name} | {product} | {price}"
            
            # 신규 예약 강조 (mark_new가 True일 때만)
            if mark_new and is_new:
                line = f"*{line}*" 
                
            message.append(line)
            
        return "\n".join(message)
