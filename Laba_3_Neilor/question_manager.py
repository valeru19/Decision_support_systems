"""
Улучшенный менеджер вопросов с дифференцированными стратегиями
"""

from typing import List, Dict, Tuple, Set, Optional
import random
import math
from disease_database import DISEASES_DATABASE, SYMPTOM_QUESTIONS

class QuestionManager:
    def __init__(self):
        self.asked_questions: Set[str] = set()
        self.question_history: List[Dict] = []
        self.symptom_responses: Dict[str, float] = {}

        # Статистика по типам вопросов
        self.general_questions_asked = 0
        self.differential_questions_asked = 0
        self.specific_questions_asked = 0

    def calculate_question_value(self, symptom: str, active_diseases: List[str],
                                disease_probabilities: Dict[str, float]) -> float:
        """
        Рассчитать ценность вопроса на основе его способности различать заболевания

        Args:
            symptom: Симптом для оценки
            active_diseases: Активные заболевания
            disease_probabilities: Текущие вероятности

        Returns:
            Значение вопроса (чем выше, тем информативнее)
        """
        if not active_diseases or len(active_diseases) < 2:
            return 0.0

        # Собираем вероятности наличия симптома для каждого активного заболевания
        symptom_probs = []
        total_prob = 0.0

        for disease in active_diseases:
            disease_data = DISEASES_DATABASE.get(disease, {})
            symptoms = disease_data.get("symptoms", {})

            if symptom in symptoms:
                # Преобразуем вес в вероятность
                weight = symptoms[symptom]["weight"]
                specificity = symptoms[symptom]["specificity"]
                symptom_prob = weight / 10.0
            else:
                # Симптом не характерен для заболевания
                symptom_prob = 0.1

            disease_prob = disease_probabilities.get(disease, 0.0)
            weighted_prob = symptom_prob * disease_prob

            symptom_probs.append((disease, symptom_prob, disease_prob))
            total_prob += weighted_prob

        if total_prob == 0:
            return 0.0

        # Нормализуем
        normalized_probs = [(d, sp, dp) for d, sp, dp in symptom_probs]

        # Вычисляем информативность как энтропию
        # Вопрос тем информативнее, чем ближе суммарная вероятность симптома к 0.5
        # (то есть он не слишком частый и не слишком редкий)

        # Вычисляем ожидаемую вероятность симптома
        expected_prob = 0.0
        for _, sp, dp in normalized_probs:
            expected_prob += sp * dp

        # Информативность максимальна при expected_prob = 0.5
        # Используем отрицание квадратичного отклонения от 0.5
        info_value = 1.0 - abs(expected_prob - 0.5) * 2.0

        # Учитываем разброс вероятностей симптома между заболеваниями
        # Чем больше разброс, тем лучше вопрос различает заболевания
        if len(symptom_probs) >= 2:
            symptom_values = [sp for _, sp, _ in symptom_probs]
            variance = np.var(symptom_values) if symptom_values else 0.0
            info_value *= (1.0 + variance)

        # Учитываем предыдущие ответы пользователя по этому симптому (адаптация к ответам)
        if symptom in self.symptom_responses:
            resp = self.symptom_responses[symptom]
            # Сильный негативный ответ снижает ценность повторного вопроса про тот же симптом
            if resp <= 0.3:
                info_value *= 0.2
            # Сильный позитивный ответ делает уместными уточнения
            elif resp >= 0.7:
                info_value *= 1.25

        # Штрафуем уже заданные вопросы
        if symptom in self.asked_questions:
            info_value *= 0.3

        return info_value

    def get_next_question_strategically(self, active_diseases: List[str],
                                       disease_probabilities: Dict[str, float],
                                       questions_asked: int) -> Tuple[Optional[str], Optional[str], Optional[Dict]]:
        """
        Стратегический выбор следующего вопроса

        Args:
            active_diseases: Активные заболевания
            disease_probabilities: Текущие вероятности
            questions_asked: Количество уже заданных вопросов

        Returns:
            Кортеж (симптом, текст вопроса, данные вопроса)
        """
        if not active_diseases:
            return None, None, None

        # Получаем все возможные симптомы для активных заболеваний
        all_symptoms = set()
        for disease in active_diseases:
            symptoms = DISEASES_DATABASE.get(disease, {}).get("symptoms", {}).keys()
            all_symptoms.update(symptoms)

        # Исключаем уже заданные вопросы
        available_symptoms = list(all_symptoms - self.asked_questions)

        if not available_symptoms:
            # Если все симптомы заданы, начинаем задавать уточняющие вопросы
            available_symptoms = list(all_symptoms)
            # Сбрасываем штраф за повторные вопросы
            for symptom in available_symptoms:
                if symptom in self.asked_questions:
                    # Немного снижаем вероятность повторного вопроса
                    continue

        if not available_symptoms:
            return None, None, None

        # Оценим долю отрицательных ответов пользователя для адаптации стратегии
        negatives = sum(1 for v in self.symptom_responses.values() if v <= 0.3)
        total_resp = len(self.symptom_responses)
        negative_ratio = (negatives / total_resp) if total_resp > 0 else 0.0

        # Стратегия в зависимости от этапа диагностики и доли отрицательных ответов
        if questions_asked < 4:
            # Ранний этап: задаем общие вопросы с высокой информативностью
            strategy = "general"
        elif negative_ratio >= 0.6:
            # Много отрицаний: агрессивно отсекаем заболевания
            strategy = "prune"
        elif questions_asked < 9:
            # Средний этап: дифференциальная диагностика
            strategy = "differential"
        else:
            # Поздний этап: уточнение диагноза
            strategy = "refinement"

        # Выбираем лучший вопрос в соответствии со стратегией
        best_symptom = None
        best_value = -1.0

        for symptom in available_symptoms:
            # Базовое значение вопроса
            base_value = self.calculate_question_value(symptom, active_diseases, disease_probabilities)

            # Корректируем в зависимости от стратегии
            if strategy == "general":
                # На раннем этапе предпочитаем общие симптомы
                question_data = SYMPTOM_QUESTIONS.get(symptom, {})
                question_text = question_data.get("question", "")
                # Общие симптомы часто содержат базовые термины
                general_terms = ["температура", "слабость", "боль", "кашель", "насморк"]
                is_general = any(term in symptom.lower() or term in question_text.lower() for term in general_terms)
                value = base_value * (1.5 if is_general else 1.0)

            elif strategy == "differential":
                # На среднем этапе предпочитаем симптомы с высокой специфичностью
                max_specificity = 0
                for disease in active_diseases:
                    disease_data = DISEASES_DATABASE.get(disease, {})
                    symptoms = disease_data.get("symptoms", {})
                    if symptom in symptoms:
                        specificity = symptoms[symptom].get("specificity", 0)
                        max_specificity = max(max_specificity, specificity)

                # Нормализуем специфичность (1-10 -> 0.1-1.0)
                specificity_factor = max_specificity / 10.0
                value = base_value * (1.0 + specificity_factor * 0.5)

            elif strategy == "prune":
                # При множестве отрицаний выбираем симптомы, которые покрывают
                # много активных заболеваний и имеют высокие веса (для быстрого отсечения)
                coverage = 0
                weight_sum = 0
                for disease in active_diseases:
                    disease_data = DISEASES_DATABASE.get(disease, {})
                    symptoms = disease_data.get("symptoms", {})
                    if symptom in symptoms:
                        coverage += 1
                        weight_sum += symptoms[symptom].get("weight", 0)

                mean_weight = (weight_sum / coverage) if coverage > 0 else 0
                coverage_factor = (coverage / max(1, len(active_diseases)))  # 0..1
                # Буст: предпочитаем широкий охват и средний-высокий вес
                value = base_value * (1.1 + mean_weight / 20.0 + coverage_factor * 0.6)

            else:  # refinement
                # На позднем этапе предпочитаем вопросы, которые могут подтвердить или опровергнуть текущий лидер
                if len(active_diseases) > 0:
                    leader = active_diseases[0]  # Заболевание с максимальной вероятностью
                    disease_data = DISEASES_DATABASE.get(leader, {})
                    symptoms = disease_data.get("symptoms", {})

                    if symptom in symptoms:
                        # Симптом характерен для лидера
                        weight = symptoms[symptom]["weight"]
                        # Вопросы, которые могут подтвердить лидера, ценны
                        value = base_value * (1.0 + weight / 20.0)
                    else:
                        # Симптом не характерен для лидера - тоже ценно, может опровергнуть
                        value = base_value * 1.2
                else:
                    value = base_value

            # Дополнительная адаптация: если пользователь ранее отрицал этот симптом, сильно понижаем
            prev = self.symptom_responses.get(symptom)
            if prev is not None and prev <= 0.3:
                value *= 0.15

            # Учитываем, задавался ли вопрос ранее
            if symptom in self.asked_questions:
                value *= 0.25  # Еще более сильный штраф за повторный вопрос

            if value > best_value:
                best_value = value
                best_symptom = symptom

        if not best_symptom:
            return None, None, None

        # Получаем данные вопроса
        question_data = SYMPTOM_QUESTIONS.get(best_symptom, {})
        question_text = question_data.get("question", "Вопрос о симптоме")

        # Помечаем как заданный
        self.asked_questions.add(best_symptom)

        # Обновляем статистику
        if strategy == "general":
            self.general_questions_asked += 1
        elif strategy == "differential":
            self.differential_questions_asked += 1
        else:
            self.specific_questions_asked += 1

        return best_symptom, question_text, question_data

    def record_response(self, symptom: str, user_response: float, question_type: str = "confidence"):
        """Записать ответ пользователя"""
        self.symptom_responses[symptom] = user_response
        self.question_history.append({
            "symptom": symptom,
            "user_response": user_response,
            "question_type": question_type,
            "question": SYMPTOM_QUESTIONS.get(symptom, {}).get("question", "")
        })

    def get_response_summary(self) -> List[Dict]:
        """Получить сводку ответов"""
        return self.question_history

    def reset(self):
        """Сбросить историю вопросов"""
        self.asked_questions.clear()
        self.question_history.clear()
        self.symptom_responses.clear()
        self.general_questions_asked = 0
        self.differential_questions_asked = 0
        self.specific_questions_asked = 0


# Добавляем поддержку numpy для вычисления дисперсии
import numpy as np