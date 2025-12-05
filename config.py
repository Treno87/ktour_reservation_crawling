# 크롤링 설정 파일
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 사이트 정보 (환경변수에서 로드)
BASE_URL = os.getenv('BASE_URL', "https://guide.ktourstory.com/")

# 로그인 정보 (환경변수에서 로드)
LOGIN_ID = os.getenv('LOGIN_ID')
LOGIN_PASSWORD = os.getenv('LOGIN_PASSWORD')

# 크롤링 설정
IMPLICIT_WAIT = 10  # 암묵적 대기 시간 (초)
EXPLICIT_WAIT = 15  # 명시적 대기 시간 (초)
PAGE_LOAD_TIMEOUT = 30  # 페이지 로드 타임아웃 (초)

# 데이터 저장 설정
OUTPUT_DIR = "output"
OUTPUT_FORMAT = "csv"  # csv 또는 json

# 크롤링할 날짜 범위 (YYYY-MM-DD 형식) - 환경변수에서 로드
START_DATE = os.getenv('START_DATE', "2025-12-05")
END_DATE = os.getenv('END_DATE', "2025-12-31")

# 대기 시간 설정 (초)
SHORT_DELAY = 1
MEDIUM_DELAY = 2
LONG_DELAY = 3

# 구글 시트 설정
GOOGLE_SHEETS_ENABLED = False  # 구글 시트 사용 여부
GOOGLE_SHEETS_CREDENTIALS = "credentials.json"  # 서비스 계정 인증 파일
GOOGLE_SHEETS_URL = ""  # 스프레드시트 URL (예: https://docs.google.com/spreadsheets/d/...)
GOOGLE_SHEETS_WORKSHEET = "예약현황"  # 워크시트 이름
