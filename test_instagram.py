import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.collectors.instagram_collector import InstagramCollector

def test_instagram_no_login():
    """Instagram 로그인 없이 테스트"""
    print("=== Instagram 테스트 (로그인 없음) ===")
    
    try:
        # 수집기 생성
        collector = InstagramCollector()
        print("✓ Instagram 수집기 생성 성공!")
        
        # 공개 해시태그 테스트 (매우 적은 수만)
        print("\n공개 해시태그 테스트...")
        print("주의: Rate limit 때문에 1-2개만 수집합니다.")
        
        posts = collector.search_hashtag('meme', max_posts=2)
        
        if posts:
            print(f"✓ 성공! {len(posts)}개 게시물 발견")
            print(f"- 첫 게시물 URL: {posts[0]['url']}")
        else:
            print("게시물을 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"✗ 오류 발생: {e}")
        print("Instagram은 rate limit이 매우 엄격합니다.")

if __name__ == "__main__":
    test_instagram_no_login()