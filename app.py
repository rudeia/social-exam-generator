import streamlit as st
import json
import os
from datetime import datetime

# ============================================================
# 📚 설정: 2022 개정 교육과정 통합사회 단원 & 성취기준
# ============================================================

UNITS = {
    "통합사회1": {
        "Ⅰ. 통합적 관점": {
            "성취기준": [
                "[10통사1-01-01] 사회적 삶의 모습을 시간적, 공간적, 사회적, 윤리적 관점에서 통합적으로 살펴본다.",
                "[10통사1-01-02] 통합적 관점을 적용하여 우리 사회의 다양한 현상과 문제를 분석하고 탐구한다."
            ],
            "핵심개념": "통합적 관점, 시간적·공간적·사회적·윤리적 관점, 사회 현상 분석",
            "출제포인트": "시간적·공간적·사회적·윤리적 관점의 특징 구분, 통합적 관점 적용 사례 분석"
        },
        "Ⅱ. 인간, 사회, 환경과 행복": {
            "성취기준": [
                "[10통사1-02-01] 행복의 의미와 기준이 시대와 지역에 따라 달라질 수 있음을 이해한다.",
                "[10통사1-02-02] 행복한 삶을 위해 필요한 조건을 경제적, 사회적, 환경적 측면에서 탐구한다.",
                "[10통사1-02-03] 다양한 사회에서 나타나는 행복 지수와 삶의 질을 비교 분석한다."
            ],
            "핵심개념": "행복의 의미, 삶의 질, 행복 지수, 행복의 조건",
            "출제포인트": "행복의 기준 비교, 행복 지수 분석, 삶의 질 향상 방안"
        },
        "Ⅲ. 자연환경과 인간": {
            "성취기준": [
                "[10통사1-03-01] 자연환경이 인간의 생활에 미치는 영향을 다양한 사례를 통해 탐구한다.",
                "[10통사1-03-02] 인간의 자연환경 이용 방식이 시대에 따라 변화해 왔음을 파악한다.",
                "[10통사1-03-03] 환경 문제의 발생 원인과 해결 방안을 지속가능성의 관점에서 탐색한다."
            ],
            "핵심개념": "자연환경, 기후, 지형, 인간과 자연의 관계, 환경 문제, 지속가능성",
            "출제포인트": "기후·지형이 인간 생활에 미치는 영향, 환경 문제 원인과 해결 방안"
        },
        "Ⅳ. 문화와 다양성": {
            "성취기준": [
                "[10통사1-04-01] 문화의 의미와 특징을 이해하고 다양한 문화권의 삶의 방식을 탐구한다.",
                "[10통사1-04-02] 문화 변동의 다양한 양상을 이해하고 현대 사회에서 전통문화의 의의를 탐색한다.",
                "[10통사1-04-03] 문화 상대주의와 보편 윤리의 관계를 이해하고 다문화 사회의 바람직한 자세를 모색한다."
            ],
            "핵심개념": "문화의 의미, 문화 변동, 문화 상대주의, 보편 윤리, 다문화 사회",
            "출제포인트": "문화 변동 요인 구분, 문화 상대주의 vs 자문화중심주의 vs 문화 사대주의"
        },
        "Ⅴ. 생활공간과 사회": {
            "성취기준": [
                "[10통사1-05-01] 산업화와 도시화로 인한 생활공간의 변화를 파악한다.",
                "[10통사1-05-02] 교통·통신의 발달에 따른 생활공간의 변화를 탐구한다.",
                "[10통사1-05-03] 생활공간에서 나타나는 다양한 문제를 파악하고 해결 방안을 모색한다."
            ],
            "핵심개념": "산업화, 도시화, 생활공간 변화, 교통·통신 발달, 도시 문제",
            "출제포인트": "도시화의 특징과 문제, 교통·통신 발달의 영향, 공간 불평등"
        }
    },
    "통합사회2": {
        "Ⅵ. 인권 보장과 헌법": {
            "성취기준": [
                "[10통사2-06-01] 인권의 의미와 발전 과정을 이해하고 현대 사회에서 인권의 중요성을 인식한다.",
                "[10통사2-06-02] 헌법이 보장하는 기본권의 내용을 파악하고 기본권 침해 시 구제 방법을 탐구한다.",
                "[10통사2-06-03] 근로자의 권리와 노동권 보장의 중요성을 이해한다."
            ],
            "핵심개념": "인권, 기본권, 헌법, 기본권 구제, 근로자의 권리, 노동권",
            "출제포인트": "기본권의 종류와 특징, 기본권 침해 구제 방법, 노동 3권"
        },
        "Ⅶ. 사회정의와 불평등": {
            "성취기준": [
                "[10통사2-07-01] 정의의 의미와 실질적 기준을 탐구하고 다양한 정의관을 비교 분석한다.",
                "[10통사2-07-02] 사회적 불평등 현상을 다양한 측면에서 파악하고 이를 해소하기 위한 방안을 모색한다.",
                "[10통사2-07-03] 사회 복지와 복지 제도의 역할을 이해하고 바람직한 복지의 방향을 탐색한다."
            ],
            "핵심개념": "정의, 공정, 사회 불평등, 사회 이동, 사회 복지",
            "출제포인트": "롤스·노직 정의관 비교, 사회 계층 구조, 사회 복지 제도"
        },
        "Ⅷ. 시장경제와 지속가능발전": {
            "성취기준": [
                "[10통사2-08-01] 시장경제의 원리와 시장 참여자의 역할을 이해한다.",
                "[10통사2-08-02] 시장 실패와 정부 실패의 원인을 파악하고 이를 보완하는 방안을 탐색한다.",
                "[10통사2-08-03] 합리적 소비와 금융 생활의 중요성을 이해하고 지속가능발전과의 관계를 탐구한다."
            ],
            "핵심개념": "시장경제, 수요·공급, 시장 실패, 정부 실패, 합리적 소비, 금융, 지속가능발전",
            "출제포인트": "수요·공급 법칙, 시장 실패 유형, 합리적 소비와 금융 설계"
        },
        "Ⅸ. 세계화와 평화": {
            "성취기준": [
                "[10통사2-09-01] 세계화의 양상과 그에 따른 문제점을 다양한 측면에서 탐구한다.",
                "[10통사2-09-02] 국제 사회의 행위 주체와 국제 관계의 특성을 이해한다.",
                "[10통사2-09-03] 국제 분쟁의 원인을 파악하고 평화의 중요성 및 실현 방안을 모색한다."
            ],
            "핵심개념": "세계화, 국제 관계, 국제기구, 국제 분쟁, 평화",
            "출제포인트": "세계화의 긍정적·부정적 영향, 국제 관계 관점(현실주의/자유주의), 평화 실현 방안"
        },
        "Ⅹ. 미래와 지속 가능한 삶": {
            "성취기준": [
                "[10통사2-10-01] 과학기술의 발전이 가져올 미래 사회의 변화를 다양한 측면에서 예측한다.",
                "[10통사2-10-02] 지속가능한 미래를 위한 개인적·사회적·국가적 노력을 탐색한다.",
                "[10통사2-10-03] 세대 간 형평성과 미래 세대에 대한 책임을 인식하고 실천 방안을 모색한다."
            ],
            "핵심개념": "미래 사회, 과학기술, 지속가능한 삶, 세대 간 형평성",
            "출제포인트": "4차 산업혁명의 영향, 지속가능발전 목표(SDGs), 세대 간 정의"
        }
    }
}

def get_all_units_flat():
    """모든 단원을 평면 리스트로 반환"""
    result = []
    for subject, units in UNITS.items():
        for unit_name in units.keys():
            result.append(f"{subject} > {unit_name}")
    return result

def get_unit_info(unit_name):
    """단원명으로 성취기준 정보 반환"""
    for subject, units in UNITS.items():
        for name, info in units.items():
            if name == unit_name or f"{subject} > {name}" == unit_name:
                return {
                    "subject": subject,
                    "unit": name,
                    **info
                }
    return None

# ============================================================
# 🤖 Gemini 서비스
# ============================================================

def init_gemini(api_key):
    """Gemini API 초기화"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
        return model
    except Exception as e:
        st.error(f"Gemini 초기화 실패: {e}")
        return None

def analyze_and_generate_similar(model, image_bytes, filename):
    """이미지 문항 분석 → 유사 문항 2개 생성"""
    import google.generativeai as genai

    # 성취기준 전체 텍스트 생성
    standards_text = ""
    for subject, units in UNITS.items():
        for unit_name, info in units.items():
            standards_text += f"\n[{subject} - {unit_name}]\n"
            for s in info["성취기준"]:
                standards_text += f"  {s}\n"
            standards_text += f"  핵심개념: {info['핵심개념']}\n"
            standards_text += f"  출제포인트: {info['출제포인트']}\n"

    prompt = f"""당신은 대한민국 고등학교 2022 개정 교육과정 '통합사회' 전문 출제 교사입니다.

아래는 2022 개정 교육과정 통합사회의 성취기준입니다:
{standards_text}

[작업]
1. 업로드된 이미지의 문항을 정확히 읽고 분석하세요.
2. 해당 문항이 어떤 단원, 어떤 성취기준에 해당하는지 판별하세요.
3. 동일한 성취기준과 유사한 난이도로 **5지선다형 유사 문항 2개**를 만드세요.

[출제 규칙]
- 5지선다형 (①②③④⑤)
- 개념 파악 위주
- 수능 스타일 문항 형태
- 문항마다 정답과 해설 포함
- 표나 그래프가 필요한 경우: 직접 그리지 말고 [시각 자료 설명] 블록에 어떤 표/그래프인지 상세히 텍스트로 설명
- 한국어로 작성

[출력 형식 - 반드시 아래 JSON 형식으로 출력]
{{
  "원본분석": {{
    "단원": "해당 단원명",
    "성취기준": "해당 성취기준 코드",
    "핵심개념": "해당 핵심 개념",
    "문항유형": "문항의 유형 설명"
  }},
  "유사문항": [
    {{
      "문항번호": 1,
      "문제": "문제 전문",
      "보기": ["①선지1", "②선지2", "③선지3", "④선지4", "⑤선지5"],
      "정답": "③",
      "해설": "상세한 해설",
      "시각자료설명": "필요한 경우 표/그래프 설명 (없으면 null)"
    }},
    {{
      "문항번호": 2,
      "문제": "문제 전문",
      "보기": ["①선지1", "②선지2", "③선지3", "④선지4", "⑤선지5"],
      "정답": "②",
      "해설": "상세한 해설",
      "시각자료설명": "필요한 경우 표/그래프 설명 (없으면 null)"
    }}
  ]
}}"""

    image_part = genai.types.Part.from_data(data=image_bytes, mime_type="image/png")
    response = model.generate_content([prompt, image_part])
    return response.text

def generate_exam_by_unit(model, unit_names, difficulty="중", count=2):
    """단원별 수능형 문항 자동 출제"""
    # 선택된 단원의 성취기준 수집
    selected_info = ""
    for unit_name in unit_names:
        info = get_unit_info(unit_name)
        if info:
            selected_info += f"\n[{info['subject']} - {info['unit']}]\n"
            for s in info["성취기준"]:
                selected_info += f"  {s}\n"
            selected_info += f"  핵심개념: {info['핵심개념']}\n"
            selected_info += f"  출제포인트: {info['출제포인트']}\n"

    prompt = f"""당신은 대한민국 고등학교 2022 개정 교육과정 '통합사회' 전문 출제 교사입니다.

아래 단원의 성취기준을 바탕으로 수능 스타일 문항을 출제하세요:
{selected_info}

[출제 조건]
- 문항 수: {count}개
- 난이도: {difficulty}
- 형태: 5지선다형 (①②③④⑤)
- 개념 파악 위주
- 수능 스타일 (지문 + 발문 + 선지)
- 표나 그래프가 필요한 경우: [시각 자료 설명] 블록에 어떤 표/그래프인지 상세히 텍스트로 설명
- 한국어로 작성

[출력 형식 - 반드시 아래 JSON 형식으로 출력]
{{
  "문항": [
    {{
      "문항번호": 1,
      "단원": "단원명",
      "성취기준": "성취기준 코드",
      "난이도": "{difficulty}",
      "문제": "문제 전문 (지문 포함)",
      "보기": ["①선지1", "②선지2", "③선지3", "④선지4", "⑤선지5"],
      "정답": "③",
      "해설": "상세한 해설",
      "시각자료설명": "필요한 경우 표/그래프 설명 (없으면 null)"
    }}
  ]
}}"""

    response = model.generate_content(prompt)
    return response.text

def generate_cross_unit(model, image_bytes, target_unit_names):
    """이미지 문항 형태 유지 + 다른 단원 내용으로 교차 출제"""
    import google.generativeai as genai

    target_info = ""
    for unit_name in target_unit_names:
        info = get_unit_info(unit_name)
        if info:
            target_info += f"\n[{info['subject']} - {info['unit']}]\n"
            for s in info["성취기준"]:
                target_info += f"  {s}\n"
            target_info += f"  핵심개념: {info['핵심개념']}\n"
            target_info += f"  출제포인트: {info['출제포인트']}\n"

    prompt = f"""당신은 대한민국 고등학교 2022 개정 교육과정 '통합사회' 전문 출제 교사입니다.

[작업]
1. 업로드된 이미지의 문항을 정확히 읽고 **문항의 형태(구조, 발문 방식, 선지 구성 방식)**를 분석하세요.
2. 그 문항 형태는 유지하되, **아래 타겟 단원의 내용**으로 교체하여 새 문항을 만드세요.

[타겟 단원 성취기준]
{target_info}

[출제 규칙]
- 원본 문항의 형태(구조)를 최대한 유지
- 내용만 타겟 단원으로 교체
- 5지선다형 (①②③④⑤)
- 개념 파악 위주
- 문항 수: 타겟 단원당 1개씩
- 표나 그래프가 필요한 경우: [시각 자료 설명] 블록에 어떤 표/그래프인지 상세히 텍스트로 설명
- 한국어로 작성

[출력 형식 - 반드시 아래 JSON 형식으로 출력]
{{
  "원본형태분석": {{
    "문항구조": "원본 문항의 구조 설명",
    "발문방식": "발문 방식 설명",
    "선지구성": "선지 구성 방식 설명"
  }},
  "교차문항": [
    {{
      "문항번호": 1,
      "타겟단원": "단원명",
      "성취기준": "성취기준 코드",
      "문제": "문제 전문",
      "보기": ["①선지1", "②선지2", "③선지3", "④선지4", "⑤선지5"],
      "정답": "③",
      "해설": "상세한 해설",
      "시각자료설명": "필요한 경우 표/그래프 설명 (없으면 null)"
    }}
  ]
}}"""

    image_part = genai.types.Part.from_data(data=image_bytes, mime_type="image/png")
    response = model.generate_content([prompt, image_part])
    return response.text

# ============================================================
# 🔧 유틸리티
# ============================================================

def parse_json_response(text):
    """Gemini 응답에서 JSON 추출"""
    try:
        # ```json ... ``` 블록 추출
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            text = text[start:end].strip()
        return json.loads(text)
    except:
        return None

def display_question(q, idx=None):
    """문항 하나를 예쁘게 표시"""
    title = f"### 📝 문항 {q.get('문항번호', idx or '')}"
    st.markdown(title)

    # 단원/성취기준 정보
    if q.get("단원"):
        st.caption(f"📚 {q['단원']} | {q.get('성취기준', '')}")
    if q.get("난이도"):
        st.caption(f"⭐ 난이도: {q['난이도']}")

    # 시각자료 설명
    if q.get("시각자료설명") and q["시각자료설명"] != "null":
        st.info(f"📊 **[시각 자료 설명]**\n\n{q['시각자료설명']}")

    # 문제
    st.markdown(f"**{q['문제']}**")

    # 보기
    for choice in q.get("보기", []):
        st.markdown(f"　{choice}")

    # 정답 & 해설 (접기)
    with st.expander("✅ 정답 & 해설 보기"):
        st.success(f"**정답: {q['정답']}**")
        st.markdown(q.get("해설", ""))

    st.divider()

# ============================================================
# 🎨 메인 앱 UI
# ============================================================

def main():
    st.set_page_config(
        page_title="📚 통합사회 문항 출제기",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 사이드바
    with st.sidebar:
        st.title("⚙️ 설정")
        st.divider()

        # API 키 입력
        api_key = st.text_input(
            "🔑 Gemini API 키",
            type="password",
            placeholder="AIza... 형태의 키 입력",
            help="[Google AI Studio](https://aistudio.google.com/apikey)에서 무료 발급"
        )

        if api_key:
            model = init_gemini(api_key)
            if model:
                st.success("✅ Gemini 연결 완료!")
                st.session_state["model"] = model
                st.session_state["api_key"] = api_key
            else:
                st.error("❌ API 키를 확인해주세요")
        else:
            st.warning("⬆️ API 키를 입력하세요")

        st.divider()

        # 단원 목록
        st.subheader("📖 지원 단원")
        for subject, units in UNITS.items():
            st.markdown(f"**{subject}**")
            for unit_name in units.keys():
                st.caption(f"　{unit_name}")

    # 메인 영역 - 탭
    st.title("📚 통합사회 문항 출제기")
    st.caption("2022 개정 교육과정 | 통합사회1·2 | Gemini 2.5 AI 기반")

    tab1, tab2, tab3 = st.tabs([
        "📸 이미지 → 유사 문항",
        "📝 수능형 자동 출제",
        "🔀 교차 단원 출제"
    ])

    # ──────────────────────────────────────
    # 📸 탭1: 이미지 → 유사 문항
    # ──────────────────────────────────────
    with tab1:
        st.header("📸 이미지 → 유사 문항 생성")
        st.markdown("문항 이미지를 업로드하면 **동일 성취기준 기반 유사 문항 2개**를 생성합니다.")

        uploaded_file = st.file_uploader(
            "문항 이미지 업로드",
            type=["png", "jpg", "jpeg", "webp"],
            key="similar_upload"
        )

        if uploaded_file:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(uploaded_file, caption="업로드된 문항", use_container_width=True)

            with col2:
                if st.button("🚀 유사 문항 생성", key="btn_similar", type="primary", use_container_width=True):
                    if "model" not in st.session_state:
                        st.error("⬅️ 사이드바에서 API 키를 먼저 입력하세요!")
                    else:
                        with st.spinner("🔄 문항을 분석하고 유사 문항을 생성 중... (30초~1분)"):
                            try:
                                image_bytes = uploaded_file.getvalue()
                                result_text = analyze_and_generate_similar(
                                    st.session_state["model"],
                                    image_bytes,
                                    uploaded_file.name
                                )

                                result = parse_json_response(result_text)

                                if result:
                                    # 원본 분석
                                    st.subheader("🔍 원본 문항 분석")
                                    analysis = result.get("원본분석", {})
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        st.info(f"📚 **단원:** {analysis.get('단원', 'N/A')}")
                                        st.info(f"📋 **성취기준:** {analysis.get('성취기준', 'N/A')}")
                                    with col_b:
                                        st.info(f"💡 **핵심개념:** {analysis.get('핵심개념', 'N/A')}")
                                        st.info(f"📝 **문항유형:** {analysis.get('문항유형', 'N/A')}")

                                    st.divider()

                                    # 유사 문항
                                    st.subheader("✨ 유사 문항")
                                    for q in result.get("유사문항", []):
                                        display_question(q)
                                else:
                                    st.warning("JSON 파싱 실패. 원본 응답을 표시합니다:")
                                    st.code(result_text)
                            except Exception as e:
                                st.error(f"오류 발생: {e}")

    # ──────────────────────────────────────
    # 📝 탭2: 수능형 자동 출제
    # ──────────────────────────────────────
    with tab2:
        st.header("📝 수능형 자동 출제")
        st.markdown("단원과 난이도를 선택하면 **수능 스타일 문항**을 자동 생성합니다.")

        all_units = get_all_units_flat()

        selected_units = st.multiselect(
            "📚 출제 단원 선택 (복수 선택 가능)",
            options=all_units,
            default=None,
            placeholder="단원을 선택하세요..."
        )

        col1, col2 = st.columns(2)
        with col1:
            difficulty = st.select_slider(
                "⭐ 난이도",
                options=["하", "중하", "중", "중상", "상"],
                value="중"
            )
        with col2:
            count = st.number_input("📊 문항 수", min_value=1, max_value=10, value=2)

        if st.button("🚀 문항 출제", key="btn_exam", type="primary", use_container_width=True):
            if "model" not in st.session_state:
                st.error("⬅️ 사이드바에서 API 키를 먼저 입력하세요!")
            elif not selected_units:
                st.error("📚 단원을 하나 이상 선택하세요!")
            else:
                # 단원명만 추출
                unit_names = [u.split(" > ")[1] for u in selected_units]

                with st.spinner("🔄 수능형 문항을 생성 중... (30초~1분)"):
                    try:
                        result_text = generate_exam_by_unit(
                            st.session_state["model"],
                            unit_names,
                            difficulty,
                            count
                        )

                        result = parse_json_response(result_text)

                        if result:
                            st.subheader("✨ 생성된 문항")
                            for q in result.get("문항", []):
                                display_question(q)
                        else:
                            st.warning("JSON 파싱 실패. 원본 응답을 표시합니다:")
                            st.code(result_text)
                    except Exception as e:
                        st.error(f"오류 발생: {e}")

    # ──────────────────────────────────────
    # 🔀 탭3: 교차 단원 출제
    # ──────────────────────────────────────
    with tab3:
        st.header("🔀 교차 단원 출제")
        st.markdown("업로드한 문항의 **형태(구조)는 유지**하고, **다른 단원의 내용**으로 새 문항을 만듭니다.")

        uploaded_cross = st.file_uploader(
            "문항 이미지 업로드",
            type=["png", "jpg", "jpeg", "webp"],
            key="cross_upload"
        )

        target_units = st.multiselect(
            "🎯 타겟 단원 선택 (내용을 가져올 단원)",
            options=all_units if 'all_units' in dir() else get_all_units_flat(),
            default=None,
            placeholder="변환할 단원을 선택하세요...",
            key="cross_units"
        )

        if uploaded_cross:
            st.image(uploaded_cross, caption="업로드된 원본 문항", width=400)

        if st.button("🚀 교차 출제", key="btn_cross", type="primary", use_container_width=True):
            if "model" not in st.session_state:
                st.error("⬅️ 사이드바에서 API 키를 먼저 입력하세요!")
            elif not uploaded_cross:
                st.error("📸 문항 이미지를 업로드하세요!")
            elif not target_units:
                st.error("🎯 타겟 단원을 하나 이상 선택하세요!")
            else:
                target_names = [u.split(" > ")[1] for u in target_units]

                with st.spinner("🔄 교차 단원 문항을 생성 중... (30초~1분)"):
                    try:
                        image_bytes = uploaded_cross.getvalue()
                        result_text = generate_cross_unit(
                            st.session_state["model"],
                            image_bytes,
                            target_names
                        )

                        result = parse_json_response(result_text)

                        if result:
                            # 원본 형태 분석
                            st.subheader("🔍 원본 문항 형태 분석")
                            form = result.get("원본형태분석", {})
                            st.info(f"📐 **문항구조:** {form.get('문항구조', 'N/A')}")
                            st.info(f"❓ **발문방식:** {form.get('발문방식', 'N/A')}")
                            st.info(f"📋 **선지구성:** {form.get('선지구성', 'N/A')}")

                            st.divider()

                            # 교차 문항
                            st.subheader("✨ 교차 출제 문항")
                            for q in result.get("교차문항", []):
                                display_question(q)
                        else:
                            st.warning("JSON 파싱 실패. 원본 응답을 표시합니다:")
                            st.code(result_text)
                    except Exception as e:
                        st.error(f"오류 발생: {e}")

    # 하단 정보
    st.divider()
    st.caption("📚 2022 개정 교육과정 통합사회 1·2 | Gemini 2.5 AI 기반 문항 출제기 | v2.0")

if __name__ == "__main__":
    main()
