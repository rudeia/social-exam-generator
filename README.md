# 📝 통합사회 유사 문항 출제기

> 2022 개정 교육과정 | 고등학교 통합사회1·2 | Gemini 2.5 기반

## 🎯 주요 기능

| 기능 | 설명 |
|------|------|
| 📸 이미지→유사문항 | 시험 문항 이미지 업로드 → 유사 문항 2개 자동 생성 |
| 📝 수능형 자동출제 | 단원·난이도 선택 → 수능 스타일 5지 선다형 출제 |
| 🔀 교차 단원 출제 | 이미지 문항 형태 유지 + 다른 단원 내용으로 변환 |
| 📊 출제 이력 | 생성 기록 확인 |

## 📖 지원 단원

### 통합사회1
- Ⅰ. 통합적 관점
- Ⅱ. 인간, 사회, 환경과 행복
- Ⅲ. 자연환경과 인간
- Ⅳ. 문화와 다양성
- Ⅴ. 생활공간과 사회

### 통합사회2
- Ⅵ. 인권 보장과 헌법
- Ⅶ. 사회정의와 불평등
- Ⅷ. 시장경제와 지속가능발전
- Ⅸ. 세계화와 평화
- Ⅹ. 미래와 지속가능한 삶

## 🚀 실행 방법

### 로컬 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Streamlit Cloud 배포
1. 이 저장소를 GitHub에 Push
2. [share.streamlit.io](https://share.streamlit.io) 접속
3. 저장소 연결 → 자동 배포

## 🔑 필요 API
- **Gemini API Key**: [Google AI Studio](https://aistudio.google.com/apikey)에서 무료 발급

## 📦 기술 스택
- Python 3.9+
- Streamlit
- Google Generative AI (Gemini 2.5)
- Pillow (이미지 처리)
