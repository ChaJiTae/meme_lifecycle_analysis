import pandas as pd
import numpy as np
from datetime import datetime
import re
import os
import sys
import glob
import argparse

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

def find_latest_reddit_file(meme_name=None):
    """가장 최근 Reddit 데이터 파일 찾기"""
    if meme_name:
        # 특정 밈의 파일 찾기
        meme_safe_name = meme_name.replace(' ', '_').lower()
        pattern = f"reddit_{meme_safe_name}_*.csv"
    else:
        # 모든 Reddit 파일 찾기
        pattern = "reddit_*_*.csv"
    
    reddit_files = glob.glob(os.path.join(RAW_DATA_DIR, pattern))
    
    if reddit_files:
        # 가장 최근 파일 반환
        latest_file = max(reddit_files, key=os.path.getctime)
        return latest_file
    else:
        return None

def extract_meme_name_from_filename(filename):
    """파일명에서 밈 이름 추출"""
    basename = os.path.basename(filename)
    # reddit_meme_name_timestamp.csv 형식
    parts = basename.replace('reddit_', '').replace('.csv', '').split('_')
    
    # 타임스탬프 부분 제거 (마지막 2개 요소: YYYYMMDD, HHMMSS)
    if len(parts) >= 2:
        # 마지막 2개가 숫자인지 확인 (타임스탬프)
        if parts[-1].isdigit() and parts[-2].isdigit() and len(parts[-2]) == 8:
            meme_parts = parts[:-2]
        else:
            meme_parts = parts
    else:
        meme_parts = parts
    
    return '_'.join(meme_parts)

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='Reddit 데이터 전처리')
    parser.add_argument('--meme', type=str, help='처리할 밈 이름')
    parser.add_argument('--file', type=str, help='처리할 특정 파일명')
    
    args = parser.parse_args()
    
    # 전처리기 생성
    preprocessor = DataPreprocessor()
    
    # 처리할 파일 찾기
    if args.file:
        # 특정 파일 지정
        target_file = os.path.join(RAW_DATA_DIR, args.file)
        if not os.path.exists(target_file):
            print(f"파일을 찾을 수 없습니다: {args.file}")
            return
        filename = args.file
        meme_name = extract_meme_name_from_filename(filename)
    else:
        # 가장 최근 파일 또는 특정 밈의 파일 찾기
        latest_file = find_latest_reddit_file(args.meme)
        if not latest_file:
            if args.meme:
                print(f"'{args.meme}' 밈의 Reddit 데이터 파일을 찾을 수 없습니다.")
            else:
                print("Reddit 데이터 파일을 찾을 수 없습니다.")
            return
        
        filename = os.path.basename(latest_file)
        meme_name = extract_meme_name_from_filename(filename)
    
    print(f"처리할 파일: {filename}")
    print(f"밈 이름: {meme_name}")
    
    try:
        # 데이터 로드 및 전처리
        df = preprocessor.load_reddit_data(filename)
        df_processed = preprocessor.preprocess_reddit(df)
        
        # 시간 패턴 분석
        temporal_patterns = preprocessor.analyze_temporal_patterns(df_processed)
        
        # 저장
        output_filename = filename.replace('reddit_', 'processed_reddit_')
        preprocessor.save_processed_data(df_processed, output_filename)
        
        print(f"\n✅ '{meme_name}' 밈 데이터 전처리 완료!")
        
    except Exception as e:
        print(f"❌ 전처리 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

# 실행 코드
if __name__ == "__main__":
    main()