import os,platform
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

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

def set_global_font():
    system = platform.system()
    if system == "Darwin":  # macOS
        font_path = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
    elif system == "Windows":
        font_path = "C:/Windows/Fonts/malgun.ttf"
    else:
        font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"  # 예시
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
    
    return font_prop.get_name()

# 실제로 한 번 설정 적용,
DEFAULT_FONT = set_global_font()


# 데이터 수집 기간
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)

# 기타 설정
BATCH_SIZE = 100
MAX_TWEETS_PER_MEME = 10000
MAX_REDDIT_POSTS_PER_MEME = 5000
