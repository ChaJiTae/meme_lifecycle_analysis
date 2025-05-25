import os
from datetime import datetime

# 프로젝트 루트 경로
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 데이터 경로
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')

# 결과 경로
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')
FIGURES_DIR = os.path.join(RESULTS_DIR, 'figures')
REPORTS_DIR = os.path.join(RESULTS_DIR, 'reports')

# 분석 대상 밈 목록
TARGET_MEMES = [
    "Italian Brain Rot",
    "chill guy",
    "나니가스키",
    # 추가 밈들...
]

# 데이터 수집 기간
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)

# 기타 설정
BATCH_SIZE = 100
MAX_TWEETS_PER_MEME = 10000
MAX_REDDIT_POSTS_PER_MEME = 5000
