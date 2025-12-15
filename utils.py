"""
유틸리티 함수 모듈
"""

from functools import wraps
import time
import logging
import config
import json
import os
import re


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


def load_prices(file_path='prices.json'):
    """
    가격 정보 로드
    
    Args:
        file_path (str): JSON 파일 경로
        
    Returns:
        dict: 상품명-가격 매핑 딕셔너리
    """
    try:
        if not os.path.exists(file_path):
            return {}
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"가격 정보 로드 실패: {e}")
        return {}


def calculate_price(product_str, price_table):
    """
    상품 문자열에서 가격 계산
    예: "CUT + STYLING X 1" -> (CUT + STYLING 가격) * 1
    
    Args:
        product_str (str): 상품 문자열
        price_table (dict): 가격 테이블
        
    Returns:
        int: 계산된 가격 (매칭 실패 시 0)
    """
    if not product_str:
        return 0
        
    # 수량 파싱
    quantity = 1
    clean_name = product_str
    
    # " X 1", " x 2" 등의 패턴 찾기
    match = re.search(r'\s+[xX]\s*(\d+)$', product_str)
    if match:
        quantity = int(match.group(1))
        clean_name = product_str[:match.start()].strip()
    
    # 가격 테이블에서 찾기
    # 1. 전체 이름 매칭
    unit_price = price_table.get(clean_name)
    
    # 2. 매칭 안되면 " + "로 분리해서 각각 찾아서 합산 시도
    if unit_price is None and '+' in clean_name:
        parts = [p.strip() for p in clean_name.split('+')]
        temp_price = 0
        all_found = True
        for part in parts:
            part_price = price_table.get(part)
            if part_price is None:
                # 개별 부품도 없으면 기본값 시도
                all_found = False
                break
            temp_price += part_price
        
        if all_found:
            unit_price = temp_price
    
    if unit_price is None:
        unit_price = price_table.get('DEFAULT', 0)
    
    return unit_price * quantity
