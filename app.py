import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import json
from datetime import datetime

# ============================================================
# 📚 2022 개정 교육과정 - 통합사회 단원 & 성취기준
# ============================================================
UNITS = {
    "통합사회1": {
        "Ⅰ. 통합적 관점": {
            "성취기준": [
                "[10통사1-01-01] 시간적, 공간적, 사회적, 윤리적 관점을 통합하여 사회 현상을 이해한다.",
                "[10통사1-01-02] 통합적 관점이 자연환경과 인간 생활의 관계를 탐구하는 데 어떻게 활용될 수 있는지 분석한다."
            ],
            "핵심개념": "통합적 관점, 시간적·공간적·사회적·윤리적 관점",
            "출제포인트": "네 가지 관점의 특징 구분, 사례에 적용, 통합적 사고의 필요성"
        },
        "Ⅱ. 인간, 사회, 환경과 행복": {
            "성취기준": [
                "[10통사1-02-01] 행복의 의미와 기준을 다양한 측면에서 이해한다.",
                "[10통사1-02-02] 행복한 삶을 위한 조건을 경제적, 사회적, 개인적 측면에서 분석한다."
            ],
            "핵심개념": "행복, 삶의 질, 행복 지수, 객관적·주관적 기준",
            "출제포인트": "행복의 조건, 삶의 질 지표 비교, 행복 실현 방안"
        },
        "Ⅲ. 자연환경과 인간": {
            "성취기준": [
                "[10통사1-03-01] 자연환경이 인간 생활에 미치는 영향을 분석한다.",
                "[10통사1-03-02] 인간의 자연환경 이용과 자연재해에 대한 대응 방안을 탐구한다."
            ],
            "핵심개념": "기후, 지형, 자연재해, 인간과 자연의 관계",
            "출제포인트": "기후와 생활양식, 자연재해 유형과 대응, 환경 문제"
        },
        "Ⅳ. 문화와 다양성": {
            "성취기준": [
                "[10통사1-04-01] 문화의 의미를 이해하고 문화를 바라보는 다양한 관점을 비교한다.",
                "[10통사1-04-02] 문화 변동의 요인과 양상을 이해하고 문화 다양성을 존중하는 태도를 기른다."
            ],
            "핵심개념": "문화, 문화 상대주의, 자문화 중심주의, 문화 사대주의, 문화 변동",
            "출제포인트": "문화 이해 관점 비교, 문화 변동 사례, 다문화 사회"
        },
        "Ⅴ. 생활공간과 사회": {
            "성취기준": [
                "[10통사1-05-01] 산업화와 도시화로 인한 생활공간과 생활양식의 변화를 분석한다.",
                "[10통사1-05-02] 교통·통신의 발달이 생활공간에 미치는 영향을 탐구한다."
            ],
            "핵심개념": "산업화, 도시화, 생활공간 변화, 교통·통신 발달",
            "출제포인트": "도시화 과정과 문제, 공간 불평등, 지역 변화"
        }
    },
    "통합사회2": {
        "Ⅵ. 인권 보장과 헌법": {
            "성취기준": [
                "[10통사2-06-01] 인권의 의미와 변화 양상을 이해하고 인권 보장을 위한 헌법의 역할을 분석한다.",
                "[10통사2-06-02] 인권 침해 사례를 분석하고 구제 방법을 탐구한다."
            ],
            "핵심개념": "인권, 기본권, 헌법, 인권 침해와 구제",
            "출제포인트": "기본권 유형 구분, 인권 보장 기관, 인권 침해 구제 절차"
        },
        "Ⅶ. 사회정의와 불평등": {
            "성취기준": [
                "[10통사2-07-01] 정의의 의미와 실질적 기준을 탐구한다.",
                "[10통사2-07-02] 사회적 불평등 현상의 원인과 해결 방안을 분석한다."
            ],
            "핵심개념": "정의, 공정, 사회적 불평등, 사회 복지",
            "출제포인트": "정의관 비교(롤스, 노직 등), 사회 불평등 양상, 복지 제도"
        },
        "Ⅷ. 시장경제와 지속가능발전": {
            "성취기준": [
                "[10통사2-08-01] 시장경제의 원리와 시장 참여자의 역할을 이해한다.",
                "[10통사2-08-02] 지속가능한 발전을 위한 경제적 노력을 탐구한다."
            ],
            "핵심개념": "시장경제, 수요와 공급, 시장 실패, 지속가능발전",
            "출제포인트": "시장 가격 결정, 시장 실패와 정부 개입, 지속가능발전 사례"
        },
        "Ⅸ. 세계화와 평화": {
            "성취기준": [
                "[10통사2-09-01] 세계화의 양상과 문제를 분석한다.",
                "[10통사2-09-02] 국제 사회의 행위 주체와 평화를 위한 노력을 탐구한다."
            ],
            "핵심개념": "세계화, 국제기구, 국제 분쟁, 평화",
            "출제포인트": "세계화 장단점, 국제 분쟁 유형, 평화 실현 노력"
        },
        "Ⅹ. 미래와 지속 가능한 삶": {
            "성취기준": [
                "[10통사2-10-01] 미래 사회 변화가 우리 삶에 미치는 영향을 예측한다.",
                "[10통사2-10-02] 지속 가능한 미래를 위한 과제를 탐구하고 실천 방안을 모색한다."
            ],
            "핵심개념": "미래 사회, 저출산·고령화, 지속 가능한 삶, 세대 간 형평성",
            "출제포인트": "미래 사회 변화 양상, 지속가능발전 목표(SDGs), 시민 참여"
        }
    }
}

def get_all_units_flat():
    """전체 단원 리스트 반환"""
    units = []
    for subject, unit_dict in UNITS.items():
        for unit_name in unit_dict.keys():
            units.append(f"{subject} > {unit_name}")
    return units

def get_unit_info(unit_full_name):
    """단원 전체 이름으로 정보 조회"""
    for subject, unit_dict in UNITS.items():
        for unit_name, info in unit_dict.items():
            if unit_name in unit_full_name:
                return {
                    "subject": subject,
                    "unit_name": unit_name,
                    **info
                }
    return None

# ============================================================
# 🤖 Gemini API 서비스
# ============================================================
def init_gemini(api_key):
    """Gemini API 초기화"""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")

def analyze_and_generate_similar(model, image, unit_info_list):
    """이미지 분석 후 유사 문항 2개 생성"""
    curriculum_context = ""
    for info in unit_info_list:
        curriculum_context += f"""
[{info['unit_name']}]
- 성취기준: {', '.join(info['성취기준'])}
- 핵심개념: {info['핵심개념']}
- 출제포인트: {info['출제포인트']}
"""

    prompt = f"""당신은 대한민국 고등학교 통합사회 과목의 수능형 문항 출제 전문가입니다.

## 교육과정 성취기준 참조:
{curriculum_context}

## 작업 지시:
1. 업로드된 문항 이미지를 분석하세요.
2. 해당 문항이 평가하는 성취기준과 핵심 개념을 파악하세요.
3. 동일한 성취기준과 유사한 형태의 **수능형 5지 선다 문항 2개**를 생성하세요.

## 문항 출제 규칙:
- 5지 선다형 (①~⑤)
- 개념 파악 위주
- 수능/모의고사 스타일
- 표나 그래프가 필요한 경우: 직접 표를 만들지 말고, [시각 자료 설명: ○○○] 형태로 어떤 자료가 필요한지 상세히 서술
- 보기(ㄱ, ㄴ, ㄷ) 활용 가능
- 정답과 해설 포함

## 출력 형식 (반드시 이 형식을 따르세요):

### 📋 원본 문항 분석
- **관련 단원**: (단원명)
- **성취기준**: (코드)
- **평가 요소**: (무엇을 측정하는지)
- **문항 유형**: (자료 해석형/개념 이해형/사례 분석형 등)

---

### 📝 유사 문항 1
**문제번호: 1**

(문항 본문 - 필요시 [시각 자료 설명: ○○○] 포함)

① (선택지1)
② (선택지2)  
③ (선택지3)
④ (선택지4)
⑤ (선택지5)

**정답**: ○번
**해설**: (상세한 풀이)

---

### 📝 유사 문항 2
**문제번호: 2**

(문항 본문)

① (선택지1)
② (선택지2)
③ (선택지3)
④ (선택지4)
⑤ (선택지5)

**정답**: ○번
**해설**: (상세한 풀이)
"""

    response = model.generate_content([prompt, image])
    return response.text

def generate_exam_by_unit(model, unit_info, difficulty, count=2):
    """단원별 수능형 문항 자동 출제"""
    prompt = f"""당신은 대한민국 고등학교 통합사회 과목의 수능형 문항 출제 전문가입니다.

## 출제 대상 단원:
- 단원: {unit_info['unit_name']}
- 성취기준: {', '.join(unit_info['성취기준'])}
- 핵심개념: {unit_info['핵심개념']}
- 출제포인트: {unit_info['출제포인트']}

## 난이도: {difficulty}

## 출제 규칙:
- 5지 선다형 (①~⑤)
- 개념 파악 위주의 수능/모의고사 스타일
- 표나 그래프가 필요한 경우: [시각 자료 설명: ○○○] 형태로 상세 서술
- 보기(ㄱ, ㄴ, ㄷ) 활용 가능
- 각 문항마다 정답과 상세 해설 포함

## {count}개의 문항을 생성하세요.

## 출력 형식:

### 📝 문항 1
**문제번호: 1**

(문항 본문 - 필요시 [시각 자료 설명: ○○○] 포함)

① (선택지1)
② (선택지2)
③ (선택지3)
④ (선택지4)
⑤ (선택지5)

**정답**: ○번
**해설**: (상세한 풀이)

---

(이하 동일 형식으로 반복)
"""

    response = model.generate_content(prompt)
    return response.text

def generate_cross_unit(model, image, source_unit_info, target_unit_info):
    """교차 단원 출제: 이미지 형태 유지 + 다른 단원 내용"""
    prompt = f"""당신은 대한민국 고등학교 통합사회 과목의 수능형 문항 출제 전문가입니다.

## 작업 지시:
1. 업로드된 문항 이미지의 **문항 형태(구조, 자료 제시 방식, 질문 유형)**를 분석하세요.
2. 그 형태를 유지하되, **내용은 아래 타겟 단원의 성취기준**에 맞게 변환하세요.

## 원본 문항 단원 (형태 참고용):
- 단원: {source_unit_info['unit_name'] if source_unit_info else '이미지에서 자동 분석'}
- 핵심개념: {source_unit_info['핵심개념'] if source_unit_info else '자동 분석'}

## 타겟 단원 (내용 적용 대상):
- 단원: {target_unit_info['unit_name']}
- 성취기준: {', '.join(target_unit_info['성취기준'])}
- 핵심개념: {target_unit_info['핵심개념']}
- 출제포인트: {target_unit_info['출제포인트']}

## 출제 규칙:
- 5지 선다형 (①~⑤)
- 원본 문항의 형태(구조)를 최대한 유지
- 내용만 타겟 단원으로 교체
- 표나 그래프 필요 시: [시각 자료 설명: ○○○] 형태로 상세 서술
- 정답과 해설 포함

## 출력 형식:

### 📋 원본 문항 형태 분석
- **문항 구조**: (자료 제시형/대화문형/사례 분석형 등)
- **자료 유형**: (표/그래프/지도/대화문/제시문 등)
- **질문 유형**: (옳은 것 고르기/분석하기/추론하기 등)

---

### 📝 교차 단원 문항 1
**[{target_unit_info['unit_name']}] 적용**

(문항 본문 - 원본 형태 유지, 내용은 타겟 단원)

① (선택지1)
② (선택지2)
③ (선택지3)
④ (선택지4)
⑤ (선택지5)

**정답**: ○번
**해설**: (상세한 풀이)

---

### 📝 교차 단원 문항 2
(동일 형식)
"""

    response = model.generate_content([prompt, image])
    return response.text

# ============================================================
# 🎨 Streamlit 앱 UI
# ============================================================

