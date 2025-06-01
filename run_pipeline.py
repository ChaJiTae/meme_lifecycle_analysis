#!/usr/bin/env python3
"""
밈 수명 주기 분석 전체 파이프라인 실행 스크립트
"""

import argparse
import sys
import time
import glob
import os
import pandas as pd
from datetime import datetime

# 프로젝트 루트 디렉토리를 sys.path에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.collectors.reddit_collector import RedditCollector
from src.preprocessors.data_preprocessor import DataPreprocessor
from src.visualizers.meme_visualizer import MemeVisualizer
from src.analyzers.lifecycle_analyzer import LifecycleAnalyzer
from src.utils import create_directories
from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

def run_collection(meme_name, platforms=['reddit']):
    """데이터 수집 단계"""
    print(f"\n{'='*50}")
    print(f"1단계: 데이터 수집 - {meme_name}")
    print(f"{'='*50}")
    
    collected_files = []
    
    # Reddit 수집
    if 'reddit' in platforms:
        try:
            print(f"Reddit에서 '{meme_name}' 데이터 수집 중...")
            collector = RedditCollector()
            posts = collector.collect_meme_data(meme_name)
            if posts:
                collected_files.append('reddit')
                print(f"✓ Reddit에서 {len(posts)}개 게시물 수집 완료")
            else:
                print("✗ Reddit 데이터 수집 실패")
        except Exception as e:
            print(f"✗ Reddit 수집 실패: {e}")
    
    # Twitter 수집 (향후 구현)
    if 'twitter' in platforms:
        try:
            print(f"Twitter에서 '{meme_name}' 데이터 수집 중...")
            # from src.collectors.twitter_collector import TwitterCollector
            # collector = TwitterCollector()
            # collector.collect_meme_data(meme_name)
            # collected_files.append('twitter')
            print("Twitter 수집기는 아직 구현되지 않았습니다.")
        except Exception as e:
            print(f"✗ Twitter 수집 실패: {e}")
    
    # Instagram 수집 (향후 구현)
    if 'instagram' in platforms:
        try:
            print(f"Instagram에서 '{meme_name}' 데이터 수집 중...")
            # from src.collectors.instagram_collector import InstagramCollector
            # collector = InstagramCollector()
            # collector.collect_meme_data(meme_name)
            # collected_files.append('instagram')
            print("Instagram 수집기는 아직 구현되지 않았습니다.")
        except Exception as e:
            print(f"✗ Instagram 수집 실패: {e}")
    
    return collected_files

def run_preprocessing(meme_name):
    """데이터 전처리 단계"""
    print(f"\n{'='*50}")
    print(f"2단계: 데이터 전처리")
    print(f"{'='*50}")
    
    preprocessor = DataPreprocessor()
    
    # 수집된 데이터 파일 찾기 (가장 최근 파일)
    meme_safe_name = meme_name.replace(' ', '_').lower()
    pattern = f"reddit_{meme_safe_name}_*.csv"
    files = glob.glob(os.path.join(RAW_DATA_DIR, pattern))
    
    if not files:
        print(f"✗ 전처리할 데이터를 찾을 수 없습니다: {pattern}")
        return None
    
    # 가장 최근 파일 선택
    latest_file = max(files, key=os.path.getctime)
    filename = os.path.basename(latest_file)
    
    print(f"전처리할 파일: {filename}")
    
    try:
        # 데이터 로드 및 전처리
        df = preprocessor.load_reddit_data(filename)
        df_processed = preprocessor.preprocess_reddit(df)
        
        # 시간 패턴 분석
        temporal_patterns = preprocessor.analyze_temporal_patterns(df_processed)
        
        # 저장
        output_filename = filename.replace('reddit_', 'processed_reddit_')
        preprocessor.save_processed_data(df_processed, output_filename)
        
        print(f"✓ 전처리 완료: {output_filename}")
        return output_filename
        
    except Exception as e:
        print(f"✗ 전처리 실패: {e}")
        return None

def run_visualization(processed_filename, meme_name):
    """시각화 단계"""
    print(f"\n{'='*50}")
    print(f"3단계: 시각화 생성")
    print(f"{'='*50}")
    
    try:
        visualizer = MemeVisualizer()
        
        # 전처리된 데이터 로드
        filepath = os.path.join(PROCESSED_DATA_DIR, processed_filename)
        df = pd.read_csv(filepath)
        df['created_utc'] = pd.to_datetime(df['created_utc'])
        df['date'] = pd.to_datetime(df['date'])
        
        meme_safe_name = meme_name.replace(' ', '_').lower()
        
        print("시각화 생성 중...")
        
        # 각 시각화 생성
        visualizer.plot_lifecycle_curve(df, meme_safe_name)
        visualizer.plot_engagement_analysis(df, meme_safe_name)
        visualizer.plot_subreddit_distribution(df, meme_safe_name)
        visualizer.plot_lifecycle_phases(df, meme_safe_name)
        visualizer.create_summary_dashboard(df, meme_safe_name)
        
        print("✓ 모든 시각화 완료!")
        return True
        
    except Exception as e:
        print(f"✗ 시각화 생성 실패: {e}")
        return False

def run_analysis(processed_filename, meme_name):
    """분석 단계"""
    print(f"\n{'='*50}")
    print(f"4단계: 수명 주기 분석")
    print(f"{'='*50}")
    
    try:
        analyzer = LifecycleAnalyzer()
        
        # 전처리된 데이터 로드
        filepath = os.path.join(PROCESSED_DATA_DIR, processed_filename)
        df = pd.read_csv(filepath)
        df['created_utc'] = pd.to_datetime(df['created_utc'])
        df['date'] = pd.to_datetime(df['date'])
        
        meme_safe_name = meme_name.replace(' ', '_').lower()
        
        print("수명 주기 분석 중...")
        
        # 분석 실행
        daily_metrics, phases = analyzer.identify_lifecycle_phases(df)
        curve_fit = analyzer.fit_lifecycle_curve(daily_metrics)
        metrics = analyzer.calculate_lifecycle_metrics(df, daily_metrics)
        
        # 보고서 생성
        report_path = analyzer.generate_report(
            meme_safe_name, df, daily_metrics, phases, curve_fit, metrics
        )
        
        print(f"✓ 분석 완료! 보고서: {report_path}")
        return True
        
    except Exception as e:
        print(f"✗ 분석 실패: {e}")
        return False

def validate_environment():
    """환경 설정 검증"""
    print("환경 설정 검증 중...")
    
    # 필요한 디렉토리 생성
    create_directories()
    
    # API 키 확인
    try:
        from config.api_keys import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET
        if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
            print("⚠️  Reddit API 키가 설정되지 않았습니다.")
            print("config/api_keys.py 파일을 확인하세요.")
            return False
    except ImportError:
        print("⚠️  API 키 파일을 찾을 수 없습니다.")
        print("config/api_keys.py 파일을 생성하세요.")
        return False
    
    print("✓ 환경 설정 검증 완료")
    return True

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(
        description='밈 수명 주기 분석 파이프라인',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python run_pipeline.py --meme "chill guy"
  python run_pipeline.py --meme "wojak" --platforms reddit
  python run_pipeline.py --meme "pepe" --skip-collection
        """
    )
    
    parser.add_argument('--meme', type=str, required=True, 
                       help='분석할 밈 이름 (예: "chill guy", "wojak")')
    parser.add_argument('--platforms', nargs='+', default=['reddit'], 
                       choices=['twitter', 'reddit', 'instagram'],
                       help='데이터 수집 플랫폼 (기본값: reddit)')
    parser.add_argument('--skip-collection', action='store_true', 
                       help='데이터 수집 단계 건너뛰기 (기존 데이터 사용)')
    parser.add_argument('--skip-visualization', action='store_true',
                       help='시각화 단계 건너뛰기')
    parser.add_argument('--skip-analysis', action='store_true',
                       help='분석 단계 건너뛰기')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"밈 수명 주기 분석 파이프라인")
    print(f"{'='*60}")
    print(f"분석 대상: {args.meme}")
    print(f"플랫폼: {', '.join(args.platforms)}")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # 환경 검증
    if not validate_environment():
        print("환경 설정을 완료한 후 다시 실행하세요.")
        return 1
    
    start_time = time.time()
    
    try:
        # 1. 데이터 수집
        if not args.skip_collection:
            collected = run_collection(args.meme, args.platforms)
            if not collected:
                print("\n❌ 데이터 수집에 실패했습니다.")
                return 1
            time.sleep(2)
        else:
            print("\n⏭️  데이터 수집 단계를 건너뜁니다.")
        
        # 2. 데이터 전처리
        processed_filename = run_preprocessing(args.meme)
        if not processed_filename:
            print("\n❌ 데이터 전처리에 실패했습니다.")
            return 1
        time.sleep(1)
        
        # 3. 시각화
        if not args.skip_visualization:
            success = run_visualization(processed_filename, args.meme)
            if not success:
                print("\n⚠️  시각화 생성에 실패했지만 계속 진행합니다.")
            time.sleep(1)
        else:
            print("\n⏭️  시각화 단계를 건너뜁니다.")
        
        # 4. 분석
        if not args.skip_analysis:
            success = run_analysis(processed_filename, args.meme)
            if not success:
                print("\n⚠️  분석에 실패했습니다.")
                return 1
        else:
            print("\n⏭️  분석 단계를 건너뜁니다.")
        
        # 완료 메시지
        elapsed_time = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"🎉 파이프라인 완료!")
        print(f"소요 시간: {elapsed_time:.2f}초")
        print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # 결과 파일 위치 안내
        print(f"\n📁 결과 파일 위치:")
        print(f"  - 원본 데이터: data/raw/")
        print(f"  - 전처리된 데이터: data/processed/")
        print(f"  - 시각화: results/figures/")
        print(f"  - 분석 보고서: results/reports/")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⛔ 사용자에 의해 중단되었습니다.")
        return 1
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())