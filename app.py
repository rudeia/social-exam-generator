import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import time

# ============================================
# 페이지 설정
# ============================================
st.set_page_config(
    page_title="통합사회 유사 문항 출제기",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# 성취기준 데이터베이스 (2022 개정 교육과정)
# ============================================
CURRICULUM_DB = [
    {
        "id": "[10통사01-01]",
        "unit": "Ⅰ. 통합적 관점",
        "subject": "통합사회1",
        "standard": "사회적 존재로서의 인간이 공동체 내에서 살아가기 위해 다양한 방식으로 시간적, 공간적, 사회적, 윤리적 관점에서 탐구해 왔음을 조사한다.",
        "core_idea": "인간은 다양한 관점에서 사회를 탐구해옴",
        "knowledge": "인간의 사회적 존재 의미, 통합적 관점의 필요성",
        "process_value": "사회적 관점에서 탐구하는 능력",
        "explanation": "다양한 관점을 통합하여 사회 현상을 이해하는 것의 중요성을 다룸",
        "consideration": "학생들이 일상생활에서 통합적 관점의 사례를 찾을 수 있도록 지도",
        "ai_guide": "통합적 관점에서 사회 현상을 분석하는 문항. 시간적/공간적/사회적/윤리적 관점을 종합적으로 다룰 것."
    },
    {
        "id": "[10통사01-02]",
        "unit": "Ⅰ. 통합적 관점",
        "subject": "통합사회1",
        "standard": "시간적, 공간적, 사회적, 윤리적 관점의 특징을 이해하고, 이를 통합적으로 적용하여 사회 현상을 탐구한다.",
        "core_idea": "통합적 관점을 적용한 사회 현상 탐구",
        "knowledge": "시간적, 공간적, 사회적, 윤리적 관점의 특징과 통합적 적용",
        "process_value": "통합적 관점 적용 능력, 다각적 분석 태도",
        "explanation": "각 관점의 고유한 특징을 이해하고 이를 통합하여 하나의 사회 현상을 다양하게 분석",
        "consideration": "하나의 사회 현상을 네 가지 관점에서 분석하는 활동 권장",
        "ai_guide": "하나의 사회 현상에 대해 시간적/공간적/사회적/윤리적 관점을 통합 적용하는 문항 출제. 자료 분석형 권장."
    },
    {
        "id": "[10통사02-01]",
        "unit": "Ⅱ. 인간, 사회, 환경과 행복",
        "subject": "통합사회1",
        "standard": "행복의 의미와 기준은 시대와 지역에 따라 변화해 왔음을 이해하고, 자신의 행복의 기준을 성찰한다.",
        "core_idea": "행복의 의미와 기준의 시대적/지역적 변화",
        "knowledge": "행복의 다양한 의미, 시대별/지역별 행복 기준 변화",
        "process_value": "자신의 행복 기준 성찰, 다양성 존중",
        "explanation": "행복이 보편적이면서도 상대적 개념임을 이해",
        "consideration": "동서양의 다양한 행복관을 비교하며 학생 스스로의 행복관 성찰 유도",
        "ai_guide": "시대별/지역별 행복관 비교 문항. 동양과 서양, 과거와 현재의 행복 기준 차이를 자료로 제시."
    },
    {
        "id": "[10통사02-02]",
        "unit": "Ⅱ. 인간, 사회, 환경과 행복",
        "subject": "통합사회1",
        "standard": "자연환경과 사회 환경이 인간의 생활과 행복에 미치는 영향을 탐구한다.",
        "core_idea": "자연환경과 사회 환경이 행복에 미치는 영향",
        "knowledge": "자연환경과 사회환경의 특성, 환경이 삶의 질에 미치는 영향",
        "process_value": "환경과 인간 생활의 관계 탐구 능력",
        "explanation": "인간의 행복이 자연환경(기후, 지형 등)과 사회환경(제도, 문화 등)에 영향 받음을 이해",
        "consideration": "구체적 사례(도시/농촌, 열대/한대 등)를 통해 환경과 행복의 관계 탐구",
        "ai_guide": "자연환경(기후, 지형)과 사회환경(제도, 문화)이 행복에 미치는 영향을 비교하는 자료 분석형 문항."
    },
    {
        "id": "[10통사02-03]",
        "unit": "Ⅱ. 인간, 사회, 환경과 행복",
        "subject": "통합사회1",
        "standard": "삶의 질을 향상시키기 위한 다양한 조건을 탐색하고, 행복한 삶을 위한 개인적, 사회적 방안을 모색한다.",
        "core_idea": "삶의 질 향상 조건과 행복 방안 모색",
        "knowledge": "삶의 질 지표(경제적, 사회적 등), 행복 증진 방안",
        "process_value": "삶의 질 향상 방안 모색 능력, 실천 의지",
        "explanation": "경제적 조건 외에 사회적 관계, 건강, 여가 등 다양한 행복 조건 탐색",
        "consideration": "국가별 행복지수, 삶의 질 지표 등 구체적 통계 자료 활용 권장",
        "ai_guide": "삶의 질 지표(행복지수, GDP, 기대수명 등)를 비교하는 통계 자료 분석형 문항 출제."
    },
    {
        "id": "[10통사03-01]",
        "unit": "Ⅲ. 자연환경과 인간",
        "subject": "통합사회1",
        "standard": "지구적 차원의 기후 변화가 인간의 생활에 미치는 영향을 조사하고, 기후 변화에 적응하거나 대응하기 위한 개인적, 사회적 방안을 모색한다.",
        "core_idea": "기후 변화의 영향과 대응 방안",
        "knowledge": "기후 변화의 원인과 영향, 적응 및 대응 방안",
        "process_value": "기후 변화 대응 방안 모색, 환경 의식",
        "explanation": "기후 변화로 인한 생태계, 농업, 건강 등의 변화와 대응 전략",
        "consideration": "최신 기후 변화 데이터와 국제 협약 사례 활용",
        "ai_guide": "기후 변화 관련 그래프/통계 자료를 제시하고 영향과 대응 방안을 분석하는 문항."
    },
    {
        "id": "[10통사03-02]",
        "unit": "Ⅲ. 자연환경과 인간",
        "subject": "통합사회1",
        "standard": "자연환경과 인간 생활의 관계를 탐구하고, 자연재해에 대한 대응 방안을 모색한다.",
        "core_idea": "자연환경과 인간 생활, 자연재해 대응",
        "knowledge": "다양한 자연재해의 특성, 피해와 대응 방안",
        "process_value": "자연재해 대응 능력, 안전 의식",
        "explanation": "지진, 홍수, 태풍 등 자연재해가 인간 생활에 미치는 영향과 대비 방안",
        "consideration": "실제 자연재해 사례를 통한 탐구 활동 권장",
        "ai_guide": "자연재해 유형별 특성과 대응 방안을 비교하는 문항. 사례 기반 자료 활용."
    },
    {
        "id": "[10통사03-03]",
        "unit": "Ⅲ. 자연환경과 인간",
        "subject": "통합사회1",
        "standard": "환경 문제의 발생 원인을 자연적, 인위적 측면에서 분석하고, 지속 가능한 환경을 위한 해결 방안을 제안한다.",
        "core_idea": "환경 문제의 원인과 지속 가능한 해결 방안",
        "knowledge": "환경 문제의 자연적/인위적 원인, 지속 가능한 발전",
        "process_value": "환경 문제 분석 및 해결 방안 제안 능력",
        "explanation": "환경 오염, 생태계 파괴 등의 원인을 다각적으로 분석하고 해결책 모색",
        "consideration": "지역 및 글로벌 환경 문제를 균형있게 다룰 것",
        "ai_guide": "환경 문제의 원인(자연적/인위적)을 분석하고 해결 방안을 제안하는 서술형 또는 선택형 문항."
    },
    {
        "id": "[10통사04-01]",
        "unit": "Ⅳ. 문화와 다양성",
        "subject": "통합사회1",
        "standard": "문화의 의미와 특징을 이해하고, 문화가 인간의 삶에 미치는 영향을 탐구한다.",
        "core_idea": "문화의 의미, 특징과 삶에 미치는 영향",
        "knowledge": "문화의 개념(넓은 의미/좁은 의미), 문화의 속성(학습성, 공유성, 축적성, 변동성, 총체성)",
        "process_value": "문화 이해 능력, 문화 감수성",
        "explanation": "문화의 보편성과 특수성을 이해하고 일상에서 문화의 영향력 파악",
        "consideration": "학생들의 일상적 문화 경험을 출발점으로 활용",
        "ai_guide": "문화의 속성(학습성, 공유성, 축적성, 변동성, 총체성)을 사례와 연결하는 문항 출제."
    },
    {
        "id": "[10통사04-02]",
        "unit": "Ⅳ. 문화와 다양성",
        "subject": "통합사회1",
        "standard": "문화 변동의 다양한 양상을 이해하고, 현대 사회에서 전통문화가 갖는 의의를 파악한다.",
        "core_idea": "문화 변동과 전통문화의 의의",
        "knowledge": "문화 변동의 요인(발명, 발견, 전파), 문화 접변(동화, 병존, 융합), 전통문화의 의의",
        "process_value": "문화 변동 분석 능력, 전통문화 존중",
        "explanation": "문화가 변화하는 다양한 양상과 전통문화의 현대적 가치 이해",
        "consideration": "한국 전통문화의 현대적 계승 사례 활용",
        "ai_guide": "문화 변동 요인(발명/발견/전파)과 문화 접변(동화/병존/융합)을 구분하는 사례 분석형 문항."
    },
    {
        "id": "[10통사04-03]",
        "unit": "Ⅳ. 문화와 다양성",
        "subject": "통합사회1",
        "standard": "문화를 바라보는 여러 관점을 비교하고, 다문화 사회에서 나타나는 갈등 해결 및 문화적 다양성을 존중하는 태도를 갖는다.",
        "core_idea": "문화 이해 관점과 다문화 사회",
        "knowledge": "문화 이해 태도(문화 상대주의, 자문화 중심주의, 문화 사대주의), 다문화 갈등과 해결",
        "process_value": "문화 다양성 존중, 다문화 감수성",
        "explanation": "문화를 바라보는 다양한 관점의 장단점을 이해하고 다문화 공존 방안 모색",
        "consideration": "문화 상대주의의 한계(보편적 인권)도 함께 다룰 것",
        "ai_guide": "문화 이해 태도(상대주의/자문화중심주의/사대주의)를 구분하는 사례 제시형 문항. 다문화 갈등 해결 방안 포함."
    },
    {
        "id": "[10통사05-01]",
        "unit": "Ⅴ. 생활공간과 사회",
        "subject": "통합사회1",
        "standard": "산업화와 도시화로 인한 생활공간의 변화를 파악하고, 이에 따른 문제점과 해결 방안을 모색한다.",
        "core_idea": "산업화/도시화에 따른 생활공간 변화",
        "knowledge": "산업화와 도시화의 과정, 도시 문제(주거, 교통, 환경 등)",
        "process_value": "공간 변화 분석 능력, 문제 해결 능력",
        "explanation": "산업화와 도시화가 촌락과 도시의 생활공간에 미친 영향 분석",
        "consideration": "한국의 산업화/도시화 과정과 관련 통계 활용",
        "ai_guide": "도시화율 그래프, 인구 이동 자료 등을 활용한 산업화/도시화 관련 자료 분석형 문항."
    },
    {
        "id": "[10통사05-02]",
        "unit": "Ⅴ. 생활공간과 사회",
        "subject": "통합사회1",
        "standard": "교통·통신의 발달로 인한 생활공간의 변화를 이해하고, 공간 불평등 해소 방안을 모색한다.",
        "core_idea": "교통·통신 발달과 공간 불평등",
        "knowledge": "교통·통신 발달에 따른 생활 변화, 공간 불평등의 의미와 사례",
        "process_value": "공간 불평등 인식, 해결 방안 모색 능력",
        "explanation": "교통·통신 발달이 시간-공간 압축을 가져오고, 지역 간 격차 문제 발생",
        "consideration": "도시-농촌 간 격차, 교통 접근성 차이 등 구체적 사례 활용",
        "ai_guide": "교통·통신 발달에 따른 공간 변화와 공간 불평등 사례를 분석하는 자료 활용형 문항."
    },
    {
        "id": "[10통사05-03]",
        "unit": "Ⅴ. 생활공간과 사회",
        "subject": "통합사회1",
        "standard": "생활공간에서 나타나는 다양한 문제를 파악하고, 공간적 관점에서 해결 방안을 탐색한다.",
        "core_idea": "생활공간의 문제와 해결 방안",
        "knowledge": "생활공간의 다양한 문제(환경, 교통, 주거 등), 공간적 해결 방안",
        "process_value": "공간적 사고력, 문제 해결 의지",
        "explanation": "일상 생활공간에서 발생하는 문제를 공간적 관점에서 분석하고 해결",
        "consideration": "학생 주변의 생활공간 문제를 탐구 주제로 활용",
        "ai_guide": "생활공간의 구체적 문제 상황을 제시하고 공간적 해결 방안을 묻는 문항."
    },
    {
        "id": "[10통사06-01]",
        "unit": "Ⅵ. 인권 보장과 헌법",
        "subject": "통합사회2",
        "standard": "인권의 의미와 변화 양상을 이해하고, 인권이 헌법에 보장된 기본권으로 구체화됨을 탐구한다.",
        "core_idea": "인권의 의미와 헌법적 보장",
        "knowledge": "인권의 의미와 발전 과정, 기본권의 종류와 내용",
        "process_value": "인권 감수성, 기본권 이해",
        "explanation": "인권 사상의 발전 과정과 헌법상 기본권으로의 구체화 과정 이해",
        "consideration": "세계인권선언, 헌법 조문 등 실제 자료 활용",
        "ai_guide": "인권의 발전 과정(자유권→참정권→사회권)과 헌법상 기본권을 연결하는 문항. 헌법 조문 자료 활용."
    },
    {
        "id": "[10통사06-02]",
        "unit": "Ⅵ. 인권 보장과 헌법",
        "subject": "통합사회2",
        "standard": "인권 침해 사례를 분석하고, 국가 기관에 의한 구제 방법을 탐색한다.",
        "core_idea": "인권 침해와 구제 방법",
        "knowledge": "인권 침해 유형, 국가인권위원회, 헌법재판소, 법원 등의 구제 기관",
        "process_value": "인권 침해 인식 및 구제 방법 탐색 능력",
        "explanation": "일상생활에서 발생하는 인권 침해 사례와 이를 구제하는 제도적 방법",
        "consideration": "실제 판례나 사례를 통한 구체적 학습 권장",
        "ai_guide": "인권 침해 사례를 제시하고 적절한 구제 기관과 방법을 찾는 사례 분석형 문항."
    },
    {
        "id": "[10통사06-03]",
        "unit": "Ⅵ. 인권 보장과 헌법",
        "subject": "통합사회2",
        "standard": "사회적 소수자의 인권 문제를 이해하고, 이를 해결하기 위한 방안을 모색한다.",
        "core_idea": "사회적 소수자 인권과 해결 방안",
        "knowledge": "사회적 소수자의 의미, 차별 유형, 적극적 우대 조치",
        "process_value": "소수자 인권 감수성, 차별 해소 의지",
        "explanation": "사회적 소수자가 겪는 차별과 편견을 이해하고 제도적/개인적 해결 방안 탐색",
        "consideration": "다양한 소수자 집단(장애인, 이주민, 성소수자 등)을 균형있게 다룸",
        "ai_guide": "사회적 소수자 차별 사례와 해결 방안(적극적 우대 조치 등)을 분석하는 문항."
    },
    {
        "id": "[10통사07-01]",
        "unit": "Ⅶ. 사회정의와 불평등",
        "subject": "통합사회2",
        "standard": "정의의 의미와 실질적 기준을 탐구하고, 정의로운 사회를 만들기 위한 다양한 관점을 비교한다.",
        "core_idea": "정의의 의미와 정의로운 사회의 조건",
        "knowledge": "정의의 의미, 분배 정의의 기준(업적, 필요, 능력 등), 롤스/노직 등의 관점",
        "process_value": "정의에 대한 비판적 사고, 공정성 인식",
        "explanation": "다양한 정의관을 비교하며 정의로운 사회의 조건 탐구",
        "consideration": "학생들이 공감할 수 있는 일상적 사례로 시작하여 철학적 논의로 확장",
        "ai_guide": "분배 정의의 다양한 기준(업적/필요/능력)을 비교하는 사례 제시형 문항. 롤스와 노직의 관점 비교 포함."
    },
    {
        "id": "[10통사07-02]",
        "unit": "Ⅶ. 사회정의와 불평등",
        "subject": "통합사회2",
        "standard": "다양한 불평등 현상의 원인과 영향을 분석하고, 이를 해결하기 위한 방안을 탐색한다.",
        "core_idea": "사회 불평등의 원인과 해결 방안",
        "knowledge": "사회 불평등의 유형(경제적, 사회적, 문화적), 불평등의 원인과 영향",
        "process_value": "불평등 인식 및 해결 방안 모색 능력",
        "explanation": "소득 불평등, 교육 불평등, 정보 격차 등 다양한 불평등 현상 분석",
        "consideration": "통계 자료(지니계수, 소득 5분위 배율 등) 활용 권장",
        "ai_guide": "소득 불평등 통계(지니계수, 5분위 배율 등)를 분석하고 해결 방안을 묻는 자료 분석형 문항."
    },
    {
        "id": "[10통사07-03]",
        "unit": "Ⅶ. 사회정의와 불평등",
        "subject": "통합사회2",
        "standard": "사회 및 공간 불평등 현상을 다양한 지역의 사례를 통해 분석하고, 정의로운 사회를 위한 제도적 방안을 모색한다.",
        "core_idea": "공간 불평등과 제도적 해결 방안",
        "knowledge": "공간 불평등의 사례, 정의로운 사회를 위한 제도(복지, 조세 등)",
        "process_value": "공간 불평등 인식, 제도적 해결 방안 모색",
        "explanation": "지역 간 격차와 공간 불평등을 분석하고 이를 해소하기 위한 정책 탐구",
        "consideration": "국내외 공간 불평등 사례를 균형있게 다룸",
        "ai_guide": "지역 간 불평등 사례(도시-농촌, 국가 간)를 자료로 제시하고 해결 방안을 묻는 문항."
    },
    {
        "id": "[10통사08-01]",
        "unit": "Ⅷ. 시장경제와 지속가능발전",
        "subject": "통합사회2",
        "standard": "시장 경제의 원리와 이를 뒷받침하는 사회적 조건을 탐구한다.",
        "core_idea": "시장 경제의 원리와 사회적 조건",
        "knowledge": "시장 경제의 기본 원리(수요-공급, 가격), 시장 경제의 사회적 조건(재산권, 계약 자유 등)",
        "process_value": "경제적 사고력, 시장 원리 이해",
        "explanation": "시장 경제가 작동하기 위한 기본 원리와 제도적 조건 이해",
        "consideration": "시장 경제의 장점과 한계를 균형있게 다룸",
        "ai_guide": "수요-공급 그래프, 가격 결정 원리를 활용한 자료 분석형 문항. 시장 실패 사례 포함 가능."
    },
    {
        "id": "[10통사08-02]",
        "unit": "Ⅷ. 시장경제와 지속가능발전",
        "subject": "통합사회2",
        "standard": "합리적 선택을 위한 비용-편익 분석 방법을 이해하고, 이를 실생활에 적용한다.",
        "core_idea": "합리적 선택과 비용-편익 분석",
        "knowledge": "기회비용, 매몰비용, 비용-편익 분석, 합리적 선택",
        "process_value": "합리적 의사결정 능력, 경제적 사고",
        "explanation": "일상생활에서의 합리적 선택을 비용-편익 분석으로 설명",
        "consideration": "학생 생활과 밀접한 사례(진로, 소비 등)를 활용",
        "ai_guide": "기회비용과 편익을 비교하는 표/사례를 제시하고 합리적 선택을 묻는 문항. 매몰비용 개념 포함."
    },
    {
        "id": "[10통사08-03]",
        "unit": "Ⅷ. 시장경제와 지속가능발전",
        "subject": "통합사회2",
        "standard": "경제 성장과 환경 보전의 조화를 위한 지속 가능한 발전 방안을 탐색한다.",
        "core_idea": "경제 성장과 환경의 조화, 지속 가능 발전",
        "knowledge": "지속 가능한 발전의 의미, 경제 성장과 환경 보전의 관계",
        "process_value": "지속 가능성 인식, 미래 세대에 대한 책임감",
        "explanation": "경제 발전과 환경 보전 사이의 갈등을 인식하고 조화로운 발전 방안 모색",
        "consideration": "ESG, 탄소 중립 등 최신 이슈 연계",
        "ai_guide": "경제 성장률과 환경 지표를 함께 제시하고 지속 가능한 발전 방안을 묻는 문항."
    },
    {
        "id": "[10통사09-01]",
        "unit": "Ⅸ. 세계화와 평화",
        "subject": "통합사회2",
        "standard": "세계화의 양상을 파악하고, 세계화로 인한 문제를 해결하기 위한 방안을 모색한다.",
        "core_idea": "세계화의 양상과 문제 해결",
        "knowledge": "세계화의 의미와 양상(경제적, 문화적, 정치적), 세계화의 긍정적/부정적 영향",
        "process_value": "세계 시민 의식, 글로벌 문제 해결 능력",
        "explanation": "세계화가 가져온 기회와 도전을 균형있게 이해",
        "consideration": "세계화의 긍정적 측면과 부정적 측면을 균형있게 다룸",
        "ai_guide": "세계화의 다양한 양상(경제/문화/정치)과 긍정적/부정적 영향을 비교하는 자료 분석형 문항."
    },
    {
        "id": "[10통사09-02]",
        "unit": "Ⅸ. 세계화와 평화",
        "subject": "통합사회2",
        "standard": "국제 사회의 다양한 행위 주체의 역할을 이해하고, 국제 사회의 공존을 위한 노력을 탐구한다.",
        "core_idea": "국제 사회 행위 주체와 공존 노력",
        "knowledge": "국제기구(UN, WTO 등), NGO, 다국적 기업 등의 역할",
        "process_value": "국제 협력 의식, 평화적 공존 태도",
        "explanation": "국제 사회를 구성하는 다양한 주체들의 역할과 협력 이해",
        "consideration": "최신 국제 이슈와 연계하여 국제기구의 역할 탐구",
        "ai_guide": "국제기구/NGO/다국적 기업의 역할을 구분하는 사례 제시형 문항. 국제 협력 사례 활용."
    },
    {
        "id": "[10통사09-03]",
        "unit": "Ⅸ. 세계화와 평화",
        "subject": "통합사회2",
        "standard": "남북 분단의 배경과 분단이 미친 영향을 이해하고, 평화 통일을 위한 노력을 탐구한다.",
        "core_idea": "남북 분단과 평화 통일",
        "knowledge": "남북 분단의 배경, 분단의 영향, 통일 편익과 비용, 평화 통일 노력",
        "process_value": "통일 의식, 평화적 문제 해결 태도",
        "explanation": "분단의 역사적 배경과 현실적 영향을 이해하고 평화적 통일 방안 탐구",
        "consideration": "통일 비용과 편익을 균형있게 다루고, 평화적 접근 강조",
        "ai_guide": "남북 분단의 영향과 통일 비용/편익을 분석하는 자료 활용형 문항. 평화 통일 방안 포함."
    },
    {
        "id": "[10통사10-01]",
        "unit": "Ⅹ. 미래와 지속 가능한 삶",
        "subject": "통합사회2",
        "standard": "과학 기술의 발전에 따른 사회 변화를 예측하고, 이에 따른 윤리적 문제를 탐구한다.",
        "core_idea": "과학 기술 발전과 윤리적 문제",
        "knowledge": "4차 산업혁명, AI, 생명공학 등의 사회적 영향, 기술 윤리",
        "process_value": "미래 사회 예측 능력, 기술 윤리 의식",
        "explanation": "과학 기술 발전이 가져올 사회 변화와 윤리적 쟁점 탐구",
        "consideration": "AI, 빅데이터, 생명공학 등 최신 기술 이슈 반영",
        "ai_guide": "AI/생명공학 등 과학 기술 발전 사례를 제시하고 윤리적 쟁점을 분석하는 문항."
    },
    {
        "id": "[10통사10-02]",
        "unit": "Ⅹ. 미래와 지속 가능한 삶",
        "subject": "통합사회2",
        "standard": "세계의 인구, 식량, 자원 문제를 이해하고, 지속 가능한 발전을 위한 개인적, 사회적 노력을 모색한다.",
        "core_idea": "인구/식량/자원 문제와 지속 가능한 발전",
        "knowledge": "인구 문제(고령화, 인구 폭발), 식량 문제, 자원 고갈, 지속 가능한 발전",
        "process_value": "지속 가능성 인식, 글로벌 문제 해결 의지",
        "explanation": "세계적 차원의 인구, 식량, 자원 문제를 이해하고 지속 가능한 해결 방안 모색",
        "consideration": "통계 자료를 활용한 객관적 분석과 가치 판단의 균형",
        "ai_guide": "인구 변화, 식량 생산, 자원 소비 통계를 활용한 자료 분석형 문항. 지속 가능 발전 방안 포함."
    },
    {
        "id": "[10통사10-03]",
        "unit": "Ⅹ. 미래와 지속 가능한 삶",
        "subject": "통합사회2",
        "standard": "미래 사회의 변화에 대응하기 위한 개인적, 사회적 역량을 탐구하고, 지속 가능한 삶을 위한 실천 방안을 모색한다.",
        "core_idea": "미래 대응 역량과 지속 가능한 삶",
        "knowledge": "미래 사회 변화 트렌드, 미래 역량, 지속 가능한 삶의 실천",
        "process_value": "미래 대응 능력, 지속 가능한 삶 실천 의지",
        "explanation": "미래 사회 변화에 능동적으로 대응하기 위한 역량과 실천 방안 탐색",
        "consideration": "학생들이 구체적으로 실천할 수 있는 방안 모색 유도",
        "ai_guide": "미래 사회 변화 트렌드를 제시하고 대응 역량과 실천 방안을 묻는 문항."
    }
]

# ============================================
# API 키 로테이션 관리 (최대 5개)
# ============================================
class APIKeyManager:
    """여러 Gemini API 키를 로테이션하며 사용 (최대 5개)"""

    def __init__(self):
        self.keys = []
        self.current_index = 0
        self.failed_keys = set()

    def set_keys(self, keys_list):
        """키 리스트 등록"""
        self.keys = [k for k in keys_list if k and len(k.strip()) > 10]
        self.current_index = 0
        self.failed_keys = set()
        return len(self.keys)

    def get_current_key(self):
        """현재 사용할 키 반환"""
        if not self.keys:
            return None
        available = [k for k in self.keys if k not in self.failed_keys]
        if not available:
            self.failed_keys = set()
            available = self.keys
        return available[self.current_index % len(available)]

    def mark_failed(self, key):
        """현재 키를 실패로 표시하고 다음 키로 이동"""
        self.failed_keys.add(key)
        self.current_index += 1

    def get_status(self):
        """현재 키 상태 반환"""
        total = len(self.keys)
        failed = len(self.failed_keys)
        active = total - failed
        return total, active, failed

if 'key_manager' not in st.session_state:
    st.session_state.key_manager = APIKeyManager()

# ============================================
# 유틸리티 함수
# ============================================
def get_units():
    """대단원 목록 반환"""
    units = []
    seen = set()
    for item in CURRICULUM_DB:
        if item["unit"] not in seen:
            units.append({"unit": item["unit"], "subject": item["subject"]})
            seen.add(item["unit"])
    return units

def get_standards_by_unit(unit_name):
    """특정 대단원의 성취기준 목록 반환"""
    return [item for item in CURRICULUM_DB if item["unit"] == unit_name]

def get_standard_by_id(std_id):
    """성취기준 ID로 검색"""
    for item in CURRICULUM_DB:
        if item["id"] == std_id:
            return item
    return None

# ============================================
# Gemini API 호출 (자동 키 로테이션)
# ============================================
def call_gemini_api(prompt, image=None, max_retries=None):
    """Gemini API 호출 - 실패 시 자동으로 다음 키로 전환"""
    km = st.session_state.key_manager

    if not km.keys:
        return None, "API 키를 입력해주세요"

    if max_retries is None:
        max_retries = len(km.keys)

    last_error = ""

    for attempt in range(max_retries):
        current_key = km.get_current_key()
        if not current_key:
            return None, "사용 가능한 API 키가 없습니다"

        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel("gemini-2.5-flash")

            key_num = km.keys.index(current_key) + 1

            if image:
                response = model.generate_content([prompt, image])
            else:
                response = model.generate_content(prompt)

            st.toast(f"🔑 키 #{key_num} 사용 성공!", icon="✅")
            return response.text, None

        except Exception as e:
            error_msg = str(e)
            key_num = km.keys.index(current_key) + 1

            if any(keyword in error_msg.lower() for keyword in [
                '429', 'quota', 'rate limit', 'resource exhausted',
                'too many requests', 'limit'
            ]):
                st.warning(f"⚠️ 키 #{key_num} 용량 초과 → 다음 키로 전환 중...")
                km.mark_failed(current_key)
                last_error = f"키 #{key_num} 용량 초과"
                time.sleep(1)
                continue

            elif any(keyword in error_msg.lower() for keyword in [
                '401', '403', 'invalid', 'api_key'
            ]):
                st.warning(f"⚠️ 키 #{key_num} 인증 실패 → 다음 키로 전환 중...")
                km.mark_failed(current_key)
                last_error = f"키 #{key_num} 인증 실패"
                continue

            else:
                return None, f"오류 발생: {error_msg}"

    return None, f"모든 키 소진! ({last_error}). 잠시 후 다시 시도하거나 새 API 키를 추가해주세요."

# ============================================
# 프롬프트 생성 함수
# ============================================
def build_similar_prompt(std_info=None):
    """이미지 기반 유사 문항 생성 프롬프트"""
    base = """당신은 대한민국 고등학교 통합사회 시험 문항 출제 전문가입니다.

업로드된 시험 문항 이미지를 분석한 후, 유사한 형태와 난이도의 문항을 2개 생성하세요.

[출제 규칙]
1. 원본 문항의 형식(5지선다, 표/그래프 활용 등)을 유지
2. 원본과 동일한 성취기준/학습 내용 범위
3. 숫자, 보기, 선지를 변경하여 새로운 문항 생성
4. 각 문항에 정답과 간단한 해설 포함
5. 2022 개정 교육과정 기준"""

    if std_info:
        base += f"""

[관련 성취기준 정보]
- 성취기준: {std_info['id']} {std_info['standard']}
- 핵심 아이디어: {std_info['core_idea']}
- 지식·이해: {std_info['knowledge']}
- 출제 가이드: {std_info['ai_guide']}
- 고려사항: {std_info['consideration']}"""

    base += """

[출력 형식]
---
### 유사 문항 1
(문항 내용)

**정답:** 
**해설:** 

---
### 유사 문항 2
(문항 내용)

**정답:** 
**해설:** 
---"""
    return base

def build_auto_prompt(std_info, difficulty="중", question_type="5지선다형"):
    """성취기준 기반 자동 출제 프롬프트"""
    return f"""당신은 대한민국 고등학교 통합사회 시험 문항 출제 전문가입니다.

아래 성취기준에 맞는 {question_type} 문항을 2개 출제하세요.

[성취기준 정보]
- 성취기준 코드: {std_info['id']}
- 성취기준: {std_info['standard']}
- 대단원: {std_info['unit']}
- 핵심 아이디어: {std_info['core_idea']}
- 지식·이해: {std_info['knowledge']}
- 과정·기능/가치·태도: {std_info['process_value']}
- 해설: {std_info['explanation']}

[출제 가이드]
{std_info['ai_guide']}

[고려사항]
{std_info['consideration']}

[출제 조건]
- 난이도: {difficulty}
- 문항 유형: {question_type}
- 2022 개정 교육과정 기준
- 각 문항에 정답과 상세 해설 포함
- 표, 그래프, 사례 등 자료를 적극 활용

[출력 형식]
---
### 문항 1
(문항 내용 - 자료/표/그래프 설명 포함)

① 
② 
③ 
④ 
⑤ 

**정답:** 
**해설:** 

---
### 문항 2
(문항 내용 - 자료/표/그래프 설명 포함)

① 
② 
③ 
④ 
⑤ 

**정답:** 
**해설:** 
---"""

def build_cross_prompt(image_std_info, target_std_info):
    """교차 단원 출제 프롬프트"""
    return f"""당신은 대한민국 고등학교 통합사회 시험 문항 출제 전문가입니다.

업로드된 이미지의 문항 형식을 참고하되, 아래 성취기준의 내용으로 새로운 문항을 2개 출제하세요.

[이미지 문항의 형식을 참고]
- 문항 유형, 자료 형태, 선지 구성 방식을 참고하세요

[출제할 성취기준]
- 성취기준 코드: {target_std_info['id']}
- 성취기준: {target_std_info['standard']}
- 대단원: {target_std_info['unit']}
- 핵심 아이디어: {target_std_info['core_idea']}
- 지식·이해: {target_std_info['knowledge']}
- 출제 가이드: {target_std_info['ai_guide']}
- 고려사항: {target_std_info['consideration']}

[출제 조건]
- 이미지 문항의 형식(표, 그래프, 지도 등)을 최대한 활용
- 내용은 반드시 위 성취기준 범위에서 출제
- 2022 개정 교육과정 기준
- 각 문항에 정답과 상세 해설 포함

[출력 형식]
---
### 교차 출제 문항 1
(문항 내용)

**정답:** 
**해설:** 

---
### 교차 출제 문항 2
(문항 내용)

**정답:** 
**해설:** 
---"""

# ============================================
# 메인 UI
# ============================================
st.markdown("""
<h1 style='text-align: center;'>📚 통합사회 유사 문항 출제기</h1>
<p style='text-align: center; color: gray;'>2022 개정 교육과정 | 고등학교 통합사회 1·2 | Gemini AI 기반</p>
""", unsafe_allow_html=True)

# ============================================
# 사이드바 - API 키 입력 (최대 5개)
# ============================================
with st.sidebar:
    st.header("🔑 Gemini API 키 설정")

    st.markdown("**최대 5개 키 등록 → 자동 로테이션!**")
    st.caption("용량 초과 시 다음 키로 자동 전환됩니다")

    st.divider()

    api_keys = []
    for i in range(1, 6):
        key = st.text_input(
            f"API 키 #{i}" + (" (필수)" if i == 1 else " (선택)"),
            type="password",
            key=f"api_key_{i}",
            placeholder="AIzaSy..."
        )
        if key and len(key.strip()) > 10:
            api_keys.append(key.strip())

    # 키 등록
    if api_keys:
        count = st.session_state.key_manager.set_keys(api_keys)
        total, active, failed = st.session_state.key_manager.get_status()

        st.divider()

        col1, col2, col3 = st.columns(3)
        col1.metric("등록", f"{total}개")
        col2.metric("활성", f"{active}개")
        col3.metric("소진", f"{failed}개")

        if total >= 3:
            st.success(f"✅ {total}개 키 로테이션 모드!")
        elif total == 2:
            st.info(f"✅ {total}개 키 등록됨 (추가 권장)")
        elif total == 1:
            st.warning("⚠️ 키 1개만 등록됨 (추가 권장)")
    else:
        st.error("⬆️ API 키를 최소 1개 입력하세요")

    st.divider()
    st.markdown("### 💡 무료 키 만드는 법")
    st.markdown("""
    1. [aistudio.google.com](https://aistudio.google.com) 접속
    2. 구글 계정으로 로그인
    3. **Get API Key** → **Create**
    4. 다른 구글 계정으로 반복! (최대 5개)
    """)

    st.divider()
    st.markdown("### 📊 성취기준 DB 현황")
    st.markdown(f"- 전체 성취기준: **{len(CURRICULUM_DB)}개**")
    st.markdown(f"- 대단원: **{len(get_units())}개**")
    st.markdown("- 과목: **통합사회1·2**")

# ============================================
# 탭 구성
# ============================================
tab1, tab2, tab3 = st.tabs([
    "📸 이미지 → 유사 문항",
    "📝 성취기준별 자동 출제",
    "🔀 교차 단원 출제"
])

# ============================================
# 탭 1: 이미지 → 유사 문항
# ============================================
with tab1:
    st.markdown("### 📸 문항 이미지를 업로드하면 유사 문항 2개를 생성합니다")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("**문항 이미지 업로드**")
        uploaded_file = st.file_uploader(
            "문항 이미지를 선택하세요",
            type=["png", "jpg", "jpeg"],
            key="tab1_upload"
        )

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="업로드된 문항", use_container_width=True)

        # 성취기준 선택 (선택사항)
        st.markdown("**성취기준 지정 (선택사항)**")
        use_std = st.checkbox("특정 성취기준 지정", key="tab1_use_std")

        selected_std_info = None
        if use_std:
            units = get_units()
            unit_names = [u["unit"] for u in units]
            selected_unit = st.selectbox("대단원 선택", unit_names, key="tab1_unit")

            standards = get_standards_by_unit(selected_unit)
            std_options = [f"{s['id']} {s['standard'][:40]}..." for s in standards]
            selected_idx = st.selectbox("성취기준 선택", range(len(std_options)), format_func=lambda x: std_options[x], key="tab1_std")
            selected_std_info = standards[selected_idx]

    with col_right:
        if st.button("🚀 유사 문항 생성", use_container_width=True, type="primary", key="tab1_btn"):
            if not uploaded_file:
                st.error("❌ 이미지를 업로드해주세요")
            elif not st.session_state.key_manager.keys:
                st.error("❌ API 키를 입력해주세요")
            else:
                with st.spinner("🔄 AI가 문항을 분석하고 있습니다..."):
                    prompt = build_similar_prompt(selected_std_info)
                    result, error = call_gemini_api(prompt, image=image)

                    if error:
                        st.error(f"❌ {error}")
                    else:
                        st.success("✅ 유사 문항이 생성되었습니다!")
                        st.markdown(result)

# ============================================
# 탭 2: 성취기준별 자동 출제
# ============================================
with tab2:
    st.markdown("### 📝 성취기준을 선택하면 맞춤 문항을 자동 출제합니다")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        # 과목 선택
        subject = st.radio("과목 선택", ["통합사회1", "통합사회2"], horizontal=True, key="tab2_subject")

        # 대단원 선택
        units = get_units()
        filtered_units = [u for u in units if u["subject"] == subject]
        unit_names = [u["unit"] for u in filtered_units]
        selected_unit = st.selectbox("대단원 선택", unit_names, key="tab2_unit")

        # 성취기준 선택
        standards = get_standards_by_unit(selected_unit)

        for i, std in enumerate(standards):
            with st.expander(f"{std['id']} {std['standard'][:50]}...", expanded=False):
                st.markdown(f"**핵심 아이디어:** {std['core_idea']}")
                st.markdown(f"**지식·이해:** {std['knowledge']}")
                st.markdown(f"**해설:** {std['explanation']}")
                st.markdown(f"**고려사항:** {std['consideration']}")

        std_options = [f"{s['id']} {s['standard'][:50]}..." for s in standards]
        selected_std_idx = st.selectbox(
            "출제할 성취기준 선택",
            range(len(std_options)),
            format_func=lambda x: std_options[x],
            key="tab2_std"
        )
        selected_std = standards[selected_std_idx]

        # 난이도 & 유형
        col_d, col_t = st.columns(2)
        with col_d:
            difficulty = st.select_slider(
                "난이도",
                options=["하", "중하", "중", "중상", "상"],
                value="중",
                key="tab2_diff"
            )
        with col_t:
            q_type = st.selectbox(
                "문항 유형",
                ["5지선다형", "자료 분석형", "표/그래프 분석형", "사례 판단형", "비교 분석형"],
                key="tab2_type"
            )

    with col_right:
        # 선택된 성취기준 정보 표시
        st.markdown("#### 📋 선택된 성취기준 정보")
        st.info(f"""
        **{selected_std['id']}**

        {selected_std['standard']}
        """)
        st.markdown(f"**🎯 핵심:** {selected_std['core_idea']}")
        st.markdown(f"**📖 지식:** {selected_std['knowledge']}")
        st.markdown(f"**🤖 AI 가이드:** {selected_std['ai_guide']}")

        st.divider()

        if st.button("🚀 문항 자동 출제", use_container_width=True, type="primary", key="tab2_btn"):
            if not st.session_state.key_manager.keys:
                st.error("❌ API 키를 입력해주세요")
            else:
                with st.spinner("🔄 AI가 문항을 출제하고 있습니다..."):
                    prompt = build_auto_prompt(selected_std, difficulty, q_type)
                    result, error = call_gemini_api(prompt)

                    if error:
                        st.error(f"❌ {error}")
                    else:
                        st.success("✅ 문항이 출제되었습니다!")
                        st.markdown(result)

# ============================================
# 탭 3: 교차 단원 출제
# ============================================
with tab3:
    st.markdown("### 🔀 이미지 문항의 형식 + 다른 성취기준의 내용으로 출제합니다")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("**문항 이미지 업로드 (형식 참고용)**")
        uploaded_file_cross = st.file_uploader(
            "문항 이미지를 선택하세요",
            type=["png", "jpg", "jpeg"],
            key="tab3_upload"
        )

        if uploaded_file_cross:
            image_cross = Image.open(uploaded_file_cross)
            st.image(image_cross, caption="형식 참고 문항", use_container_width=True)

        st.markdown("**출제할 성취기준 선택**")

        subject_cross = st.radio("과목", ["통합사회1", "통합사회2"], horizontal=True, key="tab3_subject")

        units_cross = get_units()
        filtered_units_cross = [u for u in units_cross if u["subject"] == subject_cross]
        unit_names_cross = [u["unit"] for u in filtered_units_cross]
        selected_unit_cross = st.selectbox("대단원", unit_names_cross, key="tab3_unit")

        standards_cross = get_standards_by_unit(selected_unit_cross)
        std_options_cross = [f"{s['id']} {s['standard'][:50]}..." for s in standards_cross]
        selected_std_cross_idx = st.selectbox(
            "성취기준",
            range(len(std_options_cross)),
            format_func=lambda x: std_options_cross[x],
            key="tab3_std"
        )
        target_std = standards_cross[selected_std_cross_idx]

    with col_right:
        st.markdown("#### 📋 선택된 성취기준")
        st.info(f"""
        **{target_std['id']}**

        {target_std['standard']}
        """)
        st.markdown(f"**🎯 핵심:** {target_std['core_idea']}")
        st.markdown(f"**🤖 AI 가이드:** {target_std['ai_guide']}")

        st.divider()

        if st.button("🚀 교차 문항 출제", use_container_width=True, type="primary", key="tab3_btn"):
            if not uploaded_file_cross:
                st.error("❌ 이미지를 업로드해주세요")
            elif not st.session_state.key_manager.keys:
                st.error("❌ API 키를 입력해주세요")
            else:
                with st.spinner("🔄 AI가 교차 문항을 출제하고 있습니다..."):
                    prompt = build_cross_prompt(None, target_std)
                    result, error = call_gemini_api(prompt, image=image_cross)

                    if error:
                        st.error(f"❌ {error}")
                    else:
                        st.success("✅ 교차 문항이 출제되었습니다!")
                        st.markdown(result)

# ============================================
# 하단 정보
# ============================================
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.85em;'>
    📚 통합사회 유사 문항 출제기 v3 | 2022 개정 교육과정 | Gemini AI 기반<br>
    성취기준 30개 탑재 | API 키 로테이션 지원 (최대 5개)
</div>
""", unsafe_allow_html=True)
