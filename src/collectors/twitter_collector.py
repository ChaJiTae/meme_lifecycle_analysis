import tweepy
import pandas as pd
from datetime import datetime
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.api_keys import (
    TWITTER_API_KEY, 
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_BEARER_TOKEN
)
from config.config import RAW_DATA_DIR, MAX_TWEETS_PER_MEME

class TwitterCollector:
    def __init__(self):
        """Twitter API 클라이언트 초기화"""
        # Bearer Token을 사용한 인증 (v2 API)
        self.client = tweepy.Client(
            bearer_token=TWITTER_BEARER_TOKEN,
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )
        
    def search_tweets(self, query, max_results=100, start_time=None, end_time=None):
        """
        Twitter에서 특정 쿼리로 트윗 검색
        
        Args:
            query: 검색 쿼리 (밈 이름 또는 해시태그)
            max_results: 최대 결과 수
            start_time: 검색 시작 시간
            end_time: 검색 종료 시간
            
        Returns:
            검색된 트윗 리스트
        """
        tweets_data = []
        
        try:
            # 검색 실행
            tweets = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=query,
                max_results=100,  # 페이지당 최대 100개
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'lang'],
                user_fields=['username', 'public_metrics'],
                expansions=['author_id']
            ).flatten(limit=max_results)
            
            for tweet in tweets:
                tweet_info = {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'author_id': tweet.author_id,
                    'retweet_count': tweet.public_metrics['retweet_count'],
                    'reply_count': tweet.public_metrics['reply_count'],
                    'like_count': tweet.public_metrics['like_count'],
                    'quote_count': tweet.public_metrics['quote_count'],
                    'lang': tweet.lang
                }
                tweets_data.append(tweet_info)
            
            print(f"수집된 트윗 수: {len(tweets_data)}")
            return tweets_data
            
        except Exception as e:
            print(f"트윗 검색 중 오류 발생: {e}")
            return tweets_data
    
    def save_tweets(self, tweets, meme_name):
        """
        수집된 트윗을 CSV 파일로 저장
        
        Args:
            tweets: 트윗 데이터 리스트
            meme_name: 밈 이름
        """
        if not tweets:
            print("저장할 트윗이 없습니다.")
            return
        
        # 데이터프레임 생성
        df = pd.DataFrame(tweets)
        
        # 저장 경로 설정
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"twitter_{meme_name}_{timestamp}.csv"
        filepath = os.path.join(RAW_DATA_DIR, filename)
        
        # 디렉토리가 없으면 생성
        os.makedirs(RAW_DATA_DIR, exist_ok=True)
        
        # CSV 저장
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"트윗 저장 완료: {filepath}")
        
    def collect_meme_data(self, meme_name, hashtags=None):
        """
        특정 밈에 대한 데이터 수집
        
        Args:
            meme_name: 밈 이름
            hashtags: 관련 해시태그 리스트
        """
        # 검색 쿼리 생성
        query_parts = [f'"{meme_name}"']
        if hashtags:
            query_parts.extend([f"#{tag}" for tag in hashtags])
        
        query = " OR ".join(query_parts) + " -is:retweet"
        
        print(f"검색 쿼리: {query}")
        
        # 트윗 검색
        tweets = self.search_tweets(query, max_results=MAX_TWEETS_PER_MEME)
        
        # 결과 저장
        self.save_tweets(tweets, meme_name.replace(" ", "_").lower())
        
        return tweets

# 테스트 코드
if __name__ == "__main__":
    # 수집기 인스턴스 생성
    collector = TwitterCollector()
    
    # 테스트: "chill guy" 밈 검색 (최대 10개)
    test_tweets = collector.search_tweets('"chill guy" meme', max_results=10)
    
    if test_tweets:
        print("\n=== 첫 번째 트윗 예시 ===")
        print(test_tweets[0])