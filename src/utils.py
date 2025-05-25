import os
import json
from datetime import datetime
import hashlib

def create_directories():
    """필요한 디렉토리들을 생성"""
    from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, FIGURES_DIR, REPORTS_DIR
    
    directories = [RAW_DATA_DIR, PROCESSED_DATA_DIR, FIGURES_DIR, REPORTS_DIR]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"디렉토리 생성/확인: {directory}")

def generate_file_hash(content):
    """콘텐츠의 해시값 생성 (중복 제거용)"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def load_json_file(filepath):
    """JSON 파일 로드"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"JSON 파일 로드 실패: {e}")
        return None

def save_json_file(data, filepath):
    """데이터를 JSON 파일로 저장"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"JSON 파일 저장 완료: {filepath}")
    except Exception as e:
        print(f"JSON 파일 저장 실패: {e}")

def format_timestamp(dt):
    """datetime 객체를 문자열로 포맷"""
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt)

def sanitize_filename(filename):
    """파일명에 사용할 수 없는 문자 제거"""
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename