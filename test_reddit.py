import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.collectors.reddit_collector import RedditCollector

def test_reddit_connection():
    """Reddit API 연결 테스트"""
    print("=== Reddit API 연결 테스트 ===")
    
    try:
        # 수집기 생성
        collector = RedditCollector()
        print("✓ Reddit 클라이언트 생성 성공!")
        
        # 간단한 검색 테스트
        print("\n인기 밈 게시물 검색 중...")
        posts = collector.search_posts('meme', subreddit='memes', limit=5)
        
        if posts:
            print(f"✓ 검색 성공! {len(posts)}개 게시물 발견")
            print("\n첫 번째 게시물:")
            print(f"- 제목: {posts[0]['title']}")
            print(f"- 점수: {posts[0]['score']}")
            print(f"- 서브레딧: {posts[0]['subreddit']}")
        else:
            print("검색 결과 없음")
            
    except Exception as e:
        print(f"✗ 오류 발생: {e}")
        print("API 키를 확인하세요.")

if __name__ == "__main__":
    test_reddit_connection()
