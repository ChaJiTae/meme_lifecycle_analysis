import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.config import PROCESSED_DATA_DIR, FIGURES_DIR

class MemeVisualizer:
    def __init__(self):
        """시각화 클래스 초기화"""
        self.figures_dir = FIGURES_DIR
        os.makedirs(self.figures_dir, exist_ok=True)
        
        # 스타일 설정
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
        
    def plot_lifecycle_curve(self, df, meme_name, platform='reddit'):
        """밈 생명주기 곡선 시각화"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # 일별 게시물 수
        daily_posts = df.groupby('date').size()
        
        # 7일 이동평균
        daily_posts_ma = daily_posts.rolling(window=7, min_periods=1).mean()
        
        # 상단: 일별 게시물 수
        ax1.plot(daily_posts.index, daily_posts.values, alpha=0.3, label='Daily Post')
        ax1.plot(daily_posts_ma.index, daily_posts_ma.values, linewidth=2, label='7-day Moving Average')
        ax1.set_title(f'{meme_name} Meme Life Cycle - {platform.upper()}', fontsize=16, fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Number of posts')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 하단: 누적 게시물 수
        cumulative_posts = daily_posts.cumsum()
        ax2.plot(cumulative_posts.index, cumulative_posts.values, linewidth=2, color='green')
        ax2.fill_between(cumulative_posts.index, cumulative_posts.values, alpha=0.3, color='green')
        ax2.set_title('Accumulated number of posts', fontsize=14)
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Accumulated number of posts')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 저장
        filename = f'{platform}_{meme_name}_lifecycle_curve.png'
        filepath = os.path.join(self.figures_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"생명주기 곡선 저장: {filepath}")
        
    def plot_engagement_analysis(self, df, meme_name, platform='reddit'):
        """참여도 분석 시각화"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'{meme_name} Participation Analysis - {platform.upper()}', fontsize=16, fontweight='bold')
        
        # 1. Score 분포
        ax1 = axes[0, 0]
        df['score'].hist(bins=50, ax=ax1, alpha=0.7, color='blue', edgecolor='black')
        ax1.set_title('Score Distribution')
        ax1.set_xlabel('Score')
        ax1.set_ylabel('Frequency')
        ax1.set_yscale('log')
        
        # 2. 댓글 수 분포
        ax2 = axes[0, 1]
        df['num_comments'].hist(bins=50, ax=ax2, alpha=0.7, color='green', edgecolor='black')
        ax2.set_title('Distribution of comments')
        ax2.set_xlabel('Number of comments')
        ax2.set_ylabel('Frequency')
        ax2.set_yscale('log')
        
        # 3. 시간대별 평균 Score
        ax3 = axes[1, 0]
        hourly_score = df.groupby('hour')['score'].mean()
        hourly_score.plot(kind='bar', ax=ax3, color='orange')
        ax3.set_title('Hourly Average Score')
        ax3.set_xlabel('Hours (24 hours)')
        ax3.set_ylabel('Average Score')
        ax3.set_xticklabels(ax3.get_xticklabels(), rotation=0)
        
        # 4. 요일별 게시물 수
        ax4 = axes[1, 1]
        days_english = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        day_counts = df['day_of_week'].value_counts().sort_index()
        ax4.bar(range(7), day_counts.values, color='purple')
        ax4.set_xticks(range(7))
        ax4.set_xticklabels(days_english)
        ax4.set_title('Posts by Day of Week')
        ax4.set_xlabel('Day of Week')
        ax4.set_ylabel('Number of Posts')
        
        plt.tight_layout()
        
        # 저장
        filename = f'{platform}_{meme_name}_engagement_analysis.png'
        filepath = os.path.join(self.figures_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Save Participation Analysis: {filepath}")
        
    def plot_subreddit_distribution(self, df, meme_name):
        """서브레딧별 분포 시각화"""
        plt.figure(figsize=(10, 6))
        
        # 상위 10개 서브레딧
        top_subreddits = df['subreddit'].value_counts().head(10)
        
        # 막대 그래프
        bars = plt.bar(range(len(top_subreddits)), top_subreddits.values)
        plt.xticks(range(len(top_subreddits)), top_subreddits.index, rotation=45, ha='right')
        
        # 색상 그라데이션
        colors = plt.cm.viridis(np.linspace(0, 1, len(bars)))
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        
        plt.title(f'{meme_name} - Top 10 Subreddit Distribution', fontsize=14, fontweight='bold')
        plt.xlabel('Subreddit')
        plt.ylabel('Number of Posts')
        plt.grid(True, alpha=0.3, axis='y')
        
        # 저장
        filename = f'reddit_{meme_name}_subreddit_distribution.png'
        filepath = os.path.join(self.figures_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"서브레딧 분포 저장: {filepath}")
        
    def plot_lifecycle_phases(self, df, meme_name, platform='reddit'):
        """Meme Life Cycle Step Analysis"""
        # 월별 집계
        df['year_month'] = df['created_utc'].dt.to_period('M')
        monthly_stats = df.groupby('year_month').agg({
            'id': 'count',
            'score': 'mean',
            'num_comments': 'mean'
        }).rename(columns={'id': 'post_count'})
        
        # 최근 2년 데이터만 사용
        recent_data = monthly_stats[monthly_stats.index >= '2023-01']
        
        if len(recent_data) > 0:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # 정규화
            normalized_posts = recent_data['post_count'] / recent_data['post_count'].max()
            normalized_score = recent_data['score'] / recent_data['score'].max()
            
            # 플롯
            x = range(len(recent_data))
            ax.plot(x, normalized_posts, 'o-', label='Post Count (Normalized)', linewidth=2, markersize=8)
            ax.plot(x, normalized_score, 's-', label='Average Score (Normalized)', linewidth=2, markersize=8)
            
            # 배경색으로 단계 표시
            if len(x) > 0:
                # 초기 단계
                ax.axvspan(0, len(x)//3, alpha=0.1, color='green', label='Growth Phase')
                # 정점 단계
                ax.axvspan(len(x)//3, 2*len(x)//3, alpha=0.1, color='yellow', label='Maturity Phase')
                # 쇠퇴 단계
                ax.axvspan(2*len(x)//3, len(x), alpha=0.1, color='red', label='Decline Phase')
            
            ax.set_xticks(x[::3])
            ax.set_xticklabels([str(idx) for idx in recent_data.index[::3]], rotation=45)
            ax.set_title(f'{meme_name} Meme Life Cycle Stage (Last 2 Years)', fontsize=14, fontweight='bold')
            ax.set_xlabel('Year-Month')
            ax.set_ylabel('normalized value')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # 저장
            filename = f'{platform}_{meme_name}_lifecycle_phases.png'
            filepath = os.path.join(self.figures_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"Save the life cycle stage analysis : {filepath}")
        else:
            print("최근 데이터가 충분하지 않아 생명주기 단계 분석을 건너뜁니다.")
    
    def create_summary_dashboard(self, df, meme_name, platform='reddit'):
        """종합 대시보드 생성"""
        # 기본 통계
        total_posts = len(df)
        total_authors = df['author'].nunique()
        avg_score = df['score'].mean()
        avg_comments = df['num_comments'].mean()
        
        # 시간 범위
        date_range = f"{df['created_utc'].min().strftime('%Y-%m-%d')} ~ {df['created_utc'].max().strftime('%Y-%m-%d')}"
        
        # 대시보드 생성
        fig = plt.figure(figsize=(16, 12))
        
        # 제목
        fig.suptitle(f'{meme_name} Meme Analysis Dashboard - {platform.upper()}', fontsize=20, fontweight='bold')
        
        # 통계 요약 (텍스트)
        ax_text = plt.subplot2grid((4, 3), (0, 0), colspan=3)
        ax_text.axis('off')
        summary_text = f"""
        Total number of posts : {total_posts:,}post
        Total number of authors : {total_authors:,}author
        Average Score: {avg_score:.1f}
        Average number of comments : {avg_comments:.1f}
        Data Period : {date_range}
        """
        ax_text.text(0.5, 0.5, summary_text, ha='center', va='center', fontsize=14,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.5))
        
        # 그래프들
        # 1. 월별 추이
        ax1 = plt.subplot2grid((4, 3), (1, 0), colspan=2)
        monthly_posts = df.groupby(df['created_utc'].dt.to_period('M')).size()
        monthly_posts.plot(kind='line', ax=ax1, color='blue', linewidth=2)
        ax1.set_title('Monthly Post Trends')
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Number of posts')
        ax1.grid(True, alpha=0.3)
        
        # 2. Score vs Comments 산점도
        ax2 = plt.subplot2grid((4, 3), (1, 2))
        ax2.scatter(df['score'], df['num_comments'], alpha=0.5, s=20)
        ax2.set_xlabel('Score')
        ax2.set_ylabel('Number of comments')
        ax2.set_title('Score vs Number of comments')
        ax2.set_xscale('log')
        ax2.set_yscale('log')
        ax2.grid(True, alpha=0.3)
        
        # 3. 시간대별 분포
        ax3 = plt.subplot2grid((4, 3), (2, 0), colspan=3)
        df.groupby('hour').size().plot(kind='bar', ax=ax3, color='green')
        ax3.set_title('Distribution of posts by time')
        ax3.set_xlabel('Hours (24 hours)')
        ax3.set_ylabel('Number of posts')
        
        # 4. 상위 서브레딧
        ax4 = plt.subplot2grid((4, 3), (3, 0), colspan=3)
        top_subs = df['subreddit'].value_counts().head(15)
        top_subs.plot(kind='barh', ax=ax4, color='purple')
        ax4.set_title('Top 15 Subreddit')
        ax4.set_xlabel('Number of posts')
        
        plt.tight_layout()
        
        # 저장
        filename = f'{platform}_{meme_name}_dashboard.png'
        filepath = os.path.join(self.figures_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"대시보드 저장: {filepath}")

# 실행 코드
if __name__ == "__main__":
    import glob
    
    # 전처리된 데이터 찾기
    processed_files = glob.glob(os.path.join(PROCESSED_DATA_DIR, 'processed_reddit_*.csv'))
    
    if processed_files:
        # 가장 최근 파일 선택
        latest_file = max(processed_files, key=os.path.getctime)
        
        # 데이터 로드
        df = pd.read_csv(latest_file)
        df['created_utc'] = pd.to_datetime(df['created_utc'])
        df['date'] = pd.to_datetime(df['date'])
        
        # 밈 이름 추출
        meme_name = 'chill_guy'
        
        # 시각화 생성
        visualizer = MemeVisualizer()
        
        print(f"\n=== {meme_name} 밈 시각화 생성 ===")
        visualizer.plot_lifecycle_curve(df, meme_name)
        visualizer.plot_engagement_analysis(df, meme_name)
        visualizer.plot_subreddit_distribution(df, meme_name)
        visualizer.plot_lifecycle_phases(df, meme_name)
        visualizer.create_summary_dashboard(df, meme_name)
        
        print(f"\n모든 시각화 완료! 결과는 {FIGURES_DIR}에 저장되었습니다.")
    else:
        print("전처리된 데이터를 찾을 수 없습니다.")