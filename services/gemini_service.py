"""
Gemini 2.5 API 연동 서비스
- 이미지 분석 (OCR + 문항 해석)
- 유사 문항 생성
- 수능형 문항 출제
- 교차 단원 출제
"""
import json
import google.generativeai as genai
from config.settings import ALL_UNITS, get_standards_text, get_all_standards_text

# ──────────────────────────────────────────────
# 시스템 프롬프트
# ──────────────────────────────────────────────
SYSTEM_PROMPT = """당신은 대한민국 고등학교 '2022 개정 교육과정 통합사회1·2' 전문 출제위원입니다.

[교육과정 단원 구성]
■ 통합사회1
  Ⅰ. 통합적 관점
  Ⅱ. 인간, 사회, 환경과 행복
  Ⅲ. 자연환경과 인간
  Ⅳ. 문화와 다양성
  Ⅴ. 생활공간과 사회

■ 통합사회2
  Ⅵ. 인권 보장과 헌법
  Ⅶ. 사회정의와 불평등
  Ⅷ. 시장경제와 지속가능발전
  Ⅸ. 세계화와 평화
  Ⅹ. 미래와 지속 가능한 삶

[출제 규칙]
1. 5지 선다형(①②③④⑤)으로 출제
2. 개념 파악 위주의 문항 제시
3. 수능 사회탐구 스타일 유지
4. 표/그래프가 필요한 경우 [시각 자료 설명] 블록으로 텍스트 설명 대체
5. 정답은 반드시 1개
6. 매력적인 오답(오개념 유도) 포함
7. 해설에서 정답 근거와 오답 분석을 명확히 제시
8. 성취기준 코드를 반드시 명시

[출력 형식 - 반드시 JSON]
{
  "questions": [
    {
      "unit": "단원 번호 (예: Ⅰ)",
      "unit_name": "단원명",
      "standard_code": "성취기준 코드",
      "question_text": "문항 본문 (발문 포함)",
      "choices": ["①선택지1", "②선택지2", "③선택지3", "④선택지4", "⑤선택지5"],
      "answer": "정답 번호 (예: ③)",
      "explanation": "상세 해설 (정답 근거 + 오답 분석)"
    }
  ]
}
"""

# ──────────────────────────────────────────────
# Gemini 클라이언트
# ──────────────────────────────────────────────
class GeminiService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-preview-05-20",
            system_instruction=SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=8192,
            ),
        )

    def _parse_response(self, text: str) -> dict:
        """Gemini 응답에서 JSON 추출"""
        text = text.strip()
        # ```json ... ``` 블록 추출
        if "```json" in text:
            start = text.index("```json") + 7
            end = text.index("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.index("```") + 3
            end = text.index("```", start)
            text = text[start:end].strip()
        # JSON 파싱 시도
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # { } 블록 직접 추출
            brace_start = text.find("{")
            brace_end = text.rfind("}") + 1
            if brace_start != -1 and brace_end > brace_start:
                return json.loads(text[brace_start:brace_end])
            return {"error": "JSON 파싱 실패", "raw": text}

    # ──────────────────────────────────────────
    # A. 이미지 → 유사 문항 2개
    # ──────────────────────────────────────────
    def analyze_and_generate_similar(self, image_data, mime_type: str = "image/png") -> dict:
        """이미지 문항 분석 후 유사 문항 2개 생성"""
        standards_ref = get_all_standards_text()

        prompt = f"""아래 이미지는 통합사회 시험 문항입니다.

[작업 순서]
1단계: 이미지의 문항을 정확히 읽고 분석하세요.
  - 어떤 단원·성취기준에 해당하는지 판별
  - 문항 유형(개념형, 사례형, 비교형 등) 파악
  - 묻고 있는 핵심 개념 파악

2단계: 분석 결과를 바탕으로 **유사 문항 2개**를 생성하세요.
  - 같은 성취기준 범위 내에서 출제
  - 같은 유형이되 다른 소재·사례 활용
  - 5지 선다형, 개념 파악 위주
  - 표/그래프 필요 시 [시각 자료 설명] 블록으로 대체

[참조 성취기준]
{standards_ref}

반드시 아래 JSON 형식으로 출력:
{{
  "analysis": {{
    "detected_unit": "단원 번호",
    "detected_unit_name": "단원명",
    "detected_standard": "성취기준 코드",
    "question_type": "문항 유형",
    "key_concept": "핵심 개념",
    "original_text": "원문항 내용 요약"
  }},
  "questions": [
    {{
      "unit": "단원 번호",
      "unit_name": "단원명",
      "standard_code": "성취기준 코드",
      "question_text": "문항 본문",
      "choices": ["①...", "②...", "③...", "④...", "⑤..."],
      "answer": "정답",
      "explanation": "해설"
    }}
  ]
}}"""

        response = self.model.generate_content([
            {"mime_type": mime_type, "data": image_data},
            prompt
        ])
        return self._parse_response(response.text)

    # ──────────────────────────────────────────
    # B. 수능형 자동 출제
    # ──────────────────────────────────────────
    def generate_exam(self, unit_keys: list, difficulty: str = "중", count: int = 2) -> dict:
        """선택한 단원에서 수능형 문항 출제"""
        # 선택 단원 성취기준 수집
        standards_parts = []
        for key in unit_keys:
            unit = ALL_UNITS.get(key)
            if unit:
                standards_parts.append(f"\n== {key}. {unit['name']} ==")
                standards_parts.append(get_standards_text(key))

        standards_text = "\n".join(standards_parts)

        difficulty_guide = {
            "하": "기본 개념 확인 수준. 교과서 본문에서 직접 확인 가능한 내용 중심.",
            "중": "개념 이해 + 적용 수준. 사례에 개념을 적용하거나 비교·분류하는 문항.",
            "상": "수능 고난도 수준. 복합 개념, 자료 해석, 비판적 사고가 필요한 문항."
        }

        prompt = f"""아래 성취기준을 바탕으로 수능형 문항을 **{count}개** 출제하세요.

[난이도] {difficulty} - {difficulty_guide.get(difficulty, difficulty_guide['중'])}

[성취기준]
{standards_text}

[출제 지침]
- 5지 선다형, 개념 파악 위주
- 수능 사회탐구 스타일 발문 사용 (예: "~에 대한 설명으로 옳은 것은?", "~에 해당하는 것만을 <보기>에서 있는 대로 고른 것은?")
- 매력적인 오답 배치
- 표/그래프 필요 시 [시각 자료 설명] 블록으로 대체
- 각 문항마다 정답 근거와 오답 분석 포함

JSON 형식으로 출력하세요."""

        response = self.model.generate_content(prompt)
        return self._parse_response(response.text)

    # ──────────────────────────────────────────
    # C. 교차 단원 출제
    # ──────────────────────────────────────────
    def cross_unit_generate(self, image_data, target_unit_key: str, mime_type: str = "image/png") -> dict:
        """이미지 문항의 '형태'를 유지하면서 다른 단원 내용으로 출제"""
        target_unit = ALL_UNITS.get(target_unit_key, {})
        target_standards = get_standards_text(target_unit_key)

        prompt = f"""아래 이미지는 통합사회 시험 문항입니다.

[작업]
1단계: 이미지 문항을 분석하세요.
  - 문항 구조/형태 파악 (발문 패턴, 선택지 구성 방식, <보기> 사용 여부 등)

2단계: 동일한 문항 형태(구조)를 유지하면서, 아래 **타겟 단원**의 내용으로 문항 2개를 새로 출제하세요.

[타겟 단원]
{target_unit_key}. {target_unit.get('name', '')}

[타겟 단원 성취기준]
{target_standards}

[규칙]
- 원본 문항의 형태(발문 패턴, 선택지 구성)를 최대한 유지
- 내용만 타겟 단원으로 교체
- 5지 선다형, 개념 파악 위주
- 표/그래프 필요 시 [시각 자료 설명] 블록으로 대체

JSON 형식으로 출력:
{{
  "original_analysis": {{
    "question_type": "원본 문항 유형",
    "structure": "원본 문항 구조 설명"
  }},
  "questions": [...]
}}"""

        response = self.model.generate_content([
            {"mime_type": mime_type, "data": image_data},
            prompt
        ])
        return self._parse_response(response.text)
