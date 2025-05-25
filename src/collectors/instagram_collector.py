import instaloader
import pandas as pd
from datetime import datetime
import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.api_keys import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD
from config.config import RAW_DATA_DIR

class InstagramCollector:
    def __init__(self):
        """Instaloader 인스턴스 초기화"""
        self.loader = instaloader.Instaloader(
            download_pictures=False,  # 이미지 다운로드 비활성화
            download_videos=False,    # 비디오 다운로드 비활성화
            download_video_thumbnails=False,
            compress_json=False,
            save_metadata=True,
            post_metadata_txt_pattern=""  # 텍스트 파일 생성 비활성화
        )
        self.logged_in = False
        
    def login(self):
        """Instagram 로그인 (선택사항)"""
        try:
            if INSTAGRAM_USERNAME != "your_instagram_username":
                self.loader.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
                self.logged_in = True
                print("Instagram 로그인 성공!")
            else:
                print("로그인 정보가 설정되지 않았습니다. 공개 데이터만 수집합니다.")
        except Exception as e:
            print(f"로그인 실패: {e}")
            print("공개 데이터만 수집합니다.")
    
    def search_hashtag(self, hashtag, max_posts=100):
        """
        해시태그로 게시물 검색
        
        Args:
            hashtag: 검색할 해시태그 (# 제외)
            max_posts: 최대 수집할 게시물 수
            
        Returns:
            게시물 정보 리스트
        """
        posts_data = []
        
        try:
            # 해시태그 객체 가져오기
            hashtag_obj = instaloader.Hashtag.from_name(self.loader.context, hashtag)
            
            # 게시물 수집
            count = 0
            for post in hashtag_obj.get_posts():
                if count >= max_posts:
                    break
                
                post_info = {
                    'shortcode': post.shortcode,
                    'caption': post.caption if post.caption else "",
                    'hashtags': list(post.caption_hashtags) if post.caption_hashtags else [],
                    'created_utc': post.date_utc,
                    'likes': post.likes,
                    'comments': post.comments,
                    'is_video': post.is_video,
                    'url': f"https://www.instagram.com/p/{post.shortcode}/",
                    'owner_username': post.owner_username,
                    'owner_id': post.owner_id
                }
                posts_data.append(post_info)
                count += 1
                
                # Rate limit 방지
                if count % 10 == 0:
                    time.sleep(2)
            
            print(f"수집된 Instagram 게시물 수: {len(posts_data)}")
            return posts_data
            
        except Exception as e:
            print(f"Instagram 검색 중 오류 발생: {e}")
            return posts_data
    
    def save_posts(self, posts, hashtag):
        """수집된 게시물을 CSV 파일로 저장"""
        if not posts:
            print("저장할 게시물이 없습니다.")
            return
        
        df = pd.DataFrame(posts)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"instagram_{hashtag}_{timestamp}.csv"
        filepath = os.path.join(RAW_DATA_DIR, filename)
        
        os.makedirs(RAW_DATA_DIR, exist_ok=True)
        
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"Instagram 게시물 저장 완료: {filepath}")
    
    def collect_meme_data(self, meme_name, hashtags=None):
        """특정 밈에 대한 데이터 수집"""
        all_posts = []
        
        # 기본 해시태그 생성
        if not hashtags:
            # 공백과 특수문자 제거
            base_tag = meme_name.replace(" ", "").replace("-", "").lower()
            hashtags = [base_tag, f"{base_tag}meme", f"{base_tag}memes"]
        
        for hashtag in hashtags:
            print(f"\n'#{hashtag}' 해시태그 검색 중...")
            posts = self.search_hashtag(hashtag, max_posts=100)
            all_posts.extend(posts)
            
            # Rate limit 방지
            time.sleep(5)
        
        # 중복 제거
        unique_posts = []
        seen_shortcodes = set()
        for post in all_posts:
            if post['shortcode'] not in seen_shortcodes:
                unique_posts.append(post)
                seen_shortcodes.add(post['shortcode'])
        
        # 결과 저장
        self.save_posts(unique_posts, meme_name.replace(" ", "_").lower())
        
        return unique_posts

# 테스트 코드
if __name__ == "__main__":
    try:
        # 수집기 인스턴스 생성
        collector = InstagramCollector()
        
        print("Instagram 수집기 테스트")
        print("주의: Instagram은 로그인 없이도 공개 해시태그를 검색할 수 있습니다.")
        print("하지만 rate limit이 엄격하므로 신중하게 사용하세요.")
        
        # 간단한 테스트 (실제로 실행하지 않음)
        print("\n✓ Instagram 수집기 설정 완료!")
        print("✓ 실제 수집은 main.py에서 진행합니다.")
        
    except Exception as e:
        print(f"오류 발생: {e}")