"""
Slack 메시지 형식 테스트
"""
from slack_notifier import SlackNotifier

# 테스트 데이터
test_reservations = [
    {
        'date': '2025-12-20',
        'team': 'TEAM 1',
        'customer_name': 'Anita Tifentale',
        'reservation_number': 'QEP003448',
        'channel': 'KLOOK',
        'people_count': 'Ad: 1 Kd: 0 Bb: 0',
        'country': 'Latvia',
        'product': 'CUT + STYLING',
        'time_request': '10:30',
        'price': 150000,
        'is_new': True  # 신규 예약
    },
    {
        'date': '2025-12-20',
        'team': 'TEAM 2',
        'customer_name': 'Cristina Tran',
        'reservation_number': 'VGS049491',
        'channel': 'Naver',
        'people_count': 'Ad: 1 Kd: 0 Bb: 0',
        'country': 'Vietnam',
        'product': 'PERSONAL COLOR DIAGNOSIS',
        'time_request': '11:00',
        'price': 80000,
        'is_new': False  # 기존 예약
    },
    {
        'date': '2025-12-20',
        'team': 'TEAM 3',
        'customer_name': 'Cristina Tran',
        'reservation_number': 'VUM187947',
        'channel': 'Klook',
        'people_count': 'Ad: 1 Kd: 0 Bb: 0',
        'country': 'Vietnam',
        'product': 'DESIGN CUT + COLORING',
        'time_request': '14:00',
        'price': 220000,
        'is_new': False  # 기존 예약
    },
    {
        'date': '2025-12-20',
        'team': 'TEAM 4',
        'customer_name': 'Cristina Tran',
        'reservation_number': 'GKC177782',
        'channel': 'Klook',
        'people_count': 'Ad: 1 Kd: 0 Bb: 0',
        'country': 'Vietnam',
        'product': 'HAIR STYLING',
        'time_request': '15:30',
        'price': 100000,
        'is_new': False  # 기존 예약
    },
    {
        'date': '2025-12-20',
        'team': 'TEAM 1',
        'customer_name': 'Unknown',
        'reservation_number': 'DIR123456',
        'channel': 'Direct',
        'people_count': 'Ad: 1 Kd: 0 Bb: 0',
        'country': 'Korea',
        'product': 'CONSULTATION',
        'time_request': '16:00',
        'price': 50000,
        'is_new': True  # 신규 예약
    }
]

# 슬랙 알림 객체 생성
slack = SlackNotifier()

# 당일 예약 메시지 생성
message = slack.format_reservation_message(
    test_reservations,
    title="오늘(2025-12-20) 예약 현황",
    include_date=False,
    mark_new=True,
    notify_everyone=True,
    sheet_url="https://docs.google.com/spreadsheets/d/1xFu0KNT6DDiHRJofGb9YS-S3inpjwfJrttW7z7GV4kA/edit"
)

print("=" * 50)
print("슬랙 메시지 미리보기:")
print("=" * 50)

# UTF-8 인코딩 문제 해결을 위해 파일에 저장
with open('slack_message_preview.txt', 'w', encoding='utf-8') as f:
    f.write(message)

print("메시지가 'slack_message_preview.txt' 파일에 저장되었습니다.")
print("\n[메시지 내용]")
print(message.encode('utf-8', errors='replace').decode('utf-8'))
print("=" * 50)