# 페이지 설정
st.set_page_config(
    page_title="📚 통합사회 유사 문항 출제기",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E88E5;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        background-color: #f8f9fa;
        border-left: 4px solid #1E88E5;
        padding: 1.5rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        line-height: 1.8;
    }
    .unit-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.3rem 0;
        text-align: center;
    }
    .success-msg {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 사이드바
# ============================================================
with st.sidebar:
    st.markdown("## 🔑 API 설정")
    api_key = st.text_input(
        "Gemini API 키",
        type="password",
        help="Google AI Studio에서 발급받은 API 키를 입력하세요"
    )

    if api_key:
        try:
            model = init_gemini(api_key)
            st.success("✅ Gemini 연결 완료!")
        except Exception as e:
            st.error(f"❌ 연결 실패: {e}")
            model = None
    else:
        model = None
        st.info("👆 API 키를 입력해주세요")
        st.markdown("[🔗 API 키 발급 (무료)](https://aistudio.google.com/apikey)")

    st.markdown("---")
    st.markdown("## 📖 지원 단원")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**통합사회1**")
        for unit_name in UNITS["통합사회1"].keys():
            st.markdown(f"📗 {unit_name}")
    with col2:
        st.markdown("**통합사회2**")
        for unit_name in UNITS["통합사회2"].keys():
            st.markdown(f"📘 {unit_name}")

# ============================================================
# 메인 헤더
# ============================================================
st.markdown('<div class="main-header">📚 통합사회 유사 문항 출제기</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">2022 개정 교육과정 | 고등학교 통합사회 1·2 | Gemini AI 기반</div>', unsafe_allow_html=True)

# ============================================================
# 탭 구성
# ============================================================
tab1, tab2, tab3 = st.tabs([
    "📸 이미지 → 유사 문항",
    "📝 수능형 자동 출제",
    "🔀 교차 단원 출제"
])

# ============================================================
# 탭 1: 이미지 → 유사 문항
# ============================================================
with tab1:
    st.markdown("### 📸 문항 이미지를 업로드하면 유사 문항 2개를 생성합니다")

    col_upload, col_result = st.columns([1, 1])

    with col_upload:
        st.markdown("#### 문항 이미지 업로드")
        uploaded_file = st.file_uploader(
            "문항 이미지를 선택하세요",
            type=["png", "jpg", "jpeg", "webp"],
            key="similar_upload"
        )

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="업로드된 문항", use_container_width=True)

    with col_result:
        if uploaded_file and model:
            if st.button("🚀 유사 문항 생성", key="btn_similar", use_container_width=True, type="primary"):
                with st.spinner("🤖 Gemini가 문항을 분석하고 유사 문항을 생성 중..."):
                    try:
                        image = Image.open(uploaded_file)
                        all_units_info = []
                        for subject, units in UNITS.items():
                            for unit_name, info in units.items():
                                all_units_info.append({
                                    "unit_name": unit_name,
                                    **info
                                })
                        result = analyze_and_generate_similar(model, image, all_units_info)
                        st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
                        st.markdown(result)

                        # 세션에 저장
                        if "history" not in st.session_state:
                            st.session_state.history = []
                        st.session_state.history.append({
                            "type": "유사문항",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "result": result
                        })
                    except Exception as e:
                        st.error(f"오류 발생: {e}")
        elif not model:
            st.warning("⬅️ 사이드바에서 Gemini API 키를 먼저 입력해주세요")
        elif not uploaded_file:
            st.info("⬅️ 문항 이미지를 업로드해주세요")

