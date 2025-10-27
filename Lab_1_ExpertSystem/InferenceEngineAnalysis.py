
"""
Движок анализа (Inference Engine) экспертной системы гидропоники

Содержит нелинейные математические модели для:
- Оценки выживаемости растения
- Прогнозирования урожайности
- Расчета здоровья растения
- Выявления проблем и генерации рекомендаций

Использует реальные агрономические закономерности:
- Закон минимума Либиха (урожай ограничен самым дефицитным фактором)
- Закон толерантности Шелфорда (оптимум и пределы выносливости)
- Нелинейные зависимости (экспоненциальные, сигмоидные функции)
"""

import math
from typing import Dict, List, Tuple

from HydroponicExpertSystemModels import (
    EnvironmentParameters,
    CropRequirements,
    AnalysisResult,
    OptimalRange
)


class InferenceEngine:
    """
    Движок логического вывода для анализа условий выращивания
    
    Использует нечеткую логику и нелинейные функции для оценки
    влияния каждого параметра на растение.
    """
    
    # Веса важности параметров для расчетов (сумма = 1.0)
    # Разные параметры по-разному влияют на выживаемость и урожай
    PARAMETER_WEIGHTS = {
        'temperature': 0.20,      # Температура критично важна
        'humidity': 0.10,         # Влажность важна, но не критична
        'ph': 0.25,               # pH критичен (блокирует усвоение питания)
        'ec': 0.20,               # EC критичен (концентрация удобрений)
        'light_intensity': 0.15,  # Свет важен для фотосинтеза
        'light_hours': 0.10       # Продолжительность освещения
    }
    
    def __init__(self):
        """Инициализация движка анализа"""
        pass
    
    def analyze(
        self,
        current_params: EnvironmentParameters,
        requirements: CropRequirements
    ) -> AnalysisResult:
        """
        Провести полный анализ текущих условий выращивания
        
        Args:
            current_params: Текущие параметры среды
            requirements: Требования культуры к условиям
            
        Returns:
            AnalysisResult: Полный результат анализа с оценками и рекомендациями
        """
        # Шаг 1: Рассчитываем оценки для каждого параметра (0-1)
        parameter_scores = self._calculate_parameter_scores(current_params, requirements)
        
        # Шаг 2: Рассчитываем вероятность выживания
        # Критичные отклонения приводят к низкой выживаемости
        survival_probability = self._calculate_survival_probability(parameter_scores)
        
        # Шаг 3: Рассчитываем прогноз урожайности
        # Учитывается нелинейная зависимость от всех параметров
        yield_forecast = self._calculate_yield_forecast(parameter_scores, survival_probability)

        # 3.2
        max_yield_kg_per_m2 = yield_forecast * requirements.max_yield_kg_per_m2
        
        # Шаг 4: Рассчитываем общую оценку здоровья (0-100)
        health_score = self._calculate_health_score(parameter_scores)
        
        # Шаг 5: Определяем проблемы и предупреждения
        critical_issues, warnings = self._identify_issues(
            current_params, requirements, parameter_scores
        )
        
        # Шаг 6: Генерируем конкретные рекомендации
        recommendations = self._generate_recommendations(
            current_params, requirements, parameter_scores, critical_issues, warnings
        )
        
        # Шаг 7: Вычисляем оптимальные параметры (центр оптимального диапазона)
        optimal_parameters = self._calculate_optimal_parameters(requirements)
        
        return AnalysisResult(
            survival_probability=survival_probability,
            yield_forecast=yield_forecast,
            max_yield_kg_per_m2=max_yield_kg_per_m2,
            health_score=health_score,
            critical_issues=critical_issues,
            warnings=warnings,
            recommendations=recommendations,
            optimal_parameters=optimal_parameters,
            parameter_scores=parameter_scores
        )
    
    def _calculate_parameter_scores(
        self,
        current: EnvironmentParameters,
        requirements: CropRequirements
    ) -> Dict[str, float]:
        """
        Рассчитать оценку качества для каждого параметра
        
        Оценка показывает насколько текущее значение близко к оптимуму:
        1.0 = идеально (в оптимальном диапазоне)
        0.5-0.99 = допустимо (есть отклонение, но не критично)
        0.0-0.49 = критично (серьезное отклонение)
        
        Args:
            current: Текущие параметры среды
            requirements: Требования культуры
            
        Returns:
            Dict[str, float]: Словарь с оценками для каждого параметра
        """
        scores = {}
        
        # Температура
        deviation = requirements.temperature.get_deviation(current.temperature)
        scores['temperature'] = self._deviation_to_score(deviation)
        
        # Влажность
        deviation = requirements.humidity.get_deviation(current.humidity)
        scores['humidity'] = self._deviation_to_score(deviation)
        
        # pH
        deviation = requirements.ph.get_deviation(current.ph)
        scores['ph'] = self._deviation_to_score(deviation)
        
        # EC (электропроводность)
        deviation = requirements.ec.get_deviation(current.ec)
        scores['ec'] = self._deviation_to_score(deviation)
        
        # Освещенность
        deviation = requirements.light_intensity.get_deviation(current.light_intensity)
        scores['light_intensity'] = self._deviation_to_score(deviation)
        
        # Световой день
        deviation = requirements.light_hours.get_deviation(current.light_hours)
        scores['light_hours'] = self._deviation_to_score(deviation)
        
        return scores
    
    def _deviation_to_score(self, deviation: float) -> float:
        """
        Преобразовать отклонение в оценку качества
        
        Использует нелинейную (экспоненциальную) функцию:
        - Небольшие отклонения почти не влияют на оценку
        - Критические отклонения резко снижают оценку
        
        Формула: score = exp(-k * deviation^2)
        
        Args:
            deviation: Отклонение от оптимума (0=идеал, 1=критично)
            
        Returns:
            float: Оценка качества (1=отлично, 0=критично)
        """
        # Коэффициент крутизны экспоненциальной функции
        k = 3.0
        
        # Экспоненциальная функция для нелинейности
        # При deviation=0 -> score=1.0 (идеально)
        # При deviation=1 -> score≈0.05 (критично)
        score = math.exp(-k * deviation ** 2)
        
        # Ограничиваем диапазон [0, 1]
        return max(0.0, min(1.0, score))
    
    def _calculate_survival_probability(self, parameter_scores: Dict[str, float]) -> float:
        """
        Рассчитать вероятность выживания растения
        
        Логика:
        - Если ВСЕ параметры хорошие -> высокая вероятность (0.9-1.0)
        - Если ХОТЯ БЫ ОДИН параметр критичен -> низкая вероятность
        - Используем произведение (не среднее), т.к. один плохой фактор = гибель
        
        Это реализует принцип "самого слабого звена":
        растение погибнет из-за худшего параметра
        
        Args:
            parameter_scores: Оценки всех параметров
            
        Returns:
            float: Вероятность выживания (0-1)
        """
        # Базовая вероятность = произведение всех взвешенных оценок
        base_probability = 1.0
        
        for param_name, score in parameter_scores.items():
            # Получаем вес важности параметра
            weight = self.PARAMETER_WEIGHTS[param_name]
            
            # Взвешенное влияние: score^(weight*2)
            # Если weight большой, то низкий score сильнее снижает вероятность
            weighted_score = score ** (weight * 2)
            base_probability *= weighted_score
        
        # Применяем сигмоидное сглаживание для реалистичности
        # Растения достаточно устойчивы, не умирают мгновенно
        survival = self._sigmoid(base_probability, midpoint=0.5, steepness=5)
        
        return max(0.0, min(1.0, survival))
    
    def _calculate_yield_forecast(self, parameter_scores: Dict[str, float], survival_probability: float) -> float:
        """
        Рассчитать прогноз урожайности относительно максимума
        
        Урожайность зависит от:
        1. Выживаемости (если растение умирает -> урожай 0)
        2. Всех параметров среды (нелинейная зависимость)
        3. Закона минимума Либиха (ограничивающий фактор)
        
        Математическая модель:
        yield = survival * f(params)
        где f(params) учитывает взаимодействие факторов
        
        Args:
            parameter_scores: Оценки параметров
            survival_probability: Вероятность выживания
            
        Returns:
            float: Прогноз урожайности (0-1, где 1=100% максимума)
        """
        # При низкой выживаемости урожая почти нет
        if survival_probability < 0.3:
            return survival_probability * 0.2
        
        # Закон минимума Либиха: урожай ограничен худшим фактором
        # Берем минимальную оценку (самый проблемный параметр)
        limiting_factor = min(parameter_scores.values())
        
        # Средняя оценка всех параметров (общее качество условий)
        average_score = sum(
            score * self.PARAMETER_WEIGHTS[param]
            for param, score in parameter_scores.items()
        ) / sum(self.PARAMETER_WEIGHTS.values())
        
        # Комбинируем с весами:
        # 60% - влияние ограничивающего фактора (закон Либиха)
        # 40% - влияние общего качества условий
        combined_score = 0.6 * limiting_factor + 0.4 * average_score
        
        # Применяем нелинейную функцию (степенная зависимость)
        # При идеальных условиях (score=1.0) -> yield=1.0
        # При средних условиях (score=0.7) -> yield=0.49 (серьезное снижение)
        # При плохих условиях (score=0.5) -> yield=0.25 (критическое снижение)
        base_yield = combined_score ** 1.5  # Степень > 1 создает нелинейность
        
        # Корректируем на выживаемость
        final_yield = base_yield * self._sigmoid(survival_probability, 0.6, 8)
        
        # Дополнительные штрафы за критичные параметры
        # pH и EC особенно важны для урожайности
        if parameter_scores['ph'] < 0.5:
            final_yield *= 0.7  # Штраф -30% за плохой pH
        if parameter_scores['ec'] < 0.5:
            final_yield *= 0.7  # Штраф -30% за плохой EC
        if parameter_scores['light_intensity'] < 0.5:
            final_yield *= 0.8  # Штраф -20% за недостаток света

        return max(0.0, min(1.0, final_yield))

    def _calculate_health_score(self, parameter_scores: Dict[str, float]) -> float:
        """
        Рассчитать общую оценку здоровья растения (0-100 баллов)
        
        Взвешенная средняя всех параметров с учетом их важности
        
        Args:
            parameter_scores: Оценки всех параметров
            
        Returns:
            float: Оценка здоровья (0-100 баллов)
        """
        # Взвешенная сумма всех оценок
        weighted_sum = sum(
            score * self.PARAMETER_WEIGHTS[param]
            for param, score in parameter_scores.items()
        )
        
        # Преобразуем в шкалу 0-100
        health_score = weighted_sum * 100
        
        return round(health_score, 1)
    
    def _identify_issues(
        self,
        current: EnvironmentParameters,
        requirements: CropRequirements,
        scores: Dict[str, float]
    ) -> Tuple[List[str], List[str]]:
        """
        Выявить критические проблемы и предупреждения
        
        Критические проблемы - параметры за пределами допустимого диапазона
        Предупреждения - параметры вне оптимума, но в допустимых пределах
        
        Args:
            current: Текущие параметры
            requirements: Требования культуры
            scores: Оценки параметров
            
        Returns:
            Tuple[List[str], List[str]]: (критические проблемы, предупреждения)
        """
        critical_issues = []
        warnings = []
        
        # Проверяем каждый параметр
        self._check_parameter(
            'Температура',
            current.temperature,
            requirements.temperature,
            scores['temperature'],
            'C',
            critical_issues,
            warnings
        )
        
        self._check_parameter(
            'Влажность',
            current.humidity,
            requirements.humidity,
            scores['humidity'],
            '%',
            critical_issues,
            warnings
        )
        
        self._check_parameter(
            'pH',
            current.ph,
            requirements.ph,
            scores['ph'],
            '',
            critical_issues,
            warnings
        )
        
        self._check_parameter(
            'EC',
            current.ec,
            requirements.ec,
            scores['ec'],
            'mS/cm',
            critical_issues,
            warnings
        )
        
        self._check_parameter(
            'Освещенность',
            current.light_intensity,
            requirements.light_intensity,
            scores['light_intensity'],
            'µmol/m²/s',
            critical_issues,
            warnings
        )
        
        self._check_parameter(
            'Световой день',
            current.light_hours,
            requirements.light_hours,
            scores['light_hours'],
            'ч',
            critical_issues,
            warnings
        )
        
        return critical_issues, warnings
    
    def _check_parameter(
        self,
        name: str,
        value: float,
        optimal_range: OptimalRange,
        score: float,
        unit: str,
        critical_issues: List[str],
        warnings: List[str]
    ):
        """
        Проверить один параметр и добавить соответствующие сообщения
        
        Args:
            name: Название параметра
            value: Текущее значение
            optimal_range: Оптимальный диапазон
            score: Оценка параметра
            unit: Единица измерения
            critical_issues: Список для добавления критических проблем
            warnings: Список для добавления предупреждений
        """
        # Критическая зона (за пределами допустимого)
        if value < optimal_range.min_acceptable:
            diff = optimal_range.min_acceptable - value
            
            if value <= optimal_range.critical_min:
                # За критической границей
                critical_issues.append(
                    f"КРИТИЧНО: {name} {value}{unit} - "
                    f"крайне низкое значение! Растение может погибнуть. "
                    f"Допустимый минимум: {optimal_range.min_acceptable}{unit}"
                )
            else:
                # Ниже допустимого
                critical_issues.append(
                    f"{name} {value}{unit} - ниже допустимого на {diff:.1f}{unit}. "
                    f"Требуется: минимум {optimal_range.min_acceptable}{unit}"
                )
        
        elif value > optimal_range.max_acceptable:
            diff = value - optimal_range.max_acceptable
            
            if value >= optimal_range.critical_max:
                # За критической границей
                critical_issues.append(
                    f"КРИТИЧНО: {name} {value}{unit} - "
                    f"крайне высокое значение! Растение может погибнуть. "
                    f"Допустимый максимум: {optimal_range.max_acceptable}{unit}"
                )
            else:
                # Выше допустимого
                critical_issues.append(
                    f"{name} {value}{unit} - выше допустимого на {diff:.1f}{unit}. "
                    f"Требуется: максимум {optimal_range.max_acceptable}{unit}"
                )
        
        # Предупреждения (отклонение от оптимума)
        elif value < optimal_range.min_optimal:
            diff = optimal_range.min_optimal - value
            impact = (1 - score) * 100
            warnings.append(
                f"{name} {value}{unit} - ниже оптимума на {diff:.1f}{unit}. "
                f"Снижение продуктивности на ~{impact:.0f}%. "
                f"Рекомендуется: {optimal_range.min_optimal}-{optimal_range.max_optimal}{unit}"
            )
        
        elif value > optimal_range.max_optimal:
            diff = value - optimal_range.max_optimal
            impact = (1 - score) * 100
            warnings.append(
                f"{name} {value}{unit} - выше оптимума на {diff:.1f}{unit}. "
                f"Снижение продуктивности на ~{impact:.0f}%. "
                f"Рекомендуется: {optimal_range.min_optimal}-{optimal_range.max_optimal}{unit}"
            )
    
    def _generate_recommendations(
        self,
        current: EnvironmentParameters,
        requirements: CropRequirements,
        scores: Dict[str, float],
        critical_issues: List[str],
        warnings: List[str]
    ) -> List[str]:
        """
        Сгенерировать конкретные рекомендации по исправлению проблем
        
        Приоритет:
        1. Критические проблемы (угроза жизни растения)
        2. Важные отклонения (снижение урожая)
        3. Оптимизация (улучшение условий)
        
        Args:
            current: Текущие параметры
            requirements: Требования
            scores: Оценки параметров
            critical_issues: Критические проблемы
            warnings: Предупреждения
            
        Returns:
            List[str]: Список практических рекомендаций
        """
        recommendations = []
        
        # Если все отлично
        if not critical_issues and not warnings:
            recommendations.append(
                "Все параметры в оптимальном диапазоне! "
                "Продолжайте поддерживать текущие условия."
            )
            return recommendations
        
        # Сортируем параметры по приоритету (худшие первыми)
        sorted_params = sorted(scores.items(), key=lambda x: x[1])
        
        # Генерируем рекомендации для проблемных параметров
        for param_name, score in sorted_params:
            if score < 0.8:  # Есть проблема
                rec = self._get_parameter_recommendation(
                    param_name, current, requirements, score
                )
                if rec:
                    recommendations.append(rec)
        
        # Добавляем общую рекомендацию при критических проблемах
        if len(critical_issues) > 0:
            recommendations.insert(0,
                "СРОЧНО: Обнаружены критические проблемы! "
                "Немедленно исправьте параметры, иначе растение погибнет."
            )
        
        return recommendations
    
    def _get_parameter_recommendation(
        self,
        param_name: str,
        current: EnvironmentParameters,
        requirements: CropRequirements,
        score: float
    ) -> str:
        """
        Получить конкретную рекомендацию для одного параметра
        
        Args:
            param_name: Название параметра
            current: Текущие параметры
            requirements: Требования
            score: Оценка параметра
            
        Returns:
            str: Текст рекомендации или пустая строка
        """
        # Словарь: параметр -> (значение, диапазон, единица, отображаемое имя)
        param_map = {
            'temperature': (current.temperature, requirements.temperature, 'C', 'температуру'),
            'humidity': (current.humidity, requirements.humidity, '%', 'влажность'),
            'ph': (current.ph, requirements.ph, '', 'pH'),
            'ec': (current.ec, requirements.ec, 'mS/cm', 'EC'),
            'light_intensity': (current.light_intensity, requirements.light_intensity, 'µmol/m²/s', 'освещенность'),
            'light_hours': (current.light_hours, requirements.light_hours, 'ч', 'световой день')
        }
        
        if param_name not in param_map:
            return ""
        
        value, optimal, unit, display_name = param_map[param_name]
        
        # Целевое значение (центр оптимального диапазона)
        target = (optimal.min_optimal + optimal.max_optimal) / 2
        
        # Определяем направление действия
        if value < optimal.min_optimal:
            action = "Повысьте"
            diff = target - value
        elif value > optimal.max_optimal:
            action = "Снизьте"
            diff = value - target
        else:
            return ""  # В оптимальном диапазоне
        
        # Уровень срочности
        urgency = "СРОЧНО:" if score < 0.5 else "Рекомендуется:"
        
        # Формируем рекомендацию
        recommendation = (
            f"{urgency} {action} {display_name} до "
            f"{optimal.min_optimal}-{optimal.max_optimal}{unit} "
            f"(текущее: {value}{unit}, оптимум: {target:.1f}{unit}). "
        )
        
        # Добавляем методы коррекции
        methods = self._get_correction_methods(param_name, value < optimal.min_optimal)
        if methods:
            recommendation += f"Способ: {methods}"
        
        return recommendation
    
    def _get_correction_methods(self, param_name: str, is_low: bool) -> str:
        """
        Получить практические методы коррекции параметра
        
        Args:
            param_name: Название параметра
            is_low: True если значение низкое, False если высокое
            
        Returns:
            str: Описание методов коррекции
        """
        methods = {
            'temperature': {
                True: "включите обогрев, закройте вентиляцию, используйте тепловые маты",
                False: "включите вентиляцию/кондиционер, притените, увеличьте испарение"
            },
            'humidity': {
                True: "используйте увлажнитель воздуха, распыляйте воду, уменьшите вентиляцию",
                False: "включите вентиляцию, используйте осушитель, увеличьте циркуляцию воздуха"
            },
            'ph': {
                True: "добавьте pH-Up (гидроксид калия), используйте буферные растворы",
                False: "добавьте pH-Down (фосфорная кислота), проверьте качество воды"
            },
            'ec': {
                True: "добавьте комплексное удобрение (NPK), увеличьте концентрацию раствора",
                False: "разбавьте раствор чистой водой, замените раствор полностью"
            },
            'light_intensity': {
                True: "установите дополнительные LED-лампы, приблизьте светильники к растениям",
                False: "поднимите светильники выше, уменьшите мощность ламп, используйте притенение"
            },
            'light_hours': {
                True: "увеличьте продолжительность освещения (используйте таймер)",
                False: "сократите световой день (установите таймер на меньший период)"
            }
        }
        
        return methods.get(param_name, {}).get(is_low, "")
    
    def _calculate_optimal_parameters(
        self,
        requirements: CropRequirements
    ) -> EnvironmentParameters:
        """
        Вычислить оптимальные (целевые) параметры среды
        
        Берет центр оптимального диапазона для каждого параметра
        
        Args:
            requirements: Требования культуры
            
        Returns:
            EnvironmentParameters: Оптимальные параметры
        """
        return EnvironmentParameters(
            temperature=(requirements.temperature.min_optimal + requirements.temperature.max_optimal) / 2,
            humidity=(requirements.humidity.min_optimal + requirements.humidity.max_optimal) / 2,
            ph=(requirements.ph.min_optimal + requirements.ph.max_optimal) / 2,
            ec=(requirements.ec.min_optimal + requirements.ec.max_optimal) / 2,
            light_intensity=(requirements.light_intensity.min_optimal + requirements.light_intensity.max_optimal) / 2,
            light_hours=(requirements.light_hours.min_optimal + requirements.light_hours.max_optimal) / 2
        )
    
    def _sigmoid(self, x: float, midpoint: float = 0.5, steepness: float = 10) -> float:
        """
        Сигмоидная функция для сглаживания
        
        Преобразует линейную зависимость в S-образную кривую.
        Используется для моделирования постепенных переходов.
        
        Args:
            x: Входное значение (обычно 0-1)
            midpoint: Точка перегиба кривой (центр S-образной кривой)
            steepness: Крутизна кривой (больше = резче переход)
            
        Returns:
            float: Выходное значение (0-1)
        """
        try:
            return 1 / (1 + math.exp(-steepness * (x - midpoint)))
        except OverflowError:
            # Обработка переполнения при очень больших/маленьких значениях
            return 0.0 if x < midpoint else 1.0