"""
개선사항 테스트 스크립트
"""

import logging
import sys


def test_config_import():
    """config 모듈이 환경변수를 올바르게 로드하는지 테스트"""
    print("=" * 60)
    print("1. Config 환경변수 로드 테스트")
    print("=" * 60)

    try:
        import config

        # 로그인 정보 확인
        if config.LOGIN_ID and config.LOGIN_PASSWORD:
            print("[OK] 로그인 정보 로드 성공")
            print(f"  - LOGIN_ID: {config.LOGIN_ID[:5]}***")
            print(f"  - LOGIN_PASSWORD: ***")
        else:
            print("[FAIL] 로그인 정보 로드 실패")
            print("  .env 파일을 확인하세요")
            return False

        # 날짜 범위 확인
        if config.START_DATE and config.END_DATE:
            print("[OK] 날짜 범위 로드 성공")
            print(f"  - START_DATE: {config.START_DATE}")
            print(f"  - END_DATE: {config.END_DATE}")
        else:
            print("[FAIL] 날짜 범위 로드 실패")
            return False

        return True

    except Exception as e:
        print(f"[FAIL] Config 로드 실패: {e}")
        return False


def test_retry_decorator():
    """재시도 데코레이터 테스트"""
    print("\n" + "=" * 60)
    print("2. Retry 데코레이터 테스트")
    print("=" * 60)

    try:
        from utils import retry

        attempt_count = 0

        @retry(max_attempts=3, delay=0.1)
        def failing_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception(f"시도 {attempt_count} 실패")
            return "성공!"

        result = failing_function()
        print(f"[OK] Retry 데코레이터 동작 확인 (시도 횟수: {attempt_count})")
        print(f"  - 결과: {result}")
        return True

    except Exception as e:
        print(f"[FAIL] Retry 데코레이터 테스트 실패: {e}")
        return False


def test_password_filter():
    """패스워드 필터 테스트"""
    print("\n" + "=" * 60)
    print("3. 패스워드 필터 테스트")
    print("=" * 60)

    try:
        from utils import PasswordFilter
        import config

        # 임시 로거 생성
        test_logger = logging.getLogger('test_logger')
        test_logger.setLevel(logging.INFO)

        # 스트링 핸들러 추가
        import io
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.INFO)

        # 패스워드 필터 추가
        password_filter = PasswordFilter()
        handler.addFilter(password_filter)
        test_logger.addHandler(handler)

        # 패스워드가 포함된 로그 출력
        test_password = "test_password_123"
        original_password = config.LOGIN_PASSWORD
        config.LOGIN_PASSWORD = test_password

        test_logger.info(f"비밀번호는 {test_password} 입니다")

        # 로그 내용 확인
        log_output = log_stream.getvalue()
        config.LOGIN_PASSWORD = original_password

        if test_password not in log_output and "***" in log_output:
            print("[OK] 패스워드 필터 동작 확인")
            print(f"  - 원본: '비밀번호는 {test_password} 입니다'")
            print(f"  - 필터링: '{log_output.strip()}'")
            return True
        else:
            print("[FAIL] 패스워드 필터가 제대로 동작하지 않음")
            return False

    except Exception as e:
        print(f"[FAIL] 패스워드 필터 테스트 실패: {e}")
        return False


def test_crawler_initialization():
    """크롤러 초기화 테스트 (WebDriver 없이)"""
    print("\n" + "=" * 60)
    print("4. 크롤러 초기화 테스트")
    print("=" * 60)

    try:
        from crawler import KTourCrawler

        # 크롤러 인스턴스 생성 (headless 모드)
        crawler = KTourCrawler(headless=True)

        print("[OK] 크롤러 인스턴스 생성 성공")
        print(f"  - Headless 모드: {crawler.headless}")
        print(f"  - 예약 리스트 초기화: {len(crawler.reservations)} 건")

        return True

    except Exception as e:
        print(f"[FAIL] 크롤러 초기화 실패: {e}")
        return False


def main():
    """모든 테스트 실행"""
    print("\n")
    print("=" * 60)
    print(" " * 15 + "개선사항 테스트 시작")
    print("=" * 60)
    print()

    tests = [
        ("환경변수 로드", test_config_import),
        ("재시도 로직", test_retry_decorator),
        ("패스워드 필터", test_password_filter),
        ("크롤러 초기화", test_crawler_initialization),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n예외 발생: {e}")
            results.append((test_name, False))

    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {test_name}")

    print("\n" + "=" * 60)
    print(f"전체: {passed}/{total} 테스트 통과")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
