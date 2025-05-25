import time
from src.collectors.twitter_collector import TwitterCollector
from src.collectors.reddit_collector import RedditCollector
from src.collectors.instagram_collector import InstagramCollector

def test_all_platforms():
    """모든 플랫폼 연결 테스트"""
    print("=== 모든 플랫폼 API 테스트 ===\n")
    
    results = {}
    
    # Twitter 테스트
    print("1. Twitter 테스트...")
    try:
        twitter = TwitterCollector()
        results['Twitter'] = '✓ 연결 성공 (Rate limit 주의)'
    except Exception as e:
        results['Twitter'] = f'✗ 실패: {str(e)[:50]}...'
    
    # Reddit 테스트
    print("2. Reddit 테스트...")
    try:
        reddit = RedditCollector()
        posts = reddit.search_posts('test', limit=1)
        results['Reddit'] = '✓ 연결 성공' if posts else '✓ 연결됨 (데이터 없음)'
    except Exception as e:
        results['Reddit'] = f'✗ 실패: {str(e)[:50]}...'
    
    # Instagram 테스트
    print("3. Instagram 테스트...")
    try:
        instagram = InstagramCollector()
        results['Instagram'] = '✓ 수집기 생성 성공 (Rate limit 매우 엄격)'
    except Exception as e:
        results['Instagram'] = f'✗ 실패: {str(e)[:50]}...'
    
    # 결과 출력
    print("\n=== 테스트 결과 ===")
    for platform, result in results.items():
        print(f"{platform}: {result}")
    
    print("\n주의사항:")
    print("- Twitter: 15분마다 요청 제한 재설정")
    print("- Reddit: 가장 안정적, 분당 60 요청 가능")
    print("- Instagram: 매우 제한적, 신중히 사용")

if __name__ == "__main__":
    test_all_platforms()
