#!/usr/bin/env python3
"""
밈 수명 주기 분석 전체 파이프라인 실행 스크립트
"""

import argparse
import sys
import time
import glob
import os
from datetime import datetime

from src.collectors.twitter_collector import TwitterCollector
from src.collectors.reddit_collector import RedditCollector
from src.collectors.instagram_collector import InstagramCollector
from src.preprocessors.data_preprocessor import DataPreprocessor
from src.visualizers.meme_visualizer import MemeVisualizer
from src.analyzers.lifecycle_analyzer import LifecycleAnalyzer
from config.config import TARGET_MEMES, RAW_DATA_DIR, PROCESSED_DATA_DIR

def run_collection(meme_name, platforms=['reddit']):
    """데이터 수집 단계"""
    print(f"\n{'='*50}")
    print(f"1단계: 데이터 수집 - {meme_name}")
    print(f"{'='*50}")
    
    collected_files = []
    
    if 'twitter' in platforms:
        try:
            collector = TwitterCollector()
            collector.collect_meme_data(meme_name)
            collected_files.append('twitter')
        except Exception as e:
            print(f"Twitter 수집 실패: {e}")
    
    if 'reddit' in platforms:
        try:
            collector = RedditCollector()
            collector.collect_meme_data(meme_name)
            collected_files.append('reddit')
        except Exception as e:
            print(f"Reddit 수집 실패: {e}")
    
    if 'instagram' in platforms:
        try:
            collector = InstagramCollector()
            collector.collect_meme_data(meme_name)
            collected_files.append('instagram')
        except Exception as e:
            print(f"Instagram 수집 실패: {e}")
    
    return collected_files

def run_preprocessing(meme_name):
    """데이터 전처리 단계"""
    print(f"\n{'='*50}")
    print(f"2단계: 데이터 전처리")
    print(f"{'='*50}")
    
    preprocessor = DataPreprocessor()
    
    # Reddit 데이터 찾기 (가장 최근 파일)
    pattern = f"reddit_{meme_name.replace(' ', '_').lower()}_*.csv"
    files = glob.glob(os.path.join(RAW_DATA_DIR, pattern))
    
    if files:
        latest_file = max(files, key=os.path.getctime)
        filename = os.path.basename(latest_file)
        
        df = preprocessor.load_reddit_data(filename)
        df_processed = preprocessor.preprocess_reddit(df)
        temporal_patterns = preprocessor.analyze_temporal_patterns(df_processed)
        
        output_filename = filename.replace('reddit_', 'processed_reddit_')
        preprocessor.save_processed_data(df_processed, output_filename)
        
        return output_filename
    else:
        print("전처리할 데이터를 찾을 수 없습니다.")
        return None

def run_visualization(processed_filename, meme_name):
    """시각화 단계"""
    print(f"\n{'='*50}")
    print(f"3단계: 시각화 생성")
    print(f"{'='*50}")
    
    visualizer = MemeVisualizer()
    
    # 전처리된 데이터 로드
    filepath = os.path.join(PROCESSED_DATA_DIR, processed_filename)
    df = pd.read_csv(filepath)
    df['created_utc'] = pd.to_datetime(df['created_utc'])
    df['date'] = pd.to_datetime(df['date'])
    
    # 시각화 생성
    visualizer.plot_lifecycle_curve(df, meme_name.replace(' ', '_').lower())
    visualizer.plot_engagement_analysis(df, meme_name.replace(' ', '_').lower())
    visualizer.plot_subreddit_distribution(df, meme_name.replace(' ', '_').lower())
    visualizer.plot_lifecycle_phases(df, meme_name.replace(' ', '_').lower())
    visualizer.create_summary_dashboard(df, meme_name.replace(' ', '_').lower())
    
    print("✓ 모든 시각화 완료!")

def run_analysis(processed_filename, meme_name):
    """분석 단계"""
    print(f"\n{'='*50}")
    print(f"4단계: 수명 주기 분석")
    print(f"{'='*50}")
    
    analyzer = LifecycleAnalyzer()
    
    # 전처리된 데이터 로드
    filepath = os.path.join(PROCESSED_DATA_DIR, processed_filename)
    df = pd.read_csv(filepath)
    df['created_utc'] = pd.to_datetime(df['created_utc'])
    df['date'] = pd.to_datetime(df['date'])
    
    # 분석 실행
    daily_metrics, phases = analyzer.identify_lifecycle_phases(df)
    curve_fit = analyzer.fit_lifecycle_curve(daily_metrics)
    metrics = analyzer.calculate_lifecycle_metrics(df, daily_metrics)
    
    # 보고서 생성
    report_path = analyzer.generate_report(
        meme_name.replace(' ', '_').lower(), 
        df, daily_metrics, phases, curve_fit, metrics
    )
    
    print(f"✓ 분석 완료! 보고서: {report_path}")

def main():
    parser = argparse.ArgumentParser(description='밈 수명 주기 분석 파이프라인')
    parser.add_argument('--meme', type=str, default='chill guy', help='분석할 밈 이름')
    parser.add_argument('--platforms', nargs='+', default=['reddit'], 
                       choices=['twitter', 'reddit', 'instagram'],
                       help='데이터 수집 플랫폼')
    parser.add_argument('--skip-collection', action='store_true', 
                       help='데이터 수집 단계 건너뛰기')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"밈 수명 주기 분석 파이프라인 시작")
    print(f"분석 대상: {args.meme}")
    print(f"플랫폼: {', '.join(args.platforms)}")
    print(f"시작 시간: {datetime.now()}")
    print(f"{'='*60}")
    
    try:
        # 1. 데이터 수집
        if not args.skip_collection:
            collected = run_collection(args.meme, args.platforms)
            if not collected:
                print("데이터 수집 실패!")
                return
            time.sleep(2)
        
        # 2. 데이터 전처리
        processed_filename = run_preprocessing(args.meme)
        if not processed_filename:
            print("전처리 실패!")
            return
        time.sleep(2)
        
        # 3. 시각화
        import pandas as pd  # 여기서 import
        run_visualization(processed_filename, args.meme)
        time.sleep(2)
        
        # 4. 분석
        run_analysis(processed_filename, args.meme)
        
        print(f"\n{'='*60}")
        print(f"파이프라인 완료!")
        print(f"종료 시간: {datetime.now()}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()