# ============================================================
# 탭 2: 수능형 자동 출제
# ============================================================
with tab2:
    st.markdown("### 📝 단원과 난이도를 선택하면 수능형 문항을 자동 출제합니다")

    col_setting, col_result2 = st.columns([1, 1])

    with col_setting:
        st.markdown("#### 출제 설정")

        # 과목 선택
        subject_choice = st.radio(
            "과목 선택",
            ["통합사회1", "통합사회2", "전체"],
            horizontal=True,
            key="exam_subject"
        )

        # 단원 선택
        if subject_choice == "전체":
            available_units = get_all_units_flat()
        else:
            available_units = [
                f"{subject_choice} > {unit}" 
                for unit in UNITS[subject_choice].keys()
            ]

        selected_units = st.multiselect(
            "단원 선택 (복수 선택 가능)",
            available_units,
            key="exam_units"
        )

        # 난이도
        difficulty = st.select_slider(
            "난이도",
            options=["매우 쉬움", "쉬움", "보통", "어려움", "매우 어려움"],
            value="보통",
            key="exam_difficulty"
        )

        # 문항 수
        question_count = st.slider("문항 수", 1, 5, 2, key="exam_count")

    with col_result2:
        if selected_units and model:
            if st.button("📝 문항 출제", key="btn_exam", use_container_width=True, type="primary"):
                with st.spinner("🤖 Gemini가 문항을 출제 중..."):
                    try:
                        all_results = []
                        for unit_full in selected_units:
                            info = get_unit_info(unit_full)
                            if info:
                                result = generate_exam_by_unit(model, info, difficulty, question_count)
                                all_results.append(f"## 📗 {info['unit_name']}\n\n{result}")

                        final_result = "\n\n---\n\n".join(all_results)
                        st.markdown(final_result)

                        if "history" not in st.session_state:
                            st.session_state.history = []
                        st.session_state.history.append({
                            "type": "수능형출제",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "result": final_result
                        })
                    except Exception as e:
                        st.error(f"오류 발생: {e}")
        elif not model:
            st.warning("⬅️ 사이드바에서 Gemini API 키를 먼저 입력해주세요")
        elif not selected_units:
            st.info("⬅️ 출제할 단원을 선택해주세요")

# ============================================================
# 탭 3: 교차 단원 출제
# ============================================================
with tab3:
    st.markdown("### 🔀 이미지 문항의 형태를 유지하고, 다른 단원의 내용으로 변환합니다")

    col_cross_upload, col_cross_result = st.columns([1, 1])

    with col_cross_upload:
        st.markdown("#### 1️⃣ 원본 문항 이미지 업로드")
        cross_file = st.file_uploader(
            "문항 이미지를 선택하세요",
            type=["png", "jpg", "jpeg", "webp"],
            key="cross_upload"
        )

        if cross_file:
            cross_image = Image.open(cross_file)
            st.image(cross_image, caption="원본 문항", use_container_width=True)

        st.markdown("#### 2️⃣ 타겟 단원 선택")
        target_unit = st.selectbox(
            "변환할 단원을 선택하세요",
            get_all_units_flat(),
            key="cross_target"
        )

    with col_cross_result:
        if cross_file and target_unit and model:
            if st.button("🔀 교차 단원 문항 생성", key="btn_cross", use_container_width=True, type="primary"):
                with st.spinner("🤖 형태 분석 → 단원 내용 변환 중..."):
                    try:
                        cross_image = Image.open(cross_file)
                        target_info = get_unit_info(target_unit)

                        result = generate_cross_unit(
                            model, cross_image,
                            None,
                            target_info
                        )
                        st.markdown(result)

                        if "history" not in st.session_state:
                            st.session_state.history = []
                        st.session_state.history.append({
                            "type": "교차단원",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "result": result
                        })
                    except Exception as e:
                        st.error(f"오류 발생: {e}")
        elif not model:
            st.warning("⬅️ 사이드바에서 Gemini API 키를 먼저 입력해주세요")

# ============================================================
# 하단: 출제 이력
# ============================================================
st.markdown("---")
st.markdown("### 📊 출제 이력")

if "history" in st.session_state and st.session_state.history:
    for i, item in enumerate(reversed(st.session_state.history)):
        with st.expander(f"[{item['type']}] {item['timestamp']}"):
            st.markdown(item['result'])
else:
    st.info("아직 출제 이력이 없습니다. 위에서 문항을 생성해보세요! 🚀")

# 푸터
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#999; font-size:0.9rem;'>"
    "📚 통합사회 유사 문항 출제기 v2.0 | 2022 개정 교육과정 | Powered by Gemini AI"
    "</div>",
    unsafe_allow_html=True
)
