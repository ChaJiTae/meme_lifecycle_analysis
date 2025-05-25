import praw
import pandas as pd
from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.api_keys import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
from config.config import RAW_DATA_DIR, MAX_REDDIT_POSTS_PER_MEME

class RedditCollector:
    def __init__(self):
        """Reddit API 클라이언트 초기화"""
        self.reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        
    def search_posts(self, query, subreddit='all', sort='relevance', time_filter='all', limit=100):
        """
        Reddit에서 게시물 검색
        
        Args:
            query: 검색 쿼리
            subreddit: 검색할 서브레딧 ('all'이면 전체)
            sort: 정렬 방식 ('relevance', 'hot', 'top', 'new')
            time_filter: 시간 필터 ('all', 'day', 'week', 'month', 'year')
            limit: 최대 결과 수
            
        Returns:
            검색된 게시물 리스트
        """
        posts_data = []
        
        try:
            # 서브레딧 선택
            if subreddit == 'all':
                subreddit_obj = self.reddit.subreddit('all')
            else:
                subreddit_obj = self.reddit.subreddit(subreddit)
            
            # 검색 실행
            posts = subreddit_obj.search(query, sort=sort, time_filter=time_filter, limit=limit)
            
            for post in posts:
                post_info = {
                    'id': post.id,
                    'title': post.title,
                    'selftext': post.selftext,
                    'author': str(post.author) if post.author else '[deleted]',
                    'created_utc': datetime.fromtimestamp(post.created_utc),
                    'score': post.score,
                    'upvote_ratio': post.upvote_ratio,
                    'num_comments': post.num_comments,
                    'subreddit': str(post.subreddit),
                    'url': post.url,
                    'permalink': f"https://reddit.com{post.permalink}"
                }
                posts_data.append(post_info)
            
            print(f"수집된 Reddit 게시물 수: {len(posts_data)}")
            return posts_data
            
        except Exception as e:
            print(f"Reddit 검색 중 오류 발생: {e}")
            return posts_data
    
    def search_comments(self, post_id, limit=100):
        """특정 게시물의 댓글 수집"""
        comments_data = []
        
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)
            
            for comment in submission.comments.list()[:limit]:
                comment_info = {
                    'id': comment.id,
                    'body': comment.body,
                    'author': str(comment.author) if comment.author else '[deleted]',
                    'created_utc': datetime.fromtimestamp(comment.created_utc),
                    'score': comment.score,
                    'parent_id': comment.parent_id,
                    'post_id': post_id
                }
                comments_data.append(comment_info)
                
            return comments_data
            
        except Exception as e:
            print(f"댓글 수집 중 오류 발생: {e}")
            return comments_data
    
    def save_posts(self, posts, meme_name):
        """수집된 게시물을 CSV 파일로 저장"""
        if not posts:
            print("저장할 게시물이 없습니다.")
            return
        
        df = pd.DataFrame(posts)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reddit_{meme_name}_{timestamp}.csv"
        filepath = os.path.join(RAW_DATA_DIR, filename)
        
        os.makedirs(RAW_DATA_DIR, exist_ok=True)
        
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"Reddit 게시물 저장 완료: {filepath}")
    
    def collect_meme_data(self, meme_name, subreddits=None):
        """특정 밈에 대한 데이터 수집"""
        all_posts = []
        
        # 기본 서브레딧 목록
        if not subreddits:
            subreddits = ['memes', 'dankmemes', 'all']
        
        for subreddit in subreddits:
            print(f"\n{subreddit} 서브레딧에서 '{meme_name}' 검색 중...")
            posts = self.search_posts(
                query=meme_name,
                subreddit=subreddit,
                sort='relevance',
                time_filter='all',
                limit=MAX_REDDIT_POSTS_PER_MEME // len(subreddits)
            )
            all_posts.extend(posts)
        
        # 결과 저장
        self.save_posts(all_posts, meme_name.replace(" ", "_").lower())
        
        return all_posts

# 테스트 코드
if __name__ == "__main__":
    print("Reddit 수집기는 API 키 설정 후 테스트하세요.")
    print("https://www.reddit.com/prefs/apps 에서 앱을 생성하여 키를 받으세요.")