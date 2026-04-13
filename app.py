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
        "id": "10통사1-01-01",
        "unit": "통합적 관점",
        "standard": "인간, 사회, 환경을 바라보는 시간적, 공간적, 사회적, 윤리적 관점의 의미와 특징을 사례를 통해 파악한다.",
        "core_idea": "시간적, 공간적, 사회적, 윤리적 측면을 함께 고려하는 통합적 관점의 적용을 통해 인간, 사회, 환경의 특성 및 관련 문제를 잘 파악할 수 있다.",
        "knowledge": "·통합적 관점 ·시간적 관점 ·공간적 관점 ·사회적 관점 ·윤리적 관점",
        "process_value": "(과정) 탐구 주제의 역사적 배경 조사하기 \n\n(가치) 시간적, 공간적, 사회적, 윤리적 차원의 다양한 쟁점에 관한 관심",
        "explanation": "인간과 세상을 이해하기 위해 역사적 배경과 시대적 맥락에 초점을 두는 시간적 관점, 장소와 지역 및 공간적 상호 작용에 중점을 두는 공간적 관점, 사회 구조 및 제도의 영향력에 초점을 두는 사회적 관점, 도덕적 가치와 규범을 고려하는 윤리적 관점 등을 다룬다.",
        "consideration": "인간, 사회, 환경에 대한 다양한 관점을 통합적으로 적용하는 것이 중요하며, 이는 통합사회 과목 각 영역을 관통하는 기본 원리임을 깨닫게 하는 데 중점을 둔다.",
        "ai_guide": "특정 사회 현상을 제시하고, 이를 4가지 관점(시간, 공간, 사회, 윤리) 중 하나로 올바르게 분석한 선택지를 고르도록 문항 구성."
    },
    {
        "id": "10통사1-01-02",
        "unit": "통합적 관점",
        "standard": "인간, 사회, 환경의 탐구에 통합적 관점이 요청되는 이유를 도출하고 이를 탐구에 적용한다.",
        "core_idea": "시간적, 공간적, 사회적, 윤리적 측면을 함께 고려하는 통합적 관점의 적용을 통해 인간, 사회, 환경의 특성 및 관련 문제를 잘 파악할 수 있다.",
        "knowledge": "·통합적 관점 ·시간적 관점 ·공간적 관점 ·사회적 관점 ·윤리적 관점",
        "process_value": "(과정) 통합적 관점에서 해결 방안을 도출하고 타당성 평가하기 \n\n(가치) 갈등 해결을 위한 타인과의 소통과 협력",
        "explanation": "현대 사회의 불확실하고 복잡한 사회현상에 대처하기 위해 시간적, 공간적, 사회적, 윤리적 측면을 함께 고려하는 통합적 관점의 중요성을 이해하고, 구체적인 사례를 중심으로 이를 탐구하게 한다.",
        "consideration": "통합적 관점이 요청되는 이유를 도출하는 과정에서 토의·토론 또는 협력학습을 적용할 수 있으며, 학습 활동 과정에서 학생 개인의 삶 또는 지역사회의 현상과 관련된 사례를 활용할 수 있도록 유도한다.",
        "ai_guide": "하나의 쟁점에 대해 다양한 관점의 주장이 섞인 제시문을 주고, 이를 통합적으로 고찰한 학생의 결론이나 대응 방안을 고르는 문항 구성."
    },
    {
        "id": "10통사1-02-01",
        "unit": "인간, 사회, 환경과 행복",
        "standard": "시대와 지역에 따라 다르게 나타나는 행복의 기준을 사례를 통해 비교하여 평가하고, 삶의 목적으로서 행복의 의미를 성찰한다.",
        "core_idea": "질 높은 정주 환경의 조성, 경제적 안정, 민주주의의 실현, 윤리적 실천은 행복한 삶을 위한 중요한 조건이다.",
        "knowledge": "행복의 의미, 행복의 조건",
        "process_value": "(과정) 주제와 관련된 다양한 가치를 통합적 관점에서 이해하고 가치 간의 관계 탐구하기 \n\n(가치) 타인의 삶의 방식과 문화에 대한 이해와 존중",
        "explanation": "시대적 상황과 지역적 여건 등에 따른 행복의 기준을 탐구하고, 이를 비교 평가함으로써 행복의 진정한 의미를 성찰할 수 있도록 한다.",
        "consideration": "행복에 대한 다양한 관점을 고전, 문학 작품, 신문 기사 등의 매체를 통해 균형 있게 다루되, 행복의 의미와 기준이 변화한다는 사실을 바탕으로 학생들이 진정한 행복의 의미를 성찰할 수 있도록 한다.",
        "ai_guide": "서로 다른 시대나 지역의 사상가(또는 가상 인물) 대화를 제시하고, 각 인물이 추구하는 행복의 기준을 비교하거나 비판하는 문항 구성. (고전이나 문학 작품 지문 활용 권장)"
    },
    {
        "id": "10통사1-02-02",
        "unit": "인간, 사회, 환경과 행복",
        "standard": "행복한 삶을 실현하기 위한 조건으로 질 높은 정주 환경의 조성, 경제적 안정, 민주주의 발전 및 도덕적 실천의 필요성에 관해 탐구한다.",
        "core_idea": "질 높은 정주 환경의 조성, 경제적 안정, 민주주의의 실현, 윤리적 실천은 행복한 삶을 위한 중요한 조건이다.",
        "knowledge": "행복의 의미, 행복의 조건",
        "process_value": "(과정) 탐구 주제에 적합한 자료를 수집 및 분석하기 \n\n(가치) 공동체 문제 해결을 위한 적극적 참여와 공동선의 실천",
        "explanation": "인간다운 삶을 누릴 수 있는 정주 환경의 조성과 삶의 질을 유지하기 위한 경제적 안정, 시민의 참여가 활성화되는 민주주의의 실현, 도덕적으로 행위하고 성찰하는 삶 등 행복한 삶을 실현하기 위한 조건들을 균형 있게 다루도록 한다.",
        "consideration": "행복한 삶을 실현하기 위해 요구되는 조건들을 다양한 사례를 통해 학습하여 그 필요성을 인식하고, 행복한 삶을 실현하기 위해 학생들이 스스로 실천할 수 있는 방안을 토의·토론함으로써 행복한 삶을 향유할 수 있는 태도를 함양하도록 한다.",
        "ai_guide": "특정 국가나 지역의 지표(수명, 소득, 민주주의 지수 등)를 도표로 제시하고, 이를 바탕으로 해당 지역의 행복 실현 조건을 분석하는 문항 구성. 오답 선지로 각 조건의 개념을 섞어서 제시."
    },
    {
        "id": "10통사1-03-01",
        "unit": "자연환경과 인간",
        "standard": "자연환경이 인간의 생활에 미치는 영향에 관한 과거와 현재의 사례를 조사하여 분석하고, 안전하고 쾌적한 환경에서 살아가는 것이 시민의 권리임을 주장한다.",
        "core_idea": "자연환경과 인간 생활의 유기적 관계를 고려하는 생태시민의 태도가 자연과 인간의 공존을 가능하게 한다.",
        "knowledge": "자연환경, 환경문제",
        "process_value": "(과정) 탐구 주제에 적합한 자료를 수집 및 분석하기\n\n(가치) 공동체의 문제 및 위기 해결 과정에 대한 적극적 참여",
        "explanation": "기후와 지형 등 자연환경에 따른 생활양식의 차이를 다루고, 자연환경의 변화로 인해 인간의 삶이 달라진 사례를 조사하여 원인 및 영향을 파악한다. 이를 토대로 쾌적한 환경에서 살아가는 것이 시민의 권리임을 인식한다.",
        "consideration": "자연환경의 변화로 인해 인간의 삶이 달라진 사례를 조사할 때는 지역적-국가적-세계적 규모에서 찾아보도록 하고, 긍정적인 사례도 함께 논의될 수 있도록 안내한다.",
        "ai_guide": "특정 지역의 기후/지형 자료를 제시하고 인간 생활양식의 변화를 묻거나, 환경권 보장과 관련된 헌법적 권리를 묻는 문항 구성."
    },
    {
        "id": "10통사1-03-02",
        "unit": "자연환경과 인간",
        "standard": "자연에 대한 인간의 다양한 관점을 사례를 통해 비교하고, 인간과 자연의 바람직한 관계를 제안한다.",
        "core_idea": "자연환경과 인간 생활의 유기적 관계를 고려하는 생태시민의 태도가 자연과 인간의 공존을 가능하게 한다.",
        "knowledge": "자연관",
        "process_value": "(과정) 갈등 상황에서 가치를 선택하고 그 결과를 예측 및 평가하기\n\n(가치) 생태·평화적 관점에서 공존과 지속가능한 발전을 지향하는 태도",
        "explanation": "인간 중심주의와 생태 중심주의를 중심으로 자연에 대한 인간의 관점을 다루되, 구체적인 사례를 통해 두 관점을 비교하도록 한다. 생태계 위기를 초래한 인간 사회 모습을 성찰한다.",
        "consideration": "특정 관점을 우위에 두고 일방적으로 주입하는 것이 아니라, 여러 관점을 비교하는 과정에서 인간의 관점이 정책이나 의사 결정에 영향을 미칠 수 있음을 이해하게 한다.",
        "ai_guide": "개발과 보존이 대립하는 실제 사례를 주고, 인간 중심주의와 생태 중심주의 사상가의 입장에서 어떻게 평가할지 묻는 딜레마 문항 구성."
    },
    {
        "id": "10통사1-03-03",
        "unit": "자연환경과 인간",
        "standard": "환경 문제 해결을 위한 정부, 시민사회, 기업 등의 다양한 노력을 조사하고, 생태 시민으로서 실천 방안을 모색한다.",
        "core_idea": "자연환경과 인간 생활의 유기적 관계를 고려하는 생태시민의 태도가 자연과 인간의 공존을 가능하게 한다.",
        "knowledge": "생태시민, 환경문제",
        "process_value": "(과정) 통합적 관점에서 해결 방안을 도출하고 타당성 평가하기\n\n(가치) 생태·평화적 관점에서 공존과 지속가능한 발전을 지향하는 태도",
        "explanation": "국내외 환경 문제 해결을 위한 정부의 제도적 노력, 시민단체 활동, 기업의 친환경 활동을 조사하고, 환경 문제 해결에 연대하고 실천할 수 있는 생태시민 자질을 함양한다.",
        "consideration": "개인적 차원의 실천 방안 탐색에 그치는 것이 아니라 생태시민으로서 다양한 환경문제 해결에 연대하는 구체적 실천에 주안점을 둔다.",
        "ai_guide": "환경 문제 해결을 위한 정부, 기업, 시민사회의 노력이 담긴 기사를 제시하고, 각 주체의 역할을 정확하게 짝지었는지 묻는 문항 구성."
    },
    {
        "id": "10통사1-04-01",
        "unit": "문화와 다양성",
        "standard": "자연환경과 인문환경의 영향을 받아 형성된 다양한 문화권의 특징과 삶의 방식을 탐구한다.",
        "core_idea": "다양성 존중의 태도는 서로 다른 문화권과 다문화 사회의 특성을 이해하는 바탕이 된다.",
        "knowledge": "문화권",
        "process_value": "(과정) 탐구 주제를 그림이나 지도, 도식 등을 활용하여 분석하고 표현하기\n\n(가치) 다양한 생활방식과 문화에 대한 이해와 존중",
        "explanation": "자연환경(기후, 지형)과 인문환경(종교, 산업)에 초점을 두어 다루며, 다양한 문화권의 특징과 삶의 방식은 비교 문화의 관점에서 고찰하도록 한다.",
        "consideration": "삶의 방식으로서의 문화는 해당 사회의 맥락에서 각기 고유한 의미가 있음을 학생 스스로 찾아내게 함으로써, 문화적 다양성을 존중하는 태도를 내면화하는 데 중점.",
        "ai_guide": "다양한 문화 경관이나 현상(사진, 지도)을 제시하고, 해당 문화권이 형성된 자연적/인문적 배경을 추론하게 하는 문항 구성."
    },
    {
        "id": "10통사1-04-02",
        "unit": "문화와 다양성",
        "standard": "문화 변동의 다양한 양상을 이해하고, 현대 사회에서 전통문화가 지니는 의의를 탐색한다.",
        "core_idea": "다양성 존중의 태도는 서로 다른 문화권과 다문화 사회의 특성을 이해하는 바탕이 된다.",
        "knowledge": "문화 변동",
        "process_value": "(과정) 탐구 주제의 역사적 배경 조사하기\n\n(가치) 타인의 감정 이해 및 타인의 가치와 태도 존중",
        "explanation": "문화 병존, 문화 융합, 문화 동화 등 문화 변동의 다양한 양상을 구체적인 사례를 통해 다루며, 현대 사회에서 전통문화를 창조적으로 계승·발전시키기 위한 방안을 언급한다.",
        "consideration": "음식 문화, 혼인 방식 등 자료를 수집하고 그러한 현상이 나타난 배경과 지속되는 이유 등을 탐구함으로써 깊이 있는 학습이 이루어지도록 한다.",
        "ai_guide": "문화 융합, 병존, 동화의 실제 사례(예: 음식, 언어)를 제시하고 각 개념을 올바르게 분류하거나 전통문화의 의의를 묻는 문항 구성."
    },
    {
        "id": "10통사1-04-03",
        "unit": "문화와 다양성",
        "standard": "문화적 차이에 대한 상대주의적 태도의 필요성을 이해하고, 보편 윤리의 차원에서 자문화와 타문화를 평가한다.",
        "core_idea": "다양성 존중의 태도는 서로 다른 문화권과 다문화 사회의 특성을 이해하는 바탕이 된다.",
        "knowledge": "문화 상대주의와 보편윤리",
        "process_value": "(과정) 갈등 상황에서 가치를 선택하고 그 결과를 예측 및 평가하기\n\n(가치) 다양한 생활방식과 문화에 대한 이해와 존중",
        "explanation": "문화적 차이가 나타나는 맥락을 파악하게 하여 문화 상대주의의 필요성을 인식하되, 극단적으로 흐르지 않도록 보편 윤리 차원에서 자문화와 타문화를 평가하도록 한다.",
        "consideration": "갈등 양상 실제 사례를 다룰 때는 소수의 문화나 정체성을 존중하는 관점에서 신중히 선택, 인권 존중 등 민주시민의 태도를 함양한다.",
        "ai_guide": "명예살인 등 극단적 문화 상대주의 사례를 제시하고, 보편 윤리적 관점과 문화 상대주의적 관점에서 이를 비판 및 평가하게 하는 딜레마형 문항 구성."
    },
    {
        "id": "10통사1-04-04",
        "unit": "문화와 다양성",
        "standard": "다문화 사회의 현황을 조사하고, 문화적 다양성을 존중하는 태도를 바탕으로 갈등 해결 방안을 모색한다.",
        "core_idea": "다양성 존중의 태도는 서로 다른 문화권과 다문화 사회의 특성을 이해하는 바탕이 된다.",
        "knowledge": "다문화 사회",
        "process_value": "(과정) 민주적 절차와 방법을 활용하여 합의 도출하기\n\n(가치) 민주적 절차를 존중하는 과정에서 사회적 소수자 배려",
        "explanation": "우리 사회 다문화 사회의 현황을 토대로 다양한 양상을 조명하며, 문화적 다양성 존중과 관련지어 갈등 해결 방안을 모색하도록 한다.",
        "consideration": "다문화 사회의 갈등 사례 중심으로 토의 시 인권 존중과 다양성 수용 등 민주시민으로서의 태도를 함양하는 데 초점을 맞춘다.",
        "ai_guide": "다문화 갈등 사례를 제시하고, 다양성을 존중하는 올바른 시민의 태도나 제도적 해결 방안을 고르는 문항 구성."
    },
    {
        "id": "10통사1-05-01",
        "unit": "생활공간과 사회",
        "standard": "산업화, 도시화로 인해 나타난 생활공간과 생활양식의 변화 양상을 조사하고, 이에 따른 문제점의 해결 방안을 제안한다.",
        "core_idea": "생활공간과 생활양식의 변화로 나타난 문제를 해결하려는 시민의 실천을 통해 지역사회의 변화를 이끌어낼 수 있다.",
        "knowledge": "산업화와 도시화, 생활공간과 생활양식",
        "process_value": "(과정) 탐구 주제에 적합한 자료를 수집 및 분석하기\n\n(가치) 공동체 문제 해결을 위한 적극적 참여와 공동선의 실천",
        "explanation": "생활공간 변화(거주 공간, 생태환경 등)와 생활양식 변화(도시성 확산, 개인주의 가치관 확산 등)를 다루며, 문제 해결 방안은 지역적 및 국가적 차원에서 모색한다.",
        "consideration": "산업화, 도시화의 측면에서 다각도로 살펴보고, 생활공간 및 양식의 변화로 나타난 문제에 관심을 가지고 대응하는 공동체 역량을 기른다.",
        "ai_guide": "산업화/도시화 전후의 지표(인구, 직업 비중)나 사진을 제시하고, 이에 따른 생활양식 변화(개인주의 등)와 문제 해결 방안을 묻는 문항 구성."
    },
    {
        "id": "10통사1-05-02",
        "unit": "생활공간과 사회",
        "standard": "교통·통신 및 과학기술의 발달과 함께 나타난 생활공간과 생활양식의 변화 양상을 조사하고, 이에 따른 문제점의 해결 방안을 제안한다.",
        "core_idea": "생활공간과 생활양식의 변화로 나타난 문제를 해결하려는 시민의 실천을 통해 지역사회의 변화를 이끌어낼 수 있다.",
        "knowledge": "교통·통신과 과학기술의 발달",
        "process_value": "(과정) 탐구 주제를 그림, 지도, 도식 등을 활용하여 분석하고 표현하기\n\n(가치) 지역적, 국가적, 세계적 수준의 다양한 쟁점에 관한 관심",
        "explanation": "정보화 및 제4차 산업 혁명을 통해 나타나는 공간의 확대 등을 다루며, 지역/정보 격차, 생태 교란, 노동 시장 양극화 등 새로운 사회문제와 해결 방안을 모색한다.",
        "consideration": "그림, 지도, 도식 등을 적극 활용하여 표현함으로써 시각 자료 이해 활용 능력을 강화하도록 한다.",
        "ai_guide": "교통 통신 발달로 인한 긍정적 측면(시공간 압축)과 부정적 측면(정보 격차, 양극화)을 보여주는 도표/기사를 분석하는 문항 구성."
    },
    {
        "id": "10통사1-05-03",
        "unit": "생활공간과 사회",
        "standard": "자신이 거주하는 지역을 사례로 공간 변화가 초래한 양상 및 문제점을 탐구하고, 공동체의 구성원으로서 지역사회의 변화를 위한 방안을 모색하고 이를 실천한다.",
        "core_idea": "생활공간과 생활양식의 변화로 나타난 문제를 해결하려는 시민의 실천을 통해 지역사회의 변화를 이끌어낼 수 있다.",
        "knowledge": "지역사회",
        "process_value": "(과정) 탐구 대상에 대한 현장조사 수행하기\n\n(가치) 공동체 문제 해결을 위한 적극적 참여와 공동선의 실천",
        "explanation": "토지 이용, 산업 구조, 생태환경, 가치관 변화 등을 중심으로 공간 변화를 탐구하고, 지역의 지속가능성을 고려하여 해결 방안을 모색한다.",
        "consideration": "거주 지역 사례로 당면 문제를 파악하게 함으로써 지역사회에 대한 관심 증진. 문헌 연구, 면담, 답사 등을 실시할 수 있다.",
        "ai_guide": "가상의 지역 답사 보고서나 위성 사진 비교 자료를 제시하고, 해당 지역의 공간 변화 원인과 지속가능한 해결책을 연결하는 문항 구성."
    },
    {
        "id": "10통사2-01-01",
        "unit": "인권보장과 헌법",
        "standard": "근대 시민 혁명 등을 통해 확립되어 온 인권의 의미와 변화 양상을 이해하고, 현대 사회에서 주거, 안전, 환경, 문화 등 다양한 영역으로 인권이 확장되고 있는 사례를 조사한다.",
        "core_idea": "근대 시민 혁명 이후 확립된 인권은 오늘날 사회제도적 장치의 마련과 시민의 노력으로 확장되고 있다.",
        "knowledge": "시민혁명, 인권",
        "process_value": "(과정) 탐구 주제의 역사적 배경 조사하기\n\n(가치) 시간적, 공간적, 사회적, 윤리적 차원의 쟁점에 관한 관심",
        "explanation": "인권 의미가 역사 속에서 확장되어 온 과정과 현대 사회에서 주거, 안전, 환경, 문화 영역에서 나타난 인권 확장의 대표적 사례들을 다룬다.",
        "consideration": "역사의 흐름 속에서 확장되어 온 인권의 의미와 변화 양상, 인권 보장을 위한 제도적 장치 등을 파악하여 인권 존중 태도 함양. 기록물 활용.",
        "ai_guide": "역사적 인권 선언문 사료를 순서대로 나열하거나, 현대 새롭게 등장한 인권(주거, 환경, 안전)의 사례와 특징을 연결하는 문항 구성."
    },
    {
        "id": "10통사2-01-02",
        "unit": "인권보장과 헌법",
        "standard": "인간 존엄성 실현과 인권 보장을 위한 헌법의 역할을 파악하고, 시민의 권익을 보호하기 위한 다양한 시민 참여의 방안을 탐구하고 이를 실천한다.",
        "core_idea": "근대 시민 혁명 이후 확립된 인권은 오늘날 사회제도적 장치의 마련과 시민의 노력으로 확장되고 있다.",
        "knowledge": "헌법, 시민참여",
        "process_value": "(과정) 민주적 절차와 방법을 활용하여 합의 도출하기\n\n(가치) 공동체 문제 해결을 위한 적극적 참여",
        "explanation": "인권과 헌법의 관계, 인권 보장을 위해 헌법에 규정된 제도적 장치를 다루며, 시민불복종을 비롯한 시민 참여의 다양한 방안을 찾는다.",
        "consideration": "인권 보장을 위한 헌법상의 장치와 시민의 노력 등을 파악하고 민주시민 태도 함양에 중점.",
        "ai_guide": "헌법 재판소 판례나 시민 불복종 사례를 제시하고, 그 근간이 되는 기본권 종류와 헌법의 역할을 묻는 문항 구성."
    },
    {
        "id": "10통사2-01-03",
        "unit": "인권보장과 헌법",
        "standard": "사회적 소수자 차별, 청소년의 노동권 등 국내 인권 문제와 인권지수를 통해 확인할 수 있는 세계 인권 문제의 양상을 조사하고, 이에 대한 해결 방안을 모색한다.",
        "core_idea": "근대 시민 혁명 이후 확립된 인권은 오늘날 사회제도적 장치의 마련과 시민의 노력으로 확장되고 있다.",
        "knowledge": "인권",
        "process_value": "(과정) 통합적 관점에서 해결 방안을 도출하고 타당성 평가하기\n\n(가치) 민주적 절차를 존중하는 과정에서 사회적 소수자 배려",
        "explanation": "성별, 연령 등 차별받는 소수자, 청소년 근로계약서 중심 법규 침해 사례를 다룬다. 국제기구 인권지수를 활용하여 양상과 해결 방안을 다룬다.",
        "consideration": "인권지수를 통해 세계 인권 문제 양상을 학습할 경우, 인권지수가 특정 국가의 절대적 인권 수준을 반영하는 것이 아님을 이해하게 한다.",
        "ai_guide": "잘못 작성된 청소년 근로계약서를 분석하여 법적 오류를 찾거나, 국제 인권지수 자료의 해석 한계를 묻는 문항 구성."
    },
    {
        "id": "10통사2-02-01",
        "unit": "사회정의와 불평등",
        "standard": "정의의 의미와 정의가 요구되는 이유를 파악하고, 다양한 사례를 통해 정의의 실질적 기준을 탐구한다.",
        "core_idea": "정의의 의미와 기준을 이해하고, 이에 대한 실천 방안을 모색함으로써 사회 불평등 문제 해결에 기여할 수 있다.",
        "knowledge": "정의의 실질적 기준",
        "process_value": "(과정) 주제와 관련된 다양한 가치를 통합적 관점에서 이해하기\n\n(가치) 타인의 감정 이해 및 가치와 태도 존중",
        "explanation": "분배적 정의와 교정적 정의의 의미를 분석. 특히 분배적 정의의 실질적 기준(업적, 능력, 필요 등)을 사례에 적용하여 장단점을 다룬다.",
        "consideration": "불평등 현상 및 다양한 제도를 비판적으로 분석·평가. 공정한 법 집행(교정적 정의) 구체적 사례 토의 시 세심한 주의 기울임.",
        "ai_guide": "보상이나 재화의 분배 기준(능력, 업적, 필요)이 다른 정책이나 사례를 제시하고 각 기준의 장단점을 비판적으로 평가하는 문항 구성."
    },
    {
        "id": "10통사2-02-02",
        "unit": "사회정의와 불평등",
        "standard": "개인과 공동체의 관계를 기준으로 다양한 정의관을 비교하고, 이를 구체적인 사례에 적용하여 설명한다.",
        "core_idea": "정의의 의미와 기준을 이해하고, 이에 대한 실천 방안을 모색함으로써 사회 불평등 문제 해결에 기여할 수 있다.",
        "knowledge": "정의관",
        "process_value": "(과정) 갈등 상황에서 가치를 선택하고 그 결과를 예측 평가하기\n\n(가치) 공동체 문제 해결을 위한 적극적 참여",
        "explanation": "자유주의적 정의관과 공동체주의적 정의관을 바탕으로 사익과 공익 문제 등을 다루며, 두 정의관에 기초해 정책을 평가한다.",
        "consideration": "자유주의적 정의관과 공동체주의적 정의관이 현실 정책에서 충돌할 수 있음을 사례를 통해 학습.",
        "ai_guide": "징병제 도입이나 공공시설 건설 등 사회적 딜레마를 두고 자유주의자와 공동체주의자 사상가의 대화 형태 문항 구성."
    },
    {
        "id": "10통사2-02-03",
        "unit": "사회정의와 불평등",
        "standard": "사회 및 공간 불평등 현상의 사례를 조사하고, 정의로운 사회를 만들기 위한 다양한 제도와 시민으로서의 실천 방안을 제안한다.",
        "core_idea": "정의의 의미와 기준을 이해하고, 이에 대한 실천 방안을 모색함으로써 사회 불평등 문제 해결에 기여할 수 있다.",
        "knowledge": "사회불평등, 공간불평등",
        "process_value": "(과정) 통합적 관점에서 해결 방안을 도출하고 타당성 평가하기\n\n(가치) 지역적, 국가적, 세계적 쟁점에 관한 관심",
        "explanation": "양극화, 공간 불평등 사례를 조사. 사회 복지 제도, 지역 격차 완화 정책, 적극적 평등 실현 조치 등 제도적 방안과 시민 실천 방안을 다룬다.",
        "consideration": "사회 및 공간 불평등을 해결하기 위한 제도적 방안의 도입 취지, 장단점 등에 대해 학생들이 자유롭게 토의·토론할 수 있도록 한다.",
        "ai_guide": "지니계수나 지역별 인프라 통계를 분석하고, 이를 완화하기 위한 정책(예: 할당제, 누진세)의 기대 효과나 취지를 묻는 문항 구성."
    },
    {
        "id": "10통사2-03-01",
        "unit": "시장경제와 지속가능발전",
        "standard": "자본주의의 역사적 전개 과정과 그 특징을 조사하고, 시장과 정부의 관계를 중심으로 다양한 삶의 방식을 비교 평가한다.",
        "core_idea": "경제 주체들은 효율성을 기준으로 경제활동에 참여하며, 문제 해결을 위해 지속가능발전을 추구한다.",
        "knowledge": "경제 주체의 역할",
        "process_value": "(과정) 탐구 주제의 역사적 배경 조사하기\n\n(가치) 타인의 감정 이해 및 타인의 가치 존중",
        "explanation": "자본주의 전개 과정과 특징을 역사적 사건/사상가를 통해 다루며, 시장경제와 계획경제 체제가 인간 삶에 미친 영향을 비교 평가한다.",
        "consideration": "자본주의 성립 과정 역사적 사건이나 사상가 주장에 관한 자료를 수집·탐구. 시장경제 아래 경제 주체가 효율성 기준으로 행동함을 이해.",
        "ai_guide": "시대별 경제 체제 변화(자유방임, 수정, 신자유주의)를 사상가의 글과 연결하거나, 시장과 정부의 역할 변화를 묻는 문항 구성."
    },
    {
        "id": "10통사2-03-02",
        "unit": "시장경제와 지속가능발전",
        "standard": "합리적 선택의 의미와 그 한계를 파악하고, 지속가능발전을 위해 요청되는 정부, 기업가, 노동자, 소비자의 바람직한 역할과 책임에 관해 탐구한다.",
        "core_idea": "경제 주체들은 효율성을 기준으로 경제활동에 참여하며, 문제 해결을 위해 지속가능발전을 추구한다.",
        "knowledge": "시장경제와 합리적 선택, 경제 주체의 역할",
        "process_value": "(과정) 주제와 관련된 가치를 통합적 관점에서 이해하기\n\n(가치) 공존과 지속가능한 발전을 지향하는 태도",
        "explanation": "합리적 선택 한계(시장 실패)를 다루고, 지속가능발전을 위한 정부, 기업가 정신, 기업 사회적 책임, 윤리적 소비 등을 언급한다.",
        "consideration": "합리적 선택과 지속가능발전 의미 체험을 위한 다양한 시뮬레이션 활용. 사회적 쟁점을 찾아 쟁점 중심으로 토론.",
        "ai_guide": "공공재 무임승차나 외부 효과(시장 실패) 사례를 제시하고, 이를 해결하기 위한 정부, 기업, 소비자의 올바른 역할을 찾는 문항 구성."
    },
    {
        "id": "10통사2-03-03",
        "unit": "시장경제와 지속가능발전",
        "standard": "금융 자산의 특징과 자산 관리의 원칙을 토대로 금융 생활을 설계하고, 경제적, 사회적 환경의 변화가 금융과 관련한 의사 결정에 미치는 영향을 탐구한다.",
        "core_idea": "경제 주체들은 효율성을 기준으로 경제활동에 참여하며, 문제 해결을 위해 지속가능발전을 추구한다.",
        "knowledge": "금융 생활",
        "process_value": "(과정) 탐구 주제에 적합한 자료를 수집 및 분석하기\n\n(가치) 시간적, 공간적, 사회적 쟁점에 관한 관심",
        "explanation": "예금, 채권, 주식 등을 다루며 수익성, 유동성, 안전성 원칙을 토대로 금융 설계. 금리 등 거시적 변화 요인이 미치는 영향을 이해한다.",
        "consideration": "개인의 금융 의사 결정에 영향을 미친 거시적인 변화 요인 탐구. 경제 현상에 대한 통합적인 학습이 이루어지도록 함.",
        "ai_guide": "예금, 주식, 채권의 특징을 수익성, 안전성 측면에서 비교하는 도표를 주고 분석하게 하거나, 금리 변동 뉴스 시 합리적 의사결정을 묻는 문항."
    },
    {
        "id": "10통사2-03-04",
        "unit": "시장경제와 지속가능발전",
        "standard": "자원, 노동, 자본의 지역 분포에 따른 국제 분업과 무역의 필요성을 이해하고, 지속가능발전에 기여하는 국제무역의 방안을 탐색한다.",
        "core_idea": "경제 주체들은 효율성을 기준으로 경제활동에 참여하며, 문제 해결을 위해 지속가능발전을 추구한다.",
        "knowledge": "국제 분업과 무역",
        "process_value": "(과정) 그림이나 지도, 도식 등을 활용하여 분석하고 표현하기\n\n(가치) 세계적 쟁점에 관한 관심",
        "explanation": "생산비 차이로 국제 분업/무역이 발생함을 다룸. 지속가능발전과 관련지어 공정 무역 등 국제무역 흐름 평가, 나아갈 방향 다룸.",
        "consideration": "각 나라의 주요 교역 상품 등에 관한 자료를 수집·탐구. 민주시민 및 세계시민으로서의 능력과 태도를 함양하는 데 초점.",
        "ai_guide": "생산비 차이(절대우위, 비교우위)를 보여주는 도표를 통해 어느 국가가 무역에 유리한지 계산하거나 공정 무역의 가치를 묻는 문항 구성."
    },
    {
        "id": "10통사2-04-01",
        "unit": "세계화와 평화",
        "standard": "세계화의 다양한 양상을 살펴보고, 세계화 시대의 문제점과 그에 대한 해결 방안을 제안한다.",
        "core_idea": "세계화의 과정에서 나타나는 여러 문제와 국제 분쟁을 평화적으로 해결할 수 있다.",
        "knowledge": "세계화",
        "process_value": "(과정) 탐구 주제를 나-지역-국가-세계의 관계 속에서 파악하기\n\n(가치) 지구촌 공동체의 문제 해결에 대한 적극적 참여",
        "explanation": "세계도시 형성, 다국적 기업 등장으로 인한 공간적·경제적 변화 및 문화 획일화, 빈부 격차 심화 등 문제점과 해결 방안 다룸.",
        "consideration": "뉴스, 광고 등 여러 매체를 조사하여 학생 삶 속 사례 찾기. 국제 사회 변화가 개인 삶에 깊이 영향을 미치고 있음을 이해하게 한다.",
        "ai_guide": "다국적 기업의 본사와 공장 분포 지도를 분석하거나, 세계화로 인한 문화의 동질화/이질화 양상을 비판적으로 분석하는 문항 구성."
    },
    {
        "id": "10통사2-04-02",
        "unit": "세계화와 평화",
        "standard": "평화의 관점에서 국제 사회의 갈등과 협력의 사례를 조사하고, 세계 평화를 위한 행위 주체의 바람직한 역할을 탐색한다.",
        "core_idea": "세계화의 과정에서 나타나는 여러 문제와 국제 분쟁을 평화적으로 해결할 수 있다.",
        "knowledge": "국제분쟁, 평화, 세계시민",
        "process_value": "(과정) 갈등 상황에서 가치를 선택하고 결과 예측 및 평가하기\n\n(가치) 갈등 해결을 위한 타인과의 소통과 협력",
        "explanation": "소극적 평화와 적극적 평화 개념을 다루고, 갈등/협력 사례를 통해 행위 주체(국가, NGO 등)의 역할 파악 및 세계시민 역할 탐색.",
        "consideration": "평화 추구 국제 협력 필요성 이해. 적극적 평화를 삶 속에서 지속하기 위한 조건을 탐색하고 실천 의지를 다지게 한다.",
        "ai_guide": "전쟁은 없으나 차별이 존재하는 사례를 주고 요한 갈퉁의 '적극적 평화' 개념으로 해석하게 하거나, NGO 등 국제 행위 주체 역할을 묻는 문항."
    },
    {
        "id": "10통사2-04-03",
        "unit": "세계화와 평화",
        "standard": "남북 분단과 동아시아의 역사 갈등 상황을 분석하고, 이를 토대로 우리나라가 세계 평화에 기여할 수 있는 방안을 제안한다.",
        "core_idea": "세계화의 과정에서 나타나는 여러 문제와 국제 분쟁을 평화적으로 해결할 수 있다.",
        "knowledge": "국제분쟁, 평화",
        "process_value": "(과정) 탐구 주제의 역사적 배경 조사하기\n\n(가치) 공존과 지속가능한 발전을 지향하는 태도",
        "explanation": "남북 분단 배경 및 평화통일 노력, 동아시아 역사 갈등 해결 방안 다룸. 지정학적 위치 등 고려하여 세계 평화 기여 방안 제안.",
        "consideration": "문헌, 발표문, 뉴스 등을 다각도로 조사. 영토 및 역사 갈등 상황 파악.",
        "ai_guide": "통일의 경제적/비경제적 편익을 나타낸 도표를 해석하거나, 동아시아 역사 갈등(예: 독도, 역사교과서)을 평화적으로 해결하기 위한 관점을 묻는 문항."
    },
    {
        "id": "10통사2-05-01",
        "unit": "미래와 지속가능한 삶",
        "standard": "세계의 인구 분포와 구조 등에 대한 이해를 토대로 현재와 미래의 인구 문제 양상을 파악하고, 그 해결 방안을 제안한다.",
        "core_idea": "지속가능한 발전의 추구를 통해 인류가 당면한 지구촌 문제 해결과 바람직한 미래 변화를 꾀할 수 있다.",
        "knowledge": "인구 문제, 미래 삶의 방향",
        "process_value": "(과정) 그림이나 지도, 도식 등을 활용하여 분석하기\n\n(가치) 지구촌 공동체 위기 해결에 대한 적극적 참여",
        "explanation": "저출생·고령화, 인구 과잉 등 지역별 인구 문제 배경과 문제점 파악, 미래 세대의 지속가능한 삶을 위한 해결 방안 살펴봄.",
        "consideration": "도표, 그래프, 지도 등 데이터를 읽는 방법 이해, 추세 분석 초점. 최신 통계 자료 활용.",
        "ai_guide": "선진국과 개발도상국의 인구 피라미드 변화 그래프를 제시하고, 각 지역에서 발생할 인구 문제(예: 부양비 증가)와 대책을 추론하는 문항 구성."
    },
    {
        "id": "10통사2-05-02",
        "unit": "미래와 지속가능한 삶",
        "standard": "지구적 차원에서 에너지 자원의 분포와 소비 실태 파악, 기후변화에 대한 대응과 지속가능한 발전을 위한 방안 탐구.",
        "core_idea": "지속가능발전 추구를 통해 지구촌 문제 해결과 미래 변화를 꾀할 수 있다.",
        "knowledge": "자원 위기, 지속가능발전",
        "process_value": "(과정) 주제에 적합한 자료 수집 및 분석\n\n(가치) 생태·평화적 관점에서 공존을 지향하는 태도",
        "explanation": "화석에너지 중심 소비 실태, 석유/석탄/천연가스 자원 분포 파악. 기후변화 대응 및 지속가능한 발전을 위한 제도적 방안 다룸.",
        "consideration": "통계 사이트 자료를 검색해 최신 자료 활용. 인류 공동의 문제를 지속가능성 측면에서 탐구.",
        "ai_guide": "석유, 석탄, 천연가스의 소비 비중 그래프나 편재성을 나타낸 지도를 익명으로 제시하고 자원을 매칭한 뒤 기후변화 대응 관련 특징을 묻는 문항."
    },
    {
        "id": "10통사2-05-03",
        "unit": "미래와 지속가능한 삶",
        "standard": "미래 사회의 모습을 다양한 측면에서 예측하고, 이를 바탕으로 세계시민으로서 자신의 미래 삶의 방향을 설정한다.",
        "core_idea": "지속가능발전 추구를 통해 지구촌 문제 해결과 미래 변화를 꾀할 수 있다.",
        "knowledge": "지속가능발전, 미래 삶의 방향",
        "process_value": "(과정) 탐구 주제를 나-지역-국가-세계 관계 속에서 파악하기\n\n(가치) 세계적 쟁점에 관한 관심",
        "explanation": "국가 간 협력/갈등, 과학기술 발전(공간 변화), 생태환경 등 다양한 측면에서 미래 사회 예측. 세계시민으로서 삶 방향 설정.",
        "consideration": "미래 사회 변화 예측 시 긍정적/부정적 측면을 함께 다루어 균형 잡힌 시각을 갖도록 함. 모둠 토의 시 동료 평가 진행.",
        "ai_guide": "특정 미래 기술(예: AI, 생명공학) 도입 기사를 주고, 기술 지상주의적 관점과 비관주의적 관점의 비판을 균형 있게 분석하는 문항 구성."
    },
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
