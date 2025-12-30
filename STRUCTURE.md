# 프로젝트 구조

## 📁 루트 디렉토리 (실행에 필요한 파일만)

```
ktour_reservation_crawling/
├── main.py                      ⭐ 메인 실행 파일
├── config.py                    ⚙️ 설정 (날짜 자동 계산)
├── crawler.py                   🤖 크롤링 핵심 로직
├── data_saver.py                💾 데이터 저장 (CSV/Excel/JSON)
├── google_sheets_manager.py     📊 구글 시트 연동
├── slack_notifier.py            💬 Slack 알림
├── utils.py                     🔧 유틸리티 함수
├── prices.json                  💰 가격표
├── requirements.txt             📦 Python 패키지
├── run_daily.bat                🚀 배치 스크립트
├── README.md                    📖 프로젝트 설명
└── .gitignore                   🚫 Git 제외 파일

## 📂 보관 디렉토리

archive/
├── docs/                        📚 과거 문서들
├── web_ui/                      🌐 Flask 웹 인터페이스
│   ├── static/
│   ├── templates/
│   └── web_app.py

tests/                           🧪 테스트 파일들
├── test_crawling.py
├── test_login.py
└── ...

## 🚀 사용법

### 기본 실행
```bash
python main.py
```
- 실행일부터 2주간 크롤링
- 구글 시트 자동 동기화
- Slack 알림 전송

### 특정 날짜 범위
```bash
python main.py --start-date 2026-01-01 --end-date 2026-01-31
```

## ✨ 주요 기능

✅ 자동 크롤링 (실행일 + 2주)
✅ 가격 자동 계산
✅ 구글 시트 동기화
✅ Slack 알림 (오늘 예약 + 미래 신규)
✅ 신규/기존 예약 구분
✅ CSV/Excel/JSON 저장
