"""
📝 통합사회 유사 문항 출제기 v2
2022 개정 교육과정 | 통합사회1·2
GitHub → Streamlit Cloud 배포용
"""

import streamlit as st
from PIL import Image

from config.settings import UNITS, get_all_units_flat, get_unit_info
from services.gemini_service import GeminiService
from services.sheets_service import SheetsService

# ══════════════════════════════════════════════
#  페이지 설정
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="통합사회 문항 출제기",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════
#  세션 상태 초기화
# ══════════════════════════════════════════════
if "gemini" not in st.session_state:
    st.session_state.gemini = None
if "sheets" not in st.session_state:
    st.session_state.sheets = SheetsService()
if "api_connected" not in st.session_state:
    st.session_state.api_connected = False

# ══════════════════════════════════════════════
#  사이드바
# ══════════════════════════════════════════════
with st.sidebar:
    st.image("https://em-content.zobj.net/source/twitter/376/memo_1f4dd.png", width=60)
    st.title("통합사회 출제기")
    st.caption("2022 개정 교육과정")

    st.divider()

    # API 키 입력
    st.subheader("🔑 Gemini API 키")
    api_key = st.text_input(
        "API 키 입력",
        type="password",
        placeholder="AIza...",
        help="[Google AI Studio](https://aistudio.google.com/apikey)에서 무료 발급"
    )

    if api_key:
        if not st.session_state.api_connected:
            with st.spinner("연결 확인 중..."):
                try:
                    st.session_state.gemini = GeminiService(api_key)
                    if st.session_state.gemini.test_connection():
                        st.session_state.api_connected = True
                        st.success("✅ Gemini 연결 완료!")
                    else:
                        st.error("❌ 연결 실패 - API 키를 확인하세요")
                except Exception as e:
                    st.error(f"❌ 오류: {str(e)[:100]}")
        else:
            st.success("✅ Gemini 연결됨")
    else:
        st.session_state.api_connected = False
        st.info("👆 API 키를 입력하세요")

    st.divider()

    # 페이지 선택
    st.subheader("📌 메뉴")
    page = st.radio(
        "기능 선택",
        [
            "🏠 홈",
            "📸 이미지 → 유사 문항",
            "📝 수능형 자동 출제",
            "🔀 교차 단원 출제",
            "📊 출제 이력"
        ],
        label_visibility="collapsed"
    )

# ══════════════════════════════════════════════
#  🏠 홈 페이지
# ══════════════════════════════════════════════
if page == "🏠 홈":
    st.title("📝 통합사회 유사 문항 출제기")
    st.markdown("**2022 개정 교육과정** | 고등학교 통합사회1·2 | Gemini 2.5 기반")

    st.divider()

    # 기능 소개
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### 🎯 주요 기능
        | 기능 | 설명 |
        |------|------|
        | **📸 이미지→유사문항** | 문항 사진 업로드 → 유사 문항 2개 자동 생성 |
        | **📝 수능형 자동출제** | 단원·난이도 선택 → 수능 스타일 출제 |
        | **🔀 교차 단원 출제** | 이미지 문항 형태 + 다른 단원 내용 |
        | **📊 출제 이력** | 생성 기록 확인 |
        """)

    with col2:
        st.markdown("### 📖 지원 단원")

        t1, t2 = st.columns(2)
        with t1:
            st.markdown("**통합사회1**")
            for num, info in UNITS["통합사회1"].items():
                st.markdown(f"- {num}. {info['name']}")
        with t2:
            st.markdown("**통합사회2**")
            for num, info in UNITS["통합사회2"].items():
                st.markdown(f"- {num}. {info['name']}")

    st.divider()

    # 사용 방법
    st.markdown("""
    ### 🚀 시작하기
    1. 왼쪽 사이드바에서 **Gemini API 키**를 입력하세요
    2. 원하는 **기능 메뉴**를 선택하세요
    3. 문항을 생성하고 활용하세요!

    > 💡 **API 키 발급**: [Google AI Studio](https://aistudio.google.com/apikey) → 무료
    """)

# ══════════════════════════════════════════════
#  📸 이미지 → 유사 문항
# ══════════════════════════════════════════════
elif page == "📸 이미지 → 유사 문항":
    st.title("📸 이미지 → 유사 문항 생성")
    st.markdown("시험 문항 이미지를 업로드하면, 분석 후 **유사 문항 2개**를 생성합니다.")

    if not st.session_state.api_connected:
        st.warning("⚠️ 사이드바에서 Gemini API 키를 먼저 입력하세요.")
    else:
        uploaded = st.file_uploader(
            "문항 이미지를 업로드하세요",
            type=["png", "jpg", "jpeg", "webp"],
            help="시험지 사진, 캡처 이미지 등"
        )

        if uploaded:
            image = Image.open(uploaded)

            col_img, col_result = st.columns([1, 2])
            with col_img:
                st.image(image, caption="업로드된 문항", use_container_width=True)

            with col_result:
                if st.button("🚀 분석 & 유사 문항 생성", type="primary", use_container_width=True):
                    with st.spinner("🔍 Gemini가 문항을 분석 중입니다..."):
                        try:
                            result = st.session_state.gemini.analyze_and_generate_similar(image)
                            st.markdown(result)

                            # 이력 저장
                            st.session_state.sheets.save_history(
                                mode="이미지→유사문항",
                                unit="이미지 분석",
                                result=result
                            )
                            st.success("✅ 생성 완료! 출제 이력에 저장되었습니다.")
                        except Exception as e:
                            st.error(f"❌ 오류 발생: {str(e)[:200]}")

# ══════════════════════════════════════════════
#  📝 수능형 자동 출제
# ══════════════════════════════════════════════
elif page == "📝 수능형 자동 출제":
    st.title("📝 수능형 자동 출제")
    st.markdown("단원과 난이도를 선택하면 **수능 스타일 문항**을 자동 출제합니다.")

    if not st.session_state.api_connected:
        st.warning("⚠️ 사이드바에서 Gemini API 키를 먼저 입력하세요.")
    else:
        all_units = get_all_units_flat()

        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            selected_labels = st.multiselect(
                "📖 단원 선택 (복수 선택 가능)",
                options=[u["label"] for u in all_units],
                help="출제할 단원을 선택하세요"
            )
        with col2:
            difficulty = st.select_slider(
                "📊 난이도",
                options=["하", "중하", "중", "중상", "상"],
                value="중"
            )
        with col3:
            count = st.number_input("문항 수", min_value=1, max_value=5, value=2)

        if selected_labels:
            # 선택된 라벨에서 단원 번호 추출
            selected_nums = []
            for label in selected_labels:
                for u in all_units:
                    if u["label"] == label:
                        selected_nums.append(u["num"])

            # 선택된 단원의 성취기준 미리보기
            with st.expander("📋 선택된 단원 성취기준 보기"):
                for num in selected_nums:
                    info = get_unit_info(num)
                    if info:
                        st.markdown(f"**{num}. {info['name']}** ({info['subject']})")
                        st.markdown(f"키워드: `{'`, `'.join(info['keywords'])}`")
                        for s in info["standards"]:
                            st.markdown(f"- {s['code']}: {s['content']}")
                        st.markdown("")

            if st.button("🚀 문항 출제하기", type="primary", use_container_width=True):
                with st.spinner("📝 Gemini가 문항을 출제 중입니다..."):
                    try:
                        result = st.session_state.gemini.generate_exam(
                            unit_nums=selected_nums,
                            difficulty=difficulty,
                            count=count
                        )
                        st.markdown(result)

                        unit_names = ", ".join(selected_labels)
                        st.session_state.sheets.save_history(
                            mode="수능형 자동출제",
                            unit=unit_names,
                            result=result
                        )
                        st.success("✅ 출제 완료! 출제 이력에 저장되었습니다.")
                    except Exception as e:
                        st.error(f"❌ 오류 발생: {str(e)[:200]}")
        else:
            st.info("👆 출제할 단원을 선택하세요")

# ══════════════════════════════════════════════
#  🔀 교차 단원 출제
# ══════════════════════════════════════════════
elif page == "🔀 교차 단원 출제":
    st.title("🔀 교차 단원 출제")
    st.markdown("업로드한 문항의 **형태(구조)**는 유지하고, **다른 단원의 내용**으로 문항을 생성합니다.")

    if not st.session_state.api_connected:
        st.warning("⚠️ 사이드바에서 Gemini API 키를 먼저 입력하세요.")
    else:
        all_units = get_all_units_flat()

        col_up, col_set = st.columns([1, 1])

        with col_up:
            uploaded = st.file_uploader(
                "원본 문항 이미지 업로드",
                type=["png", "jpg", "jpeg", "webp"],
                key="cross_upload"
            )
            if uploaded:
                image = Image.open(uploaded)
                st.image(image, caption="원본 문항", use_container_width=True)

        with col_set:
            target_label = st.selectbox(
                "🎯 타겟 단원 선택",
                options=[u["label"] for u in all_units],
                help="이 단원의 내용으로 문항이 변환됩니다"
            )

            # 타겟 단원 정보 표시
            if target_label:
                target_num = None
                for u in all_units:
                    if u["label"] == target_label:
                        target_num = u["num"]
                        break

                if target_num:
                    info = get_unit_info(target_num)
                    if info:
                        st.markdown(f"""
                        **타겟 단원 정보**
                        - **과목**: {info['subject']}
                        - **단원**: {target_num}. {info['name']}
                        - **키워드**: {', '.join(info['keywords'])}
                        """)

        if uploaded and target_label:
            if st.button("🚀 교차 단원 문항 생성", type="primary", use_container_width=True):
                with st.spinner("🔀 Gemini가 교차 단원 문항을 생성 중입니다..."):
                    try:
                        result = st.session_state.gemini.cross_unit_generate(
                            image=image,
                            target_unit_num=target_num
                        )
                        st.markdown(result)

                        st.session_state.sheets.save_history(
                            mode="교차 단원 출제",
                            unit=target_label,
                            result=result
                        )
                        st.success("✅ 생성 완료! 출제 이력에 저장되었습니다.")
                    except Exception as e:
                        st.error(f"❌ 오류 발생: {str(e)[:200]}")
        elif not uploaded:
            st.info("👆 원본 문항 이미지를 업로드하세요")

# ══════════════════════════════════════════════
#  📊 출제 이력
# ══════════════════════════════════════════════
elif page == "📊 출제 이력":
    st.title("📊 출제 이력")
    st.markdown("지금까지 생성한 문항 이력을 확인할 수 있습니다.")

    history = st.session_state.sheets.get_history()

    if not history:
        st.info("📭 아직 출제 이력이 없습니다. 문항을 생성해 보세요!")
    else:
        st.markdown(f"**총 {len(history)}건**의 출제 이력")

        for i, entry in enumerate(history):
            with st.expander(
                f"📄 [{entry['mode']}] {entry['unit']} — {entry['timestamp']}"
            ):
                st.markdown(entry["result"])

        # 이력 초기화 버튼
        st.divider()
        if st.button("🗑️ 이력 전체 삭제", type="secondary"):
            st.session_state.sheets.history = []
            st.rerun()

# ══════════════════════════════════════════════
#  푸터
# ══════════════════════════════════════════════
st.divider()
st.caption("📝 통합사회 유사 문항 출제기 v2.0 | 2022 개정 교육과정 | Powered by Gemini 2.5")
