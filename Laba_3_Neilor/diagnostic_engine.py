"""
Ядро байесовской диагностической системы с корректным обновлением вероятностей
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
import math
from disease_database import DISEASES_DATABASE
from question_manager import QuestionManager

class DiagnosticEngine:
    def __init__(self):
        self.diseases = list(DISEASES_DATABASE.keys())
        # Добавляем гипотезу «Здоров» как отдельную шкалу, регулируемую как диагнозы
        self.healthy_label = "Здоров"
        if self.healthy_label not in self.diseases:
            self.diseases.append(self.healthy_label)
        self.question_manager = QuestionManager()

        # Инициализация вероятностей
        self.initialize_probabilities()

        # Пороги принятия решений (повышаем чувствительность и сокращаем лимиты)
        self.upper_threshold = 0.78  # Чуть ниже для более раннего принятия диагноза
        self.lower_threshold = 0.08  # Быстрее исключаем маловероятные болезни из активных
        self.min_questions = 4       # Минимальное количество вопросов
        self.max_questions = 10      # Максимальное количество вопросов
        # Динамическое расширение лимита вопросов, если уверенный диагноз не установлен
        self.extend_step = 5         # на сколько увеличивать лимит за раз
        self.hard_cap = 20           # жесткий максимум вопросов

        # Трекинг отрицательных ответов для выявления "Здоров"
        self.negative_streak = 0
        self.negative_count = 0
        self.total_answers = 0
        self.last_top_prob = 0.0

        # История диагностики
        self.diagnosis_history = []

    def initialize_probabilities(self):
        """Инициализировать начальные вероятности заболеваний"""
        # Требование: изначально все вероятности равны, изменения начинаются после вопросов
        self.disease_probabilities = {}
        n = max(1, len(self.diseases))
        uniform = 1.0 / n
        for disease in self.diseases:
            self.disease_probabilities[disease] = uniform

    def confidence_to_probability(self, confidence: float, question_type: str = "confidence") -> float:
        """Преобразовать уверенность пользователя в вероятность наличия симптома"""
        if question_type == "binary":
            # Уже вероятность (0-1)
            return max(0.0, min(1.0, confidence))
        elif question_type == "scale":
            # Шкала 0-10 преобразуется в 0-1
            return confidence / 10.0
        elif question_type == "range":
            # Уже вероятность
            return confidence
        elif question_type == "options":
            # Уже вероятность
            return confidence
        else:
            # Стандартная шкала -5..+5
            if -5 <= confidence <= 5:
                return (confidence + 5) / 10.0
            else:
                # Если что-то не так, возвращаем нейтральное значение
                return 0.5

    def update_probabilities_correctly(self, symptom: str, user_response: float, question_type: str = "confidence") -> Dict[str, float]:
        """
        Корректное обновление вероятностей с использованием полной формулы Байеса
        с учетом как положительных, так и отрицательных свидетельств

        Args:
            symptom: Имя симптома
            user_response: Ответ пользователя (преобразуется в вероятность наличия симптома)
            question_type: Тип вопроса (binary, scale, range, options, confidence)

        Returns:
            Новые вероятности заболеваний
        """
        # Преобразуем ответ пользователя в вероятность наличия симптома
        p_symptom_given_user = self.confidence_to_probability(user_response, question_type)

        # Для отладки
        debug_info = {
            "symptom": symptom,
            "user_response": user_response,
            "p_symptom_given_user": p_symptom_given_user,
            "old_probabilities": self.disease_probabilities.copy()
        }

        # Вычисляем вероятность симптома для каждого заболевания P(S|D)
        p_s_given_d = {}
        for disease in self.diseases:
            disease_data = DISEASES_DATABASE.get(disease, {})
            symptoms = disease_data.get("symptoms", {})

            if symptom in symptoms:
                # Используем вес симптома, преобразованный в вероятность (1-10 -> 0.1-1.0)
                weight = symptoms[symptom]["weight"]
                p_s_given_d[disease] = weight / 10.0
            elif disease == getattr(self, 'healthy_label', 'Здоров'):
                # Для гипотезы «Здоров» предполагаем очень низкую базовую вероятность
                # наличия любого симптома
                p_s_given_d[disease] = 0.03
            else:
                # Если симптом не характерен для заболевания, вероятность низкая
                # Но не нулевая, чтобы избежать проблем с делением на ноль
                p_s_given_d[disease] = 0.02

        # Вычисляем априорную вероятность симптома P(S) по формуле полной вероятности
        p_symptom = 0.0
        for disease in self.diseases:
            p_symptom += p_s_given_d[disease] * self.disease_probabilities[disease]

        # Избегаем деления на ноль
        if p_symptom < 0.001:
            p_symptom = 0.001
        if p_symptom > 0.999:
            p_symptom = 0.999

        # Ключевое исправление: используем правильную формулу Байеса
        # P(D|S_user) = P(S_user|S) * P(S|D) * P(D) / P(S_user)
        # где P(S_user) = Σ P(S_user|S) * P(S|D) * P(D)

        # Сначала вычисляем P(S_user|S) - вероятность ответа пользователя при наличии симптома
        # Предполагаем, что если симптом есть, пользователь с большей вероятностью ответит "да"
        # и наоборот, если симптома нет, с большей вероятностью ответит "нет"

        # Вычисляем новые вероятности заболеваний
        new_probabilities = {}
        total_probability = 0.0

        for disease in self.diseases:
            p_d = self.disease_probabilities[disease]  # P(D)
            p_s_given_d_val = p_s_given_d[disease]     # P(S|D)

            # Вероятность ответа пользователя при данном заболевании
            # Если симптом характерен для заболевания (p_s_given_d_val высокое),
            # то вероятность положительного ответа выше
            # Усиливаем влияние ответа пользователя (повышаем чувствительность)
            # Преобразуем p_symptom_given_user с усилением вокруг 0.5
            gain = 2.2
            centered = (p_symptom_given_user - 0.5) * gain
            p_user_adj = max(0.0, min(1.0, 0.5 + centered))

            p_response_given_d = (p_s_given_d_val * p_user_adj +
                                 (1 - p_s_given_d_val) * (1 - p_user_adj))

            # Нормализуем, чтобы сумма по всем заболеваниям была 1
            new_probability = p_response_given_d * p_d

            new_probabilities[disease] = new_probability
            total_probability += new_probability

        # Нормализуем вероятности
        if total_probability > 0:
            for disease in self.diseases:
                new_probabilities[disease] = new_probabilities[disease] / total_probability
        else:
            # Если все вероятности нулевые, оставляем старые
            new_probabilities = self.disease_probabilities.copy()

        # Применяем затухание (еще повышаем скорость обучения для чувствительности)
        learning_rate = 0.92
        final_probabilities = {}
        for disease in self.diseases:
            final_probabilities[disease] = (
                learning_rate * new_probabilities[disease] +
                (1 - learning_rate) * self.disease_probabilities[disease]
            )

        # Нормализуем еще раз
        total = sum(final_probabilities.values())
        if total > 0:
            for disease in self.diseases:
                final_probabilities[disease] = final_probabilities[disease] / total

        debug_info["new_probabilities"] = final_probabilities.copy()
        self.diagnosis_history.append(debug_info)

        return final_probabilities

    def update_with_response(self, symptom: str, user_response: float, question_type: str = "confidence"):
        """Обновить систему на основе ответа пользователя"""
        # Обновляем вероятности с исправленной логикой
        self.disease_probabilities = self.update_probabilities_correctly(symptom, user_response, question_type)

        # Записываем ответ
        self.question_manager.record_response(symptom, user_response, question_type)

        # Обновляем счетчики отрицательных/всех ответов для логики "Здоров"
        p_user = self.confidence_to_probability(user_response, question_type)
        self.total_answers += 1
        if p_user <= 0.3:
            self.negative_streak += 1
            self.negative_count += 1
        else:
            self.negative_streak = 0

        # Отслеживаем динамику топ-диагноза
        if self.disease_probabilities:
            self.last_top_prob = max(self.disease_probabilities.values())

    def get_active_diseases(self) -> List[str]:
        """Получить список активных заболеваний (не отвергнутых)"""
        active = []
        for disease, prob in self.disease_probabilities.items():
            if prob > self.lower_threshold:
                active.append(disease)

        # Сортируем по убыванию вероятности
        return sorted(active, key=lambda d: self.disease_probabilities[d], reverse=True)

    def get_accepted_diagnosis(self) -> Optional[str]:
        """Получить принятый диагноз, если он есть"""
        for disease, prob in self.disease_probabilities.items():
            if prob >= self.upper_threshold:
                return disease

        # Правило "Здоров": много отрицательных ответов и низкие вероятности всех болезней
        max_prob = max(self.disease_probabilities.values()) if self.disease_probabilities else 0.0
        negative_ratio = (self.negative_count / self.total_answers) if self.total_answers > 0 else 0.0
        # Ослабляем условия для более раннего определения здоровья
        # - допускаем более низкое отношение отрицательных ответов
        # - допускаем чуть более высокую максимальную вероятность болезней
        if self.total_answers >= self.min_questions and negative_ratio >= 0.6 and max_prob < 0.35:
            return "Здоров"
        return None

    def is_diagnosis_complete(self) -> bool:
        """Проверка, завершена ли диагностика"""
        questions_asked = len(self.question_manager.question_history)

        # Минимальное количество вопросов не достигнуто - продолжаем
        if questions_asked < self.min_questions:
            return False

        # Достигнут текущий лимит вопросов
        if questions_asked >= self.max_questions:
            # Если уверенный диагноз отсутствует, пытаемся продолжить задавать уточняющие вопросы
            accepted_now = self.get_accepted_diagnosis()
            if not accepted_now and self.max_questions < self.hard_cap:
                # Расширяем лимит и продолжаем
                self.max_questions = min(self.hard_cap, self.max_questions + self.extend_step)
                return False
            # Иначе останавливаемся (жесткий максимум или диагноз принят)
            return True

        # Проверяем, есть ли уверенный диагноз (включая "Здоров")
        accepted = self.get_accepted_diagnosis()
        if accepted:
            # Если диагноз есть и вероятность стабильна, останавливаемся
            if accepted == "Здоров":
                return True
            if questions_asked >= 10:
                # Проверяем, не меняется ли диагноз сильно последние 3 вопроса
                if len(self.diagnosis_history) >= 3:
                    last_probs = []
                    for i in range(min(3, len(self.diagnosis_history))):
                        if accepted in self.diagnosis_history[-1-i]["new_probabilities"]:
                            last_probs.append(self.diagnosis_history[-1-i]["new_probabilities"][accepted])

                    if len(last_probs) >= 2:
                        # Если изменение вероятности меньше 0.1, считаем стабильным
                        if max(last_probs) - min(last_probs) < 0.1:
                            return True

        # Проверяем, осталось ли одно заболевание
        active = self.get_active_diseases()
        if len(active) == 1 and questions_asked >= 10:
            return True

        # Ранняя остановка при серии отрицательных ответов и низкой уверенности
        if self.negative_streak >= 4 and self.last_top_prob < 0.35:
            return True

        return False

    def get_next_question(self) -> Tuple[Optional[str], Optional[str], Optional[Dict]]:
        """Получить следующий вопрос"""
        active_diseases = self.get_active_diseases()
        # Исключаем «Здоров» из списка для выбора вопросов,
        # чтобы вопросы фокусировались на различении реальных диагнозов
        active_diseases = [d for d in active_diseases if d != self.healthy_label]
        questions_asked = len(self.question_manager.question_history)

        # Улучшенная стратегия выбора вопросов
        return self.question_manager.get_next_question_strategically(
            active_diseases,
            self.disease_probabilities,
            questions_asked
        )

    def get_diagnosis_summary(self) -> Dict:
        """Получить сводку диагностики"""
        return {
            "probabilities": self.disease_probabilities,
            "accepted_diagnosis": self.get_accepted_diagnosis(),
            "active_diseases": self.get_active_diseases(),
            "questions_asked": len(self.question_manager.question_history),
            "question_history": self.question_manager.get_response_summary(),
            "total_diseases": len(self.diseases)
        }

    def get_diagnosis_confidence(self) -> float:
        """Получить общую уверенность в диагнозе"""
        accepted = self.get_accepted_diagnosis()
        if accepted:
            return self.disease_probabilities.get(accepted, 0.0)

        # Если нет принятого диагноза, возвращаем максимальную вероятность
        if self.disease_probabilities:
            return max(self.disease_probabilities.values())
        return 0.0

    def reset(self):
        """Сбросить диагностическую систему"""
        self.initialize_probabilities()
        self.question_manager.reset()
        self.diagnosis_history.clear()