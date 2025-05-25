#!/usr/bin/env python3
"""
밈 수명 주기 분석 프로젝트 - 메인 실행 파일
"""

import argparse
import sys
import time
from datetime import datetime

from src.collectors.twitter_collector import TwitterCollector
from src.collectors.reddit_collector import RedditCollector
from src.collectors.instagram_collector import InstagramCollector
from src.utils import create_directories, sanitize_filename
from config.config import TARGET_MEMES

def collect_twitter_data(meme_name):
    """Twitter에서 밈 데이터 수집"""
    print(f"\n=== Twitter에서 '{meme_name}' 데이터 수집 시작 ===")
    try:
        collector = TwitterCollector()
        
        # 해시태그 변형 생성
        base_tag = meme_name.replace(" ", "").lower()
        hashtags = [base_tag, f"{base_tag}meme"]
        
        tweets = collector.collect_meme_data(meme_name, hashtags)
        print(f"✓ {len(tweets)}개의 트윗 수집 완료")
        
        return True
    except Exception as e:
        print(f"✗ Twitter 수집 실패: {e}")
        return False

def collect_reddit_data(meme_name):
    """Reddit에서 밈 데이터 수집"""
    print(f"\n=== Reddit에서 '{meme_name}' 데이터 수집 시작 ===")
    try:
        collector = RedditCollector()
        
        # 주요 밈 서브레딧
        subreddits = ['memes', 'dankmemes', 'meme', 'AdviceAnimals']
        
        posts = collector.collect_meme_data(meme_name, subreddits)
        print(f"✓ {len(posts)}개의 Reddit 게시물 수집 완료")
        
        return True
    except Exception as e:
        print(f"✗ Reddit 수집 실패: {e}")
        print("Reddit API 키를 설정했는지 확인하세요.")
        return False

def collect_instagram_data(meme_name):
    """Instagram에서 밈 데이터 수집"""
    print(f"\n=== Instagram에서 '{meme_name}' 데이터 수집 시작 ===")
    try:
        collector = InstagramCollector()
        posts = collector.collect_meme_data(meme_name)
        print(f"✓ {len(posts)}개의 Instagram 게시물 수집 완료")
        
        return True
    except Exception as e:
        print(f"✗ Instagram 수집 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='밈 수명 주기 분석 데이터 수집')
    parser.add_argument('--meme', type=str, help='수집할 밈 이름')
    parser.add_argument('--platform', type=str, choices=['all', 'twitter', 'reddit', 'instagram'],
                       default='all', help='수집할 플랫폼')
    parser.add_argument('--test', action='store_true', help='테스트 모드 (첫 번째 밈만 수집)')
    
    args = parser.parse_args()
    
    # 디렉토리 생성
    create_directories()
    
    # 수집할 밈 목록 결정
    if args.meme:
        memes_to_collect = [args.meme]
    elif args.test:
        memes_to_collect = [TARGET_MEMES[0]]  # 첫 번째 밈만
    else:
        memes_to_collect = TARGET_MEMES
    
    print("=== 밈 수명 주기 분석 데이터 수집 ===")
    print(f"수집 대상 밈: {', '.join(memes_to_collect)}")
    print(f"수집 플랫폼: {args.platform}")
    print(f"시작 시간: {datetime.now()}")
    
    # 각 밈에 대해 데이터 수집
    for meme in memes_to_collect:
        print(f"\n{'='*50}")
        print(f"밈 '{meme}' 수집 시작")
        print(f"{'='*50}")
        
        if args.platform in ['all', 'twitter']:
            collect_twitter_data(meme)
            time.sleep(5)  # Rate limit 방지
        
        if args.platform in ['all', 'reddit']:
            collect_reddit_data(meme)
            time.sleep(2)
        
        if args.platform in ['all', 'instagram']:
            collect_instagram_data(meme)
            time.sleep(5)
    
    print(f"\n=== 데이터 수집 완료 ===")
    print(f"종료 시간: {datetime.now()}")

if __name__ == "__main__":
    main()