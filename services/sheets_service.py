"""
Google Sheets 연동 서비스 (선택적)
- 성취기준 DB 읽기
- 출제 이력 저장
"""
import os
import datetime

class SheetsService:
    """Google Sheets가 없어도 동작하는 로컬 이력 관리"""

    def __init__(self):
        self.history = []

    def add_history(self, mode: str, unit: str, question_data: dict):
        """출제 이력 추가"""
        self.history.append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": mode,
            "unit": unit,
            "data": question_data,
        })

    def get_history(self) -> list:
        """출제 이력 반환"""
        return self.history

    def clear_history(self):
        """이력 초기화"""
        self.history = []
