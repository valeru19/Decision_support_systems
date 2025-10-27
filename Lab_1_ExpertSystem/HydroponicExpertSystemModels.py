"""
Модели данных для экспертной системы гидропоники

Содержит основные классы для представления:
- Типов культур
- Параметров окружающей среды
- Оптимальных диапазонов параметров
- Требований культур к условиям
- Результатов анализа
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class CropType(Enum):
    """
    Перечисление типов сельскохозяйственных культур

    Поддерживаемые культуры для гидропонного выращивания
    """
    TOMATO = "томат"
    CUCUMBER = "огурец"
    LETTUCE = "салат"
    STRAWBERRY = "клубника"
    PEPPER = "перец"
    BASIL = "базилик"


@dataclass
class EnvironmentParameters:
    """
    Текущие параметры окружающей среды в гидропонной системе

    Attributes:
        temperature: Температура воздуха в градусах Цельсия (C)
        humidity: Относительная влажность воздуха в процентах (%)
        ph: Кислотность питательного раствора (pH)
        ec: Электропроводность раствора в миллисименсах на см (mS/cm)
            Показывает общую концентрацию растворенных солей (удобрений)
        light_intensity: Интенсивность света в микромолях на м² в секунду (µmol/m²/s)
            PPFD - Photosynthetic Photon Flux Density
        light_hours: Продолжительность светового дня в часах
        co2: Концентрация углекислого газа в ppm (необязательно)
        water_temperature: Температура питательного раствора в C (необязательно)
    """
    temperature: float
    humidity: float
    ph: float
    ec: float
    light_intensity: float
    light_hours: float
    co2: Optional[float] = None
    water_temperature: Optional[float] = None

    def __post_init__(self):
        """
        Автоматическая валидация параметров после создания объекта
        """
        self._validate()

    def _validate(self):
        """
        Проверка корректности значений всех параметров

        Raises:
            ValueError: Если хотя бы один параметр выходит за допустимые пределы
        """
        if not 0 <= self.temperature <= 50:
            raise ValueError(
                f"Температура {self.temperature}C вне допустимого диапазона (0-50C)"
            )

        if not 0 <= self.humidity <= 100:
            raise ValueError(
                f"Влажность {self.humidity}% вне допустимого диапазона (0-100%)"
            )

        if not 0 <= self.ph <= 14:
            raise ValueError(
                f"pH {self.ph} вне допустимого диапазона (0-14)"
            )

        if not 0 <= self.ec <= 10:
            raise ValueError(
                f"EC {self.ec} вне допустимого диапазона (0-10 mS/cm)"
            )

        if not 0 <= self.light_intensity <= 2000:
            raise ValueError(
                f"Освещенность {self.light_intensity} вне допустимого диапазона (0-2000 µmol/m²/s)"
            )

        if not 0 <= self.light_hours <= 24:
            raise ValueError(
                f"Световой день {self.light_hours}ч вне допустимого диапазона (0-24ч)"
            )


@dataclass
class OptimalRange:
    """
    Оптимальный диапазон значений для одного параметра

    Определяет три уровня допустимости:
    1. Оптимальный диапазон (min_optimal - max_optimal)
       Растение развивается идеально
    2. Допустимый диапазон (min_acceptable - max_acceptable)
       Растение развивается нормально, но не оптимально
    3. Критический диапазон (critical_min - critical_max)
       За этими пределами растение погибает

    Attributes:
        min_optimal: Минимальное оптимальное значение
        max_optimal: Максимальное оптимальное значение
        min_acceptable: Минимальное допустимое значение
        max_acceptable: Максимальное допустимое значение
        critical_min: Критический минимум (ниже - гибель)
        critical_max: Критический максимум (выше - гибель)
    """
    min_optimal: float
    max_optimal: float
    min_acceptable: float
    max_acceptable: float
    critical_min: float
    critical_max: float

    def get_deviation(self, value: float) -> float:
        """
        Вычисляет степень отклонения текущего значения от оптимума

        Использует нелинейную функцию для расчета отклонения:
        - В оптимальном диапазоне: отклонение = 0.0 (идеально)
        - В допустимом диапазоне: отклонение = 0.0-0.5 (приемлемо)
        - За допустимым диапазоном: отклонение = 0.5-1.0 (критично)
        - За критическим диапазоном: отклонение = 1.0 (гибель)

        Args:
            value: Текущее значение параметра

        Returns:
            float: Степень отклонения (0.0 = идеально, 1.0 = критично)
        """
        # Проверка: в оптимальном диапазоне
        if self.min_optimal <= value <= self.max_optimal:
            return 0.0

        # Проверка: ниже оптимума, но в допустимых пределах
        elif self.min_acceptable <= value < self.min_optimal:
            deviation_ratio = (self.min_optimal - value) / (self.min_optimal - self.min_acceptable)
            return deviation_ratio * 0.5

        # Проверка: выше оптимума, но в допустимых пределах
        elif self.max_optimal < value <= self.max_acceptable:
            deviation_ratio = (value - self.max_optimal) / (self.max_acceptable - self.max_optimal)
            return deviation_ratio * 0.5

        # Проверка: ниже допустимого, но не за критической границей
        elif self.critical_min <= value < self.min_acceptable:
            deviation_ratio = (self.min_acceptable - value) / (self.min_acceptable - self.critical_min)
            return 0.5 + deviation_ratio * 0.5

        # Проверка: выше допустимого, но не за критической границей
        elif self.max_acceptable < value <= self.critical_max:
            deviation_ratio = (value - self.max_acceptable) / (self.critical_max - self.max_acceptable)
            return 0.5 + deviation_ratio * 0.5

        # За критическими пределами
        else:
            return 1.0


@dataclass
class CropRequirements:
    """
    Требования конкретной культуры к условиям выращивания

    Представляет "знания" экспертной системы о том, какие условия
    необходимы растению для оптимального роста и развития.

    Каждый параметр описывается через OptimalRange, который определяет:
    - Идеальные условия для максимального урожая
    - Допустимые условия для нормального развития
    - Критические границы выживаемости

    Attributes:
        crop_type: Тип культуры
        temperature: Диапазон температуры воздуха
        humidity: Диапазон влажности воздуха
        ph: Диапазон кислотности раствора
        ec: Диапазон электропроводности (концентрации удобрений)
        light_intensity: Диапазон интенсивности освещения
        light_hours: Диапазон продолжительности светового дня
    """
    crop_type: CropType
    temperature: OptimalRange
    humidity: OptimalRange
    ph: OptimalRange
    ec: OptimalRange
    light_intensity: OptimalRange
    light_hours: OptimalRange
    max_yield_kg_per_m2: float


@dataclass
class AnalysisResult:
    """
    Результат анализа текущих условий выращивания

    Содержит все данные, полученные в результате сравнения
    текущих параметров среды с требованиями выбранной культуры.

    Включает:
    - Количественные оценки (выживаемость, урожайность, здоровье)
    - Качественные оценки (проблемы, предупреждения)
    - Практические рекомендации по улучшению условий
    - Целевые параметры для достижения оптимума

    Attributes:
        survival_probability: Вероятность выживания растения (0.0-1.0)
            0.0-0.3: критическое состояние, высокий риск гибели
            0.3-0.6: высокий стресс, возможны необратимые повреждения
            0.6-0.8: умеренный стресс, растение ослаблено
            0.8-1.0: хорошие условия, растение здорово

        yield_forecast: Прогноз урожайности относительно максимума (0.0-1.0)
            0.0: урожая не будет (растение погибает)
            0.5: половина от потенциального урожая
            1.0: максимальный урожай (идеальные условия)

        health_score: Общая оценка здоровья растения (0-100 баллов)
            90-100: отличное состояние
            70-89: хорошее состояние
            50-69: удовлетворительное (есть проблемы)
            30-49: плохое (серьезные проблемы)
            0-29: критическое (на грани гибели)

        critical_issues: Список критических проблем
            Проблемы, требующие немедленного решения

        warnings: Список предупреждений
            Отклонения от оптимума, снижающие продуктивность

        recommendations: Список конкретных рекомендаций
            Практические советы по исправлению ситуации

        optimal_parameters: Целевые (оптимальные) параметры
            К каким значениям нужно стремиться

        parameter_scores: Оценки по каждому параметру (0.0-1.0)
            Детализация: какой именно параметр проблемный
            1.0 = идеально, 0.5 = допустимо, 0.0 = критично
    """
    survival_probability: float
    yield_forecast: float
    max_yield_kg_per_m2: float
    health_score: float
    critical_issues: list[str]
    warnings: list[str]
    recommendations: list[str]
    optimal_parameters: EnvironmentParameters
    parameter_scores: dict[str, float]

    def get_status_text(self) -> str:
        """
        Получить текстовое описание общего статуса растения

        Returns:
            str: Статус ("Отлично", "Хорошо", "Удовлетворительно", "Плохо", "Критично")
        """
        if self.health_score >= 90:
            return "Отлично"
        elif self.health_score >= 70:
            return "Хорошо"
        elif self.health_score >= 50:
            return "Удовлетворительно"
        elif self.health_score >= 30:
            return "Плохо"
        else:
            return "Критично"

    def get_yield_percentage(self) -> float:
        """
        Получить прогноз урожайности в процентах

        Returns:
            float: Процент от максимального урожая (0-100)
        """
        return self.yield_forecast * 100

    def get_survival_percentage(self) -> float:
        """
        Получить вероятность выживания в процентах

        Returns:
            float: Процент вероятности выживания (0-100)
        """
        return self.survival_probability * 100

    def has_critical_issues(self) -> bool:
        """
        Проверить наличие критических проблем

        Returns:
            bool: True если есть критические проблемы, False если нет
        """
        return len(self.critical_issues) > 0

    def get_worst_parameter(self) -> tuple[str, float]:
        """
        Найти параметр с наихудшей оценкой

        Returns:
            tuple: (название параметра, оценка)
        """
        if not self.parameter_scores:
            return ("нет данных", 0.0)

        worst_param = min(self.parameter_scores.items(), key=lambda x: x[1])
        return worst_param

    def get_best_parameter(self) -> tuple[str, float]:
        """
        Найти параметр с лучшей оценкой

        Returns:
            tuple: (название параметра, оценка)
        """
        if not self.parameter_scores:
            return ("нет данных", 0.0)

        best_param = max(self.parameter_scores.items(), key=lambda x: x[1])
        return best_param