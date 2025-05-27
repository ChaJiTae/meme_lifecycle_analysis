# 밈 수명 주기 분석 프로젝트

## 프로젝트 개요

인터넷 밈(Meme)의 생성, 확산, 소멸 과정을 빅데이터 분석 기법을 통해 연구하는 프로젝트입니다.

## 주요 기능

- 🐦 다중 플랫폼 데이터 수집: Twitter, Reddit, Instagram
- 📊 데이터 전처리: 중복 제거, 정규화, 파생 변수 생성
- 📈 시각화: 생명주기 곡선, 참여도 분석, 확산 패턴
- 🔬 수명 주기 분석: 단계 식별, 곡선 피팅, 메트릭 계산
- 📋 자동 보고서 생성: 한국어/영어 분석 보고서

## 프로젝트 구조

```
meme_lifecycle_analysis/
├── data/
│ ├── raw/ # 원본 데이터
│ └── processed/ # 전처리된 데이터
├── src/
│ ├── collectors/ # 데이터 수집 모듈
│ ├── preprocessors/ # 데이터 전처리 모듈
│ ├── analyzers/ # 분석 모듈
│ └── visualizers/ # 시각화 모듈
├── results/
│ ├── figures/ # 그래프 이미지
│ └── reports/ # 분석 보고서
├── config/ # 설정 파일
├── notebooks/ # Jupyter 노트북
└── tests/ # 테스트 코드
```

## 설치 방법

```
1. 저장소 클론
   bashgit clone [your-repository-url]
   cd meme_lifecycle_analysis
2. 가상환경 설정
   bashpython3.12 -m venv venv
   source venv/bin/activate # Mac/Linux
```

또는

```
venv\Scripts\activate # Windows 3. 의존성 설치
bashpip install -r requirements.txt 4. API 키 설정
config/api_keys_template.py를 config/api_keys.py로 복사하고 실제 API 키 입력:
python# Twitter API
TWITTER_BEARER_TOKEN = "your_bearer_token"
```

## Reddit API

```
REDDIT_CLIENT_ID = "your_client_id"
REDDIT_CLIENT_SECRET = "your_client_secret"
```

## 사용 방법

1. 데이터 수집
   ```
    bash# 모든 플랫폼에서 데이터 수집
    python main.py
   ```

## 특정 플랫폼만 수집

```
python main.py --platform reddit
```

## 특정 밈만 수집

```
python main.py --meme "chill guy" 2. 데이터 전처리
bashpython src/preprocessors/data_preprocessor.py 3. 시각화 생성
bashpython src/visualizers/meme_visualizer.py 4. 수명 주기 분석
bashpython src/analyzers/lifecycle_analyzer.py
```

- 피크 시점: 밈이 최고 인기를 얻는 시점 분석
- 확산 패턴: Slow Burn, Balanced, Viral Spike 등 분류
- 수명 분류: Flash, Short-lived, Standard, Long-lived 밈 구분

## API 제한사항

- Twitter: 15분당 180 요청 (무료 계정)
- Reddit: 분당 60 요청
- Instagram: 매우 제한적, 신중히 사용

## 향후 계획

- 실시간 모니터링 시스템 구축
- 머신러닝 기반 수명 예측 모델
- 더 많은 플랫폼 지원 (TikTok, YouTube 등)
- 웹 대시보드 개발

## 기여 방법

```
Fork the repository
Create your feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request
```

- 라이선스

  - 이 프로젝트는 MIT 라이선스를 따릅니다.

- 문의사항
  - 이메일: wlxo402@naver.com
  - 프로젝트 관련 이슈는 GitHub Issues를 이용해주세요.
