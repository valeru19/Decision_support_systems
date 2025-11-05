
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
    AirParameters,
    LightParameters,
    SolutionParameters,
    CropRequirements,
    StageRequirements,
    GrowthStage,
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
        # Воздух
        'temperature': 0.12,           # Температура критично важна
        'humidity': 0.08,              # Влажность влияет на транспирацию
        'atmospheric_pressure': 0.05,  # Влияет на газообмен
        # Свет
        'wavelength': 0.08,            # Соответствие спектра задаче стадии
        'energy': 0.10,                # Интенсивность света
        'hours': 0.07,                 # Длительность светового дня
        # Раствор (питание)
        'nitrogen': 0.12,              # Рост зелёной массы
        'phosphorus': 0.08,            # Корневая система и цветение
        'potassium': 0.12,             # Качество плодов и стрессоустойчивость
        'calcium': 0.08,               # Клеточные стенки, верш. гниль
        'magnesium': 0.05,             # Хлорофилл
        'iron': 0.05                   # Микроэлемент для фотосинтеза
    }
    
    def __init__(self):
        """Инициализация движка анализа"""
        pass
    
    def analyze(
        self,
        current_params: EnvironmentParameters,
        requirements: CropRequirements,
        stage: GrowthStage
    ) -> AnalysisResult:
        """
        Провести полный анализ текущих условий выращивания
        
        Args:
            current_params: Текущие параметры среды
            requirements: Требования культуры к условиям
            stage: Стадия роста, для которой проводится анализ
            
        Returns:
            AnalysisResult: Полный результат анализа с оценками и рекомендациями
        """
        # Получаем требования для конкретной стадии
        stage_reqs: StageRequirements = requirements.stages[stage]
        
        # Шаг 1: Рассчитываем оценки для каждого параметра (0-1)
        parameter_scores = self._calculate_parameter_scores(current_params, stage_reqs)
        
        # Шаг 2: Рассчитываем вероятность выживания
        # Критичные отклонения приводят к низкой выживаемости
        survival_probability = self._calculate_survival_probability(parameter_scores)
        
        # Шаг 3: Рассчитываем прогноз урожайности
        # Учитывается нелинейная зависимость от всех параметров
        yield_forecast = self._calculate_yield_forecast(parameter_scores, survival_probability)

        # 3.2 Максимальный урожай для данной стадии
        max_yield_kg_per_m2 = yield_forecast * stage_reqs.max_yield_kg_per_m2
        
        # Шаг 4: Рассчитываем общую оценку здоровья (0-100)
        health_score = self._calculate_health_score(parameter_scores)
        
        # Шаг 5: Определяем проблемы и предупреждения
        critical_issues, warnings = self._identify_issues(
            current_params, stage_reqs, parameter_scores
        )
        
        # Шаг 6: Генерируем конкретные рекомендации
        recommendations = self._generate_recommendations(
            current_params, stage_reqs, parameter_scores, critical_issues, warnings
        )
        
        # Шаг 7: Вычисляем оптимальные параметры (центр оптимального диапазона)
        optimal_parameters = self._calculate_optimal_parameters(stage_reqs)
        
        return AnalysisResult(
            stage=stage,
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
        stage_reqs: StageRequirements
    ) -> Dict[str, float]:
        """
        Рассчитать оценку качества для каждого параметра
        
        Оценка показывает насколько текущее значение близко к оптимуму:
        1.0 = идеально (в оптимальном диапазоне)
        0.5-0.99 = допустимо (есть отклонение, но не критично)
        0.0-0.49 = критично (серьезное отклонение)
        
        Args:
            current: Текущие параметры среды
            stage_reqs: Требования культуры для текущей стадии
            
        Returns:
            Dict[str, float]: Словарь с оценками для каждого параметра
        """
        scores = {}
        
        # Воздух
        deviation = stage_reqs.air.temperature.get_deviation(current.air.temperature)
        scores['temperature'] = self._deviation_to_score(deviation)
        
        deviation = stage_reqs.air.humidity.get_deviation(current.air.humidity)
        scores['humidity'] = self._deviation_to_score(deviation)
        
        deviation = stage_reqs.air.atmospheric_pressure.get_deviation(current.air.atmospheric_pressure)
        scores['atmospheric_pressure'] = self._deviation_to_score(deviation)
        
        # Свет
        deviation = stage_reqs.light.wavelength.get_deviation(current.light.wavelength)
        scores['wavelength'] = self._deviation_to_score(deviation)
        
        deviation = stage_reqs.light.energy.get_deviation(current.light.energy)
        scores['energy'] = self._deviation_to_score(deviation)
        
        deviation = stage_reqs.light.hours.get_deviation(current.light.hours)
        scores['hours'] = self._deviation_to_score(deviation)
        
        # Раствор
        deviation = stage_reqs.solution.nitrogen.get_deviation(current.solution.nitrogen)
        scores['nitrogen'] = self._deviation_to_score(deviation)
        
        deviation = stage_reqs.solution.phosphorus.get_deviation(current.solution.phosphorus)
        scores['phosphorus'] = self._deviation_to_score(deviation)
        
        deviation = stage_reqs.solution.potassium.get_deviation(current.solution.potassium)
        scores['potassium'] = self._deviation_to_score(deviation)
        
        deviation = stage_reqs.solution.calcium.get_deviation(current.solution.calcium)
        scores['calcium'] = self._deviation_to_score(deviation)
        
        deviation = stage_reqs.solution.magnesium.get_deviation(current.solution.magnesium)
        scores['magnesium'] = self._deviation_to_score(deviation)
        
        deviation = stage_reqs.solution.iron.get_deviation(current.solution.iron)
        scores['iron'] = self._deviation_to_score(deviation)
        
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
        # Если все параметры идеальны, вероятность выживания должна быть 1.0
        if all(abs(score - 1.0) < 1e-9 for score in parameter_scores.values()):
            return 1.0

        survival = self._sigmoid01(base_probability, midpoint=0.5, steepness=5)
        
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
        final_yield = base_yield * self._sigmoid01(survival_probability, 0.6, 8)
        
        # Дополнительные штрафы за критичные параметры
        # Ключевые факторы: питание (N, K), освещение (энергия)
        if parameter_scores.get('nitrogen', 1.0) < 0.5:
            final_yield *= 0.75  # Штраф -25% за дефицит азота
        if parameter_scores.get('potassium', 1.0) < 0.5:
            final_yield *= 0.80  # Штраф -20% за дефицит калия
        if parameter_scores.get('energy', 1.0) < 0.5:
            final_yield *= 0.80  # Штраф -20% за недостаток энергии света

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
        stage_reqs: StageRequirements,
        scores: Dict[str, float]
    ) -> Tuple[List[str], List[str]]:
        """
        Выявить критические проблемы и предупреждения
        
        Критические проблемы - параметры за пределами допустимого диапазона
        Предупреждения - параметры вне оптимума, но в допустимых пределах
        
        Args:
            current: Текущие параметры
            stage_reqs: Требования культуры
            scores: Оценки параметров
            
        Returns:
            Tuple[List[str], List[str]]: (критические проблемы, предупреждения)
        """
        critical_issues = []
        warnings = []
        
        # Воздух
        self._check_parameter(
            'Температура',
            current.air.temperature,
            stage_reqs.air.temperature,
            scores['temperature'],
            '°C',
            critical_issues,
            warnings
        )
        
        self._check_parameter(
            'Влажность',
            current.air.humidity,
            stage_reqs.air.humidity,
            scores['humidity'],
            '%',
            critical_issues,
            warnings
        )
        
        self._check_parameter(
            'Давление',
            current.air.atmospheric_pressure,
            stage_reqs.air.atmospheric_pressure,
            scores['atmospheric_pressure'],
            ' мм рт. ст.',
            critical_issues,
            warnings
        )
        
        # Свет
        self._check_parameter(
            'Длина волны',
            current.light.wavelength,
            stage_reqs.light.wavelength,
            scores['wavelength'],
            ' нм',
            critical_issues,
            warnings
        )
        
        self._check_parameter(
            'Энергия света',
            current.light.energy,
            stage_reqs.light.energy,
            scores['energy'],
            ' Вт/м²',
            critical_issues,
            warnings
        )
        
        self._check_parameter(
            'Световой день',
            current.light.hours,
            stage_reqs.light.hours,
            scores['hours'],
            ' ч',
            critical_issues,
            warnings
        )
        
        # Раствор
        self._check_parameter(
            'Азот (N)',
            current.solution.nitrogen,
            stage_reqs.solution.nitrogen,
            scores['nitrogen'],
            ' мг/л',
            critical_issues,
            warnings
        )
        
        self._check_parameter(
            'Фосфор (P)',
            current.solution.phosphorus,
            stage_reqs.solution.phosphorus,
            scores['phosphorus'],
            ' мг/л',
            critical_issues,
            warnings
        )
        
        self._check_parameter(
            'Калий (K)',
            current.solution.potassium,
            stage_reqs.solution.potassium,
            scores['potassium'],
            ' мг/л',
            critical_issues,
            warnings
        )
        
        self._check_parameter(
            'Кальций (Ca)',
            current.solution.calcium,
            stage_reqs.solution.calcium,
            scores['calcium'],
            ' мг/л',
            critical_issues,
            warnings
        )
        
        self._check_parameter(
            'Магний (Mg)',
            current.solution.magnesium,
            stage_reqs.solution.magnesium,
            scores['magnesium'],
            ' мг/л',
            critical_issues,
            warnings
        )
        
        self._check_parameter(
            'Железо (Fe)',
            current.solution.iron,
            stage_reqs.solution.iron,
            scores['iron'],
            ' мг/л',
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
        stage_reqs: StageRequirements,
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
                    param_name, current, stage_reqs, score
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
        stage_reqs: StageRequirements,
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
            # Воздух
            'temperature': (current.air.temperature, stage_reqs.air.temperature, '°C', 'температуру'),
            'humidity': (current.air.humidity, stage_reqs.air.humidity, '%', 'влажность'),
            'atmospheric_pressure': (current.air.atmospheric_pressure, stage_reqs.air.atmospheric_pressure, ' мм рт. ст.', 'давление'),
            # Свет
            'wavelength': (current.light.wavelength, stage_reqs.light.wavelength, ' нм', 'длину волны'),
            'energy': (current.light.energy, stage_reqs.light.energy, ' Вт/м²', 'энергию света'),
            'hours': (current.light.hours, stage_reqs.light.hours, ' ч', 'световой день'),
            # Раствор
            'nitrogen': (current.solution.nitrogen, stage_reqs.solution.nitrogen, ' мг/л', 'азот (N)'),
            'phosphorus': (current.solution.phosphorus, stage_reqs.solution.phosphorus, ' мг/л', 'фосфор (P)'),
            'potassium': (current.solution.potassium, stage_reqs.solution.potassium, ' мг/л', 'калий (K)'),
            'calcium': (current.solution.calcium, stage_reqs.solution.calcium, ' мг/л', 'кальций (Ca)'),
            'magnesium': (current.solution.magnesium, stage_reqs.solution.magnesium, ' мг/л', 'магний (Mg)'),
            'iron': (current.solution.iron, stage_reqs.solution.iron, ' мг/л', 'железо (Fe)')
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
            # Воздух
            'temperature': {
                True: "включите обогрев, закройте вентиляцию, используйте тепловые маты",
                False: "включите вентиляцию/кондиционер, притените, увеличьте испарение"
            },
            'humidity': {
                True: "используйте увлажнитель воздуха, распыляйте воду, уменьшите вентиляцию",
                False: "включите вентиляцию, используйте осушитель, увеличьте циркуляцию воздуха"
            },
            'atmospheric_pressure': {
                True: "проверьте герметичность помещения, уменьшите интенсивность вытяжки; параметр в основном справочный",
                False: "проветрите помещение, нормализуйте вентиляцию; параметр в основном справочный"
            },
            # Свет
            'wavelength': {
                True: "используйте светильники с более короткой длиной волны (синяя область), отрегулируйте спектр LED",
                False: "используйте светильники с большей долей красного спектра, настройте спектр LED"
            },
            'energy': {
                True: "установите дополнительные LED-лампы/увеличьте мощность, уменьшите расстояние до растений",
                False: "уменьшите мощность/увеличьте расстояние, примените притенение"
            },
            'hours': {
                True: "увеличьте продолжительность освещения с помощью таймера",
                False: "сократите продолжительность освещения (настройте таймер)"
            },
            # Раствор (питательные элементы)
            'nitrogen': {
                True: "добавьте азотсодержащее удобрение (N), увеличьте долю N в растворе",
                False: "разбавьте раствор чистой водой или уменьшите дозу удобрения с азотом"
            },
            'phosphorus': {
                True: "добавьте удобрение с фосфором (P), используйте монофосфат",
                False: "разбавьте раствор водой, уменьшите внесение фосфора"
            },
            'potassium': {
                True: "добавьте удобрение с калием (K), сульфат калия",
                False: "разбавьте раствор водой, уменьшите дозу калийных удобрений"
            },
            'calcium': {
                True: "добавьте кальциевую селитру, скорректируйте Ca",
                False: "разбавьте раствор водой, сократите источники кальция"
            },
            'magnesium': {
                True: "добавьте сульфат магния (MgSO4), повышайте Mg постепенно",
                False: "разбавьте раствор водой, уменьшите источники магния"
            },
            'iron': {
                True: "добавьте хелат железа (Fe-EDDHA/Fe-DTPA) согласно инструкции",
                False: "разбавьте раствор водой, временно прекратите внесение железа"
            }
        }
        
        return methods.get(param_name, {}).get(is_low, "")
    
    def _calculate_optimal_parameters(
        self,
        stage_reqs: StageRequirements
    ) -> EnvironmentParameters:
        """
        Вычислить оптимальные (целевые) параметры среды
        
        Берет центр оптимального диапазона для каждого параметра на текущей стадии
        
        Args:
            stage_reqs: Требования культуры на конкретной стадии
            
        Returns:
            EnvironmentParameters: Оптимальные параметры
        """
        air = AirParameters(
            temperature=(stage_reqs.air.temperature.min_optimal + stage_reqs.air.temperature.max_optimal) / 2,
            humidity=(stage_reqs.air.humidity.min_optimal + stage_reqs.air.humidity.max_optimal) / 2,
            atmospheric_pressure=(stage_reqs.air.atmospheric_pressure.min_optimal + stage_reqs.air.atmospheric_pressure.max_optimal) / 2
        )
        light = LightParameters(
            wavelength=(stage_reqs.light.wavelength.min_optimal + stage_reqs.light.wavelength.max_optimal) / 2,
            energy=(stage_reqs.light.energy.min_optimal + stage_reqs.light.energy.max_optimal) / 2,
            hours=(stage_reqs.light.hours.min_optimal + stage_reqs.light.hours.max_optimal) / 2
        )
        solution = SolutionParameters(
            nitrogen=(stage_reqs.solution.nitrogen.min_optimal + stage_reqs.solution.nitrogen.max_optimal) / 2,
            phosphorus=(stage_reqs.solution.phosphorus.min_optimal + stage_reqs.solution.phosphorus.max_optimal) / 2,
            potassium=(stage_reqs.solution.potassium.min_optimal + stage_reqs.solution.potassium.max_optimal) / 2,
            calcium=(stage_reqs.solution.calcium.min_optimal + stage_reqs.solution.calcium.max_optimal) / 2,
            magnesium=(stage_reqs.solution.magnesium.min_optimal + stage_reqs.solution.magnesium.max_optimal) / 2,
            iron=(stage_reqs.solution.iron.min_optimal + stage_reqs.solution.iron.max_optimal) / 2
        )
        return EnvironmentParameters(air=air, light=light, solution=solution)
    
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

    def _sigmoid01(self, x: float, midpoint: float = 0.5, steepness: float = 10) -> float:
        """
        Нормализованная сигмоида на отрезке [0,1].
        В отличие от _sigmoid гарантирует значения s(0)=0 и s(1)=1,
        что важно для корректной интерпретации идеальных условий.
        """
        # Базовое значение
        y = self._sigmoid(x, midpoint, steepness)
        y0 = self._sigmoid(0.0, midpoint, steepness)
        y1 = self._sigmoid(1.0, midpoint, steepness)
        # Избежать деления на ноль, если параметры подобраны неудачно
        if abs(y1 - y0) < 1e-9:
            return max(0.0, min(1.0, y))
        norm = (y - y0) / (y1 - y0)
        # Численная стабильность
        if norm < 0.0:
            return 0.0
        if norm > 1.0:
            return 1.0
        return norm