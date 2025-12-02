"""
Логирование результатов диагностики
"""

import json
import datetime
from typing import Dict, List
import os


class ResultsLogger:
    def __init__(self, log_dir="diagnosis_logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

    def log_diagnosis(self, diagnosis_data: Dict):
        """Записать результат диагностики в файл"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"diagnosis_{timestamp}.json"
        filepath = os.path.join(self.log_dir, filename)

        # Добавляем временную метку
        diagnosis_data["timestamp"] = timestamp
        diagnosis_data["datetime"] = datetime.datetime.now().isoformat()

        # Сохраняем в JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(diagnosis_data, f, ensure_ascii=False, indent=2)

        return filepath

    def load_recent_logs(self, count=10) -> List[Dict]:
        """Загрузить последние логи"""
        logs = []
        try:
            files = sorted([f for f in os.listdir(self.log_dir) if f.endswith('.json')])
            files.reverse()  # Новейшие сначала

            for filename in files[:count]:
                filepath = os.path.join(self.log_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                    logs.append(log_data)
        except Exception as e:
            print(f"Ошибка при загрузке логов: {e}")

        return logs