import pandas as pd
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings
import os
import sys
import glob
import argparse

warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.config import PROCESSED_DATA_DIR, RESULTS_DIR

class LifecycleAnalyzer:
    def __init__(self):
        """밈 수명 주기 분석기 초기화"""
        self.results_dir = RESULTS_DIR
        
    def identify_lifecycle_phases(self, df):
        """밈의 생명주기 단계 식별"""
        print("\n=== Lifecycle Phase Analysis ===")
        
        # 일별 집계
        daily_metrics = df.groupby('date').agg({
            'id': 'count',
            'score': ['mean', 'sum'],
            'num_comments': ['mean', 'sum'],
            'engagement_score': 'sum'
        }).reset_index()
        
        # 컬럼명 정리
        daily_metrics.columns = ['date', 'post_count', 'avg_score', 'total_score', 
                                'avg_comments', 'total_comments', 'total_engagement']
        
        # 누적 지표 계산
        daily_metrics['cumulative_posts'] = daily_metrics['post_count'].cumsum()
        daily_metrics['days_since_start'] = (daily_metrics['date'] - daily_metrics['date'].min()).dt.days
        
        # 이동 평균 (7일)
        daily_metrics['ma7_posts'] = daily_metrics['post_count'].rolling(window=7, min_periods=1).mean()
        daily_metrics['ma7_engagement'] = daily_metrics['total_engagement'].rolling(window=7, min_periods=1).mean()
        
        # 성장률 계산
        daily_metrics['growth_rate'] = daily_metrics['ma7_posts'].pct_change()
        
        # 단계 식별
        phases = self._identify_phases(daily_metrics)
        
        return daily_metrics, phases
    
    def _identify_phases(self, daily_metrics):
        """성장률 기반 단계 식별"""
        # 최근 2년 데이터만 사용
        recent_data = daily_metrics[daily_metrics['date'] >= '2023-01-01'].copy()
        
        if len(recent_data) < 30:
            print("Not enough recent data for phase identification")
            return None
        
        # 정규화된 지표
        recent_data['normalized_posts'] = recent_data['ma7_posts'] / recent_data['ma7_posts'].max()
        
        # 단계 정의 (간단한 규칙 기반)
        phases = []
        
        # 피크 찾기
        peak_idx = recent_data['normalized_posts'].idxmax()
        peak_date = recent_data.loc[peak_idx, 'date']
        
        # 피크 전후로 단계 구분
        growth_phase = recent_data[recent_data['date'] < peak_date]
        decline_phase = recent_data[recent_data['date'] >= peak_date]
        
        if len(growth_phase) > 0:
            phases.append({
                'phase': 'Growth',
                'start_date': growth_phase['date'].min(),
                'end_date': growth_phase['date'].max(),
                'duration_days': len(growth_phase),
                'avg_daily_posts': growth_phase['post_count'].mean(),
                'total_posts': growth_phase['post_count'].sum()
            })
        
        if len(decline_phase) > 0:
            phases.append({
                'phase': 'Decline',
                'start_date': decline_phase['date'].min(),
                'end_date': decline_phase['date'].max(),
                'duration_days': len(decline_phase),
                'avg_daily_posts': decline_phase['post_count'].mean(),
                'total_posts': decline_phase['post_count'].sum()
            })
        
        return phases
    
    def fit_lifecycle_curve(self, daily_metrics):
        """수명 주기 곡선 피팅"""
        print("\n=== Lifecycle Curve Fitting ===")
        
        # 최근 데이터만 사용
        recent_data = daily_metrics[daily_metrics['date'] >= '2024-01-01'].copy()
        
        if len(recent_data) < 10:
            print("Not enough data for curve fitting")
            return None
        
        # x: 시작일로부터의 일수
        x = (recent_data['date'] - recent_data['date'].min()).dt.days.values
        y = recent_data['post_count'].values
        
        # 가우시안 함수로 피팅 시도
        try:
            def gaussian(x, a, b, c):
                return a * np.exp(-(x - b)**2 / (2 * c**2))
            
            # 초기 추정값
            a_init = y.max()
            b_init = x[np.argmax(y)]
            c_init = len(x) / 4
            
            popt, pcov = curve_fit(gaussian, x, y, p0=[a_init, b_init, c_init], maxfev=5000)
            
            # 피팅 결과
            y_fit = gaussian(x, *popt)
            
            # R-squared 계산
            residuals = y - y_fit
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((y - np.mean(y))**2)
            r_squared = 1 - (ss_res / ss_tot)
            
            print(f"Gaussian fit R-squared: {r_squared:.3f}")
            print(f"Peak day: {int(popt[1])}")
            print(f"Spread (days): {int(popt[2])}")
            
            return {
                'model': 'gaussian',
                'parameters': popt,
                'r_squared': r_squared,
                'peak_day': int(popt[1]),
                'spread_days': int(popt[2])
            }
            
        except Exception as e:
            print(f"Curve fitting failed: {e}")
            return None
    
    def calculate_lifecycle_metrics(self, df, daily_metrics):
        """수명 주기 관련 메트릭 계산"""
        print("\n=== Lifecycle Metrics ===")
        
        metrics = {}
        
        # 1. 기본 통계
        metrics['total_posts'] = len(df)
        metrics['unique_authors'] = df['author'].nunique()
        metrics['date_range'] = f"{df['date'].min()} to {df['date'].max()}"
        metrics['duration_days'] = (df['date'].max() - df['date'].min()).days
        
        # 2. 참여도 지표
        metrics['avg_score'] = df['score'].mean()
        metrics['avg_comments'] = df['num_comments'].mean()
        metrics['total_engagement'] = df['engagement_score'].sum()
        
        # 3. 확산 지표
        metrics['posts_per_author'] = metrics['total_posts'] / metrics['unique_authors']
        metrics['subreddit_count'] = df['subreddit'].nunique()
        
        # 4. 시간적 패턴
        # 피크 시점 찾기
        peak_date_idx = daily_metrics['post_count'].idxmax()
        peak_date = daily_metrics.loc[peak_date_idx, 'date']
        metrics['peak_date'] = peak_date
        metrics['days_to_peak'] = (peak_date - df['date'].min()).days
        
        # 5. 생명주기 단계별 분포
        if metrics['days_to_peak'] > 0:
            growth_phase = df[df['date'] < peak_date]
            decline_phase = df[df['date'] >= peak_date]
            
            metrics['growth_phase_posts'] = len(growth_phase)
            metrics['decline_phase_posts'] = len(decline_phase)
            metrics['growth_decline_ratio'] = metrics['growth_phase_posts'] / max(metrics['decline_phase_posts'], 1)
        
        # 6. 지속성 지표
        # 활동일 비율
        active_days = daily_metrics[daily_metrics['post_count'] > 0]
        metrics['active_days_ratio'] = len(active_days) / len(daily_metrics)
        
        # 7. 바이럴리티 지표
        # 상위 10% 게시물이 차지하는 engagement 비율
        top_10_pct = int(len(df) * 0.1)
        top_posts_engagement = df.nlargest(top_10_pct, 'engagement_score')['engagement_score'].sum()
        metrics['viral_concentration'] = top_posts_engagement / df['engagement_score'].sum()
        
        return metrics
    
    def generate_report(self, meme_name, df, daily_metrics, phases, curve_fit, metrics):
        """분석 보고서 생성"""
        reports_dir = os.path.join(self.results_dir, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        report_path = os.path.join(reports_dir, f'{meme_name}_lifecycle_report.txt')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"MEME LIFECYCLE ANALYSIS REPORT\n")
            f.write(f"{'='*50}\n")
            f.write(f"Meme: {meme_name.replace('_', ' ').title()}\n")
            f.write(f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"1. OVERVIEW\n")
            f.write(f"{'-'*30}\n")
            f.write(f"Total Posts: {metrics['total_posts']:,}\n")
            f.write(f"Unique Authors: {metrics['unique_authors']:,}\n")
            f.write(f"Date Range: {metrics['date_range']}\n")
            f.write(f"Duration: {metrics['duration_days']} days\n")
            f.write(f"Peak Date: {metrics['peak_date']}\n")
            f.write(f"Days to Peak: {metrics['days_to_peak']}\n\n")
            
            f.write(f"2. ENGAGEMENT METRICS\n")
            f.write(f"{'-'*30}\n")
            f.write(f"Average Score: {metrics['avg_score']:.1f}\n")
            f.write(f"Average Comments: {metrics['avg_comments']:.1f}\n")
            f.write(f"Total Engagement: {metrics['total_engagement']:,}\n")
            f.write(f"Viral Concentration: {metrics['viral_concentration']:.2%}\n\n")
            
            f.write(f"3. SPREAD METRICS\n")
            f.write(f"{'-'*30}\n")
            f.write(f"Posts per Author: {metrics['posts_per_author']:.2f}\n")
            f.write(f"Subreddit Count: {metrics['subreddit_count']}\n")
            f.write(f"Active Days Ratio: {metrics['active_days_ratio']:.2%}\n\n")
            
            if phases:
                f.write(f"4. LIFECYCLE PHASES\n")
                f.write(f"{'-'*30}\n")
                for phase in phases:
                    f.write(f"\n{phase['phase']} Phase:\n")
                    f.write(f"  - Duration: {phase['duration_days']} days\n")
                    f.write(f"  - Period: {phase['start_date']} to {phase['end_date']}\n")
                    f.write(f"  - Total Posts: {phase['total_posts']}\n")
                    f.write(f"  - Avg Daily Posts: {phase['avg_daily_posts']:.1f}\n")
            
            if curve_fit:
                f.write(f"\n5. CURVE FITTING RESULTS\n")
                f.write(f"{'-'*30}\n")
                f.write(f"Model: {curve_fit['model']}\n")
                f.write(f"R-squared: {curve_fit['r_squared']:.3f}\n")
                f.write(f"Peak Day: {curve_fit['peak_day']}\n")
                f.write(f"Spread: {curve_fit['spread_days']} days\n")
            
            f.write(f"\n6. LIFECYCLE CLASSIFICATION\n")
            f.write(f"{'-'*30}\n")
            
            # 수명 주기 분류
            if metrics['duration_days'] < 30:
                lifecycle_type = "Flash Meme"
            elif metrics['duration_days'] < 90:
                lifecycle_type = "Short-lived Meme"
            elif metrics['duration_days'] < 365:
                lifecycle_type = "Standard Meme"
            else:
                lifecycle_type = "Long-lived Meme"
            
            f.write(f"Lifecycle Type: {lifecycle_type}\n")
            
            # 확산 패턴 분류
            if metrics.get('growth_decline_ratio', 0) > 2:
                spread_pattern = "Slow Burn"
            elif metrics.get('growth_decline_ratio', 0) > 0.5:
                spread_pattern = "Balanced"
            else:
                spread_pattern = "Viral Spike"
            
            f.write(f"Spread Pattern: {spread_pattern}\n")
            
        print(f"\nReport saved: {report_path}")
        return report_path

def find_latest_processed_file(meme_name=None):
    """가장 최근 전처리된 파일 찾기"""
    if meme_name:
        # 특정 밈의 파일 찾기
        meme_safe_name = meme_name.replace(' ', '_').lower()
        pattern = f"processed_reddit_{meme_safe_name}_*.csv"
    else:
        # 모든 전처리된 파일 찾기
        pattern = "processed_reddit_*_*.csv"
    
    processed_files = glob.glob(os.path.join(PROCESSED_DATA_DIR, pattern))
    
    if processed_files:
        # 가장 최근 파일 반환
        latest_file = max(processed_files, key=os.path.getctime)
        return latest_file
    else:
        return None

def extract_meme_name_from_processed_filename(filename):
    """전처리된 파일명에서 밈 이름 추출"""
    basename = os.path.basename(filename)
    # processed_reddit_meme_name_timestamp.csv 형식
    parts = basename.replace('processed_reddit_', '').replace('.csv', '').split('_')
    
    # 타임스탬프 부분 제거 (마지막 2개 요소: YYYYMMDD, HHMMSS)
    if len(parts) >= 2:
        # 마지막 2개가 숫자인지 확인 (타임스탬프)
        if parts[-1].isdigit() and parts[-2].isdigit() and len(parts[-2]) == 8:
            meme_parts = parts[:-2]
        else:
            meme_parts = parts
    else:
        meme_parts = parts
    
    return '_'.join(meme_parts)

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='밈 수명 주기 분석')
    parser.add_argument('--meme', type=str, help='분석할 밈 이름')
    parser.add_argument('--file', type=str, help='분석할 특정 파일명')
    
    args = parser.parse_args()
    
    # 처리할 파일 찾기
    if args.file:
        # 특정 파일 지정
        target_file = os.path.join(PROCESSED_DATA_DIR, args.file)
        if not os.path.exists(target_file):
            print(f"파일을 찾을 수 없습니다: {args.file}")
            return
        filepath = target_file
        meme_name = extract_meme_name_from_processed_filename(args.file)
    else:
        # 가장 최근 파일 또는 특정 밈의 파일 찾기
        latest_file = find_latest_processed_file(args.meme)
        if not latest_file:
            if args.meme:
                print(f"'{args.meme}' 밈의 전처리된 데이터 파일을 찾을 수 없습니다.")
            else:
                print("전처리된 데이터 파일을 찾을 수 없습니다.")
            return
        
        filepath = latest_file
        meme_name = extract_meme_name_from_processed_filename(os.path.basename(latest_file))
    
    print(f"분석할 파일: {os.path.basename(filepath)}")
    print(f"밈 이름: {meme_name}")
    
    try:
        # 데이터 로드
        df = pd.read_csv(filepath)
        df['created_utc'] = pd.to_datetime(df['created_utc'])
        df['date'] = pd.to_datetime(df['date'])
        
        # 분석 실행
        analyzer = LifecycleAnalyzer()
        
        print(f"\n=== {meme_name.replace('_', ' ').title()} 밈 수명 주기 분석 ===")
        
        # 1. 생명주기 단계 식별
        daily_metrics, phases = analyzer.identify_lifecycle_phases(df)
        
        # 2. 곡선 피팅
        curve_fit = analyzer.fit_lifecycle_curve(daily_metrics)
        
        # 3. 메트릭 계산
        metrics = analyzer.calculate_lifecycle_metrics(df, daily_metrics)
        
        # 4. 보고서 생성
        report_path = analyzer.generate_report(meme_name, df, daily_metrics, phases, curve_fit, metrics)
        
        print(f"\n✅ '{meme_name}' 밈 분석 완료!")
        print(f"보고서: {report_path}")
        
    except Exception as e:
        print(f"❌ 분석 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

# 실행 코드
if __name__ == "__main__":
    main()