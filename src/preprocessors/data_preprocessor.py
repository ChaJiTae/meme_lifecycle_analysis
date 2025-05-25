import pandas as pd
import numpy as np
from datetime import datetime
import re
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

class DataPreprocessor:
    def __init__(self):
        """데이터 전처리기 초기화"""
        self.raw_data_dir = RAW_DATA_DIR
        self.processed_data_dir = PROCESSED_DATA_DIR
        
    def load_reddit_data(self, filename):
        """Reddit 데이터 로드"""
        filepath = os.path.join(self.raw_data_dir, filename)
        df = pd.read_csv(filepath)
        print(f"Reddit 데이터 로드: {len(df)}개 게시물")
        return df
    
    def preprocess_reddit(self, df):
        """Reddit 데이터 전처리"""
        print("\n=== Reddit 데이터 전처리 시작 ===")
        
        # 1. 날짜 형식 변환
        df['created_utc'] = pd.to_datetime(df['created_utc'])
        
        # 2. 중복 제거
        original_count = len(df)
        df = df.drop_duplicates(subset=['id'])
        print(f"중복 제거: {original_count} -> {len(df)}개")
        
        # 3. 결측치 처리
        df['selftext'] = df['selftext'].fillna('')
        df['author'] = df['author'].fillna('[deleted]')
        
        # 4. 파생 변수 생성
        df['title_length'] = df['title'].str.len()
        df['has_text'] = df['selftext'].str.len() > 0
        df['engagement_score'] = df['score'] + df['num_comments'] * 2
        
        # 5. 시간 관련 변수 추가
        df['hour'] = df['created_utc'].dt.hour
        df['day_of_week'] = df['created_utc'].dt.dayofweek
        df['date'] = df['created_utc'].dt.date
        
        # 6. 텍스트 정제
        df['title_clean'] = df['title'].apply(self.clean_text)
        df['selftext_clean'] = df['selftext'].apply(self.clean_text)
        
        print(f"전처리 완료: {len(df)}개 게시물")
        return df
    
    def clean_text(self, text):
        """텍스트 정제"""
        if pd.isna(text) or text == '':
            return ''
        
        # URL 제거
        text = re.sub(r'https?://\S+|www.\S+', '', text)
        
        # 이모지 제거 (선택사항)
        # text = re.sub(r'[^\w\s]', '', text)
        
        # 여러 공백을 하나로
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def analyze_temporal_patterns(self, df):
        """시간 패턴 분석"""
        print("\n=== 시간 패턴 분석 ===")
        
        # 일별 게시물 수
        daily_posts = df.groupby('date').size()
        print(f"데이터 기간: {daily_posts.index.min()} ~ {daily_posts.index.max()}")
        print(f"일 평균 게시물 수: {daily_posts.mean():.2f}")
        
        # 시간대별 분포
        hourly_dist = df['hour'].value_counts().sort_index()
        peak_hour = hourly_dist.idxmax()
        print(f"가장 활발한 시간대: {peak_hour}시")
        
        # 요일별 분포
        days = ['월', '화', '수', '목', '금', '토', '일']
        day_dist = df['day_of_week'].value_counts().sort_index()
        peak_day = days[day_dist.idxmax()]
        print(f"가장 활발한 요일: {peak_day}요일")
        
        return {
            'daily_posts': daily_posts,
            'hourly_dist': hourly_dist,
            'day_dist': day_dist
        }
    
    def save_processed_data(self, df, output_filename):
        """전처리된 데이터 저장"""
        os.makedirs(self.processed_data_dir, exist_ok=True)
        output_path = os.path.join(self.processed_data_dir, output_filename)
        
        df.to_csv(output_path, index=False)
        print(f"\n전처리된 데이터 저장: {output_path}")
        
        # 요약 정보 저장
        summary = {
            'total_posts': len(df),
            'date_range': f"{df['created_utc'].min()} ~ {df['created_utc'].max()}",
            'unique_authors': df['author'].nunique(),
            'unique_subreddits': df['subreddit'].nunique(),
            'avg_score': df['score'].mean(),
            'avg_comments': df['num_comments'].mean()
        }
        
        summary_path = output_path.replace('.csv', '_summary.txt')
        with open(summary_path, 'w', encoding='utf-8') as f:
            for key, value in summary.items():
                f.write(f"{key}: {value}\n")
        
        return df

# 실행 코드
if __name__ == "__main__":
    # 전처리기 생성
    preprocessor = DataPreprocessor()
    
    # 가장 최근 Reddit 데이터 파일 찾기
    import glob
    reddit_files = glob.glob(os.path.join(RAW_DATA_DIR, 'reddit_chill_guy_*.csv'))
    
    if reddit_files:
        # 가장 최근 파일 선택
        latest_file = max(reddit_files, key=os.path.getctime)
        filename = os.path.basename(latest_file)
        
        print(f"처리할 파일: {filename}")
        
        # 데이터 로드 및 전처리
        df = preprocessor.load_reddit_data(filename)
        df_processed = preprocessor.preprocess_reddit(df)
        
        # 시간 패턴 분석
        temporal_patterns = preprocessor.analyze_temporal_patterns(df_processed)
        
        # 저장
        output_filename = filename.replace('reddit_', 'processed_reddit_')
        preprocessor.save_processed_data(df_processed, output_filename)
    else:
        print("Reddit 데이터 파일을 찾을 수 없습니다.")
