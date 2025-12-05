"""
유틸리티 함수 모듈
"""

from functools import wraps
import time
import logging
import config


def retry(max_attempts=3, delay=2, exceptions=(Exception,)):
    """
    함수 실행 실패 시 자동 재시도 데코레이터

    Args:
        max_attempts (int): 최대 시도 횟수
        delay (int): 재시도 사이 대기 시간(초)
        exceptions (tuple): 재시도할 예외 타입들

    Returns:
        decorator: 데코레이터 함수
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(__name__)

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"{func.__name__} 실패 (최대 시도 횟수 도달): {e}")
                        raise

                    logger.warning(f"{func.__name__} 실패 (시도 {attempt}/{max_attempts}): {e}")
                    logger.info(f"{delay}초 후 재시도...")
                    time.sleep(delay)

        return wrapper
    return decorator


class PasswordFilter(logging.Filter):
    """
    로그에서 패스워드를 마스킹하는 필터
    """

    def filter(self, record):
        """
        로그 레코드에서 패스워드를 '***'로 치환

        Args:
            record: 로그 레코드

        Returns:
            bool: True (항상 통과)
        """
        if config.LOGIN_PASSWORD and isinstance(record.msg, str):
            record.msg = record.msg.replace(config.LOGIN_PASSWORD, '***')

        # args에서도 패스워드 필터링
        if hasattr(record, 'args') and record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: '***' if config.LOGIN_PASSWORD and v == config.LOGIN_PASSWORD else v
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    '***' if config.LOGIN_PASSWORD and arg == config.LOGIN_PASSWORD else arg
                    for arg in record.args
                )

        return True
