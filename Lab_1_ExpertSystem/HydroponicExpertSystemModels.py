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
from typing import Optional, Dict
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

class GrowthStage(Enum):
    """
    Перечисление стадий роста растений
    Поддерживаемые стадии для настройки параметров:
    - SEEDLING: Стадия рассады (начальный рост)
    - VEGETATIVE: Вегетативная стадия (рост листьев и стеблей)
    - FRUITING: Стадия цветения и плодоношения
    """
    SEEDLING = "рассада"
    VEGETATIVE = "вегетация"
    FRUITING = "плодоношение"

@dataclass
class AirParameters:
    """
    Параметры воздушной среды

    Attributes:
        temperature: Температура воздуха в °C
        humidity: Относительная влажность в %
        atmospheric_pressure: Атмосферное давление в мм рт. ст.
    """
    temperature: float
    humidity: float
    atmospheric_pressure: float

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
                f"Температура {self.temperature}°C вне допустимого диапазона (0-50°C)"
            )
        if not 0 <= self.humidity <= 100:
            raise ValueError(
                f"Влажность {self.humidity}% вне допустимого диапазона (0-100%)"
            )
        if not 500 <= self.atmospheric_pressure <= 1000:
            raise ValueError(
                f"Атмосферное давление {self.atmospheric_pressure} мм рт. ст. вне допустимого диапазона (500-1000 мм рт. ст.)"
            )

@dataclass
class LightParameters:
    """
    Параметры освещения

    Attributes:
        wavelength: Длина волны света в нм (спектр; для упрощения моделируется как средняя длина волны, но может быть расширено на список для полного спектра)
        energy: Энергия света в Вт/м² (заменяет PPFD; может быть скорректировано для PAR или других метрик)
        hours: Продолжительность светового дня в часах
    """
    wavelength: float
    energy: float
    hours: float

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
        if not 400 <= self.wavelength <= 700:  # Типичный диапазон видимого света для фотосинтеза (PAR)
            raise ValueError(
                f"Длина волны {self.wavelength} нм вне допустимого диапазона (400-700 нм)"
            )
        if not 0 <= self.energy <= 1000:  # Примерные пределы для искусственного освещения в гидропонике
            raise ValueError(
                f"Энергия света {self.energy} Вт/м² вне допустимого диапазона (0-1000 Вт/м²)"
            )
        if not 0 <= self.hours <= 24:
            raise ValueError(
                f"Световой день {self.hours} ч вне допустимого диапазона (0-24 ч)"
            )

@dataclass
class SolutionParameters:
    """
    Химические параметры питательного раствора (в мг/л)

    Attributes:
        nitrogen: Концентрация азота (N)
        phosphorus: Концентрация фосфора (P)
        potassium: Концентрация калия (K)
        calcium: Концентрация кальция (Ca)
        magnesium: Концентрация магния (Mg)
        iron: Концентрация железа (Fe)
    """
    nitrogen: float
    phosphorus: float
    potassium: float
    calcium: float
    magnesium: float
    iron: float

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
        # Примерные разумные пределы для концентраций в гидропонике (мг/л); эти значения основаны на типичных агрономических данных и могут быть скорректированы
        if not 0 <= self.nitrogen <= 300:
            raise ValueError(
                f"Концентрация азота {self.nitrogen} мг/л вне допустимого диапазона (0-300 мг/л)"
            )
        if not 0 <= self.phosphorus <= 100:
            raise ValueError(
                f"Концентрация фосфора {self.phosphorus} мг/л вне допустимого диапазона (0-100 мг/л)"
            )
        if not 0 <= self.potassium <= 400:
            raise ValueError(
                f"Концентрация калия {self.potassium} мг/л вне допустимого диапазона (0-400 мг/л)"
            )
        if not 0 <= self.calcium <= 250:
            raise ValueError(
                f"Концентрация кальция {self.calcium} мг/л вне допустимого диапазона (0-250 мг/л)"
            )
        if not 0 <= self.magnesium <= 100:
            raise ValueError(
                f"Концентрация магния {self.magnesium} мг/л вне допустимого диапазона (0-100 мг/л)"
            )
        if not 0 <= self.iron <= 10:
            raise ValueError(
                f"Концентрация железа {self.iron} мг/л вне допустимого диапазона (0-10 мг/л)"
            )

@dataclass
class EnvironmentParameters:
    """
    Текущие параметры окружающей среды в гидропонной системе

    Attributes:
        air: Параметры воздушной среды (приборы оценки состояния атмосферы)
        light: Параметры освещения (регулировка ламп на основании показаний спектрометра; изначально освещение предусматривается равномерное по всей площади)
        solution: Химические параметры питательного раствора (так как у разных производителей удобрений химические составы могут варьироваться по концентрации активного вещества и прочему,
                  необходимо по данным из документации о химических показателях этого удобрения рассчитать кол-во активного элемента на литр раствора)
    """
    air: AirParameters
    light: LightParameters
    solution: SolutionParameters

    def __post_init__(self):
        """
        Автоматическая валидация параметров после создания объекта
        """
        # Валидация выполняется в подклассах, поэтому здесь только вызов их методов
        self.air._validate()
        self.light._validate()
        self.solution._validate()

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

    def get_target_value(self) -> float:
        """
        Получить целевое (оптимальное) значение параметра
        Рассчитывается как среднее оптимального диапазона для точных рекомендаций
        Returns:
            float: Целевое значение
        """
        return (self.min_optimal + self.max_optimal) / 2

    def get_adjustment_direction(self, value: float) -> str:
        """
        Определить направление корректировки для точных рекомендаций
        Args:
            value: Текущее значение параметра
        Returns:
            str: "повысить", "снизить" или "оптимально"
        """
        if value < self.min_optimal:
            return "повысить"
        elif value > self.max_optimal:
            return "снизить"
        else:
            return "оптимально"

    def get_adjustment_delta(self, value: float) -> float:
        """
        Вычислить разницу для корректировки в исходных единицах измерения
        Args:
            value: Текущее значение параметра
        Returns:
            float: Разница (target - value), положительная для повышения, отрицательная для снижения
        """
        target = self.get_target_value()
        return target - value

@dataclass
class AirRanges:
    """
    Оптимальные диапазоны для параметров воздушной среды
    """
    temperature: OptimalRange
    humidity: OptimalRange
    atmospheric_pressure: OptimalRange

@dataclass
class LightRanges:
    """
    Оптимальные диапазоны для параметров освещения
    """
    wavelength: OptimalRange
    energy: OptimalRange
    hours: OptimalRange

@dataclass
class SolutionRanges:
    """
    Оптимальные диапазоны для химических параметров питательного раствора
    """
    nitrogen: OptimalRange
    phosphorus: OptimalRange
    potassium: OptimalRange
    calcium: OptimalRange
    magnesium: OptimalRange
    iron: OptimalRange

@dataclass
class StageRequirements:
    """
    Требования к условиям на конкретной стадии роста
    """
    air: AirRanges
    light: LightRanges
    solution: SolutionRanges
    max_yield_kg_per_m2: float  # Максимальный урожай на этой стадии (для прогнозов)

@dataclass
class CropRequirements:
    """
    Требования конкретной культуры к условиям выращивания
    Представляет "знания" экспертной системы о том, какие условия
    необходимы растению для оптимального роста и развития.
    Параметры заданы отдельно для трех стадий роста для точных рекомендаций.
    Attributes:
        crop_type: Тип культуры
        stages: Требования по стадиям роста (рассада, вегетация, плодоношение)
    """
    crop_type: CropType
    stages: Dict[GrowthStage, StageRequirements]

@dataclass
class AnalysisResult:
    """
    Результат анализа текущих условий выращивания
    Содержит все данные, полученные в результате сравнения
    текущих параметров среды с требованиями выбранной культуры на конкретной стадии.
    Включает:
    - Количественные оценки (выживаемость, урожайность, здоровье)
    - Качественные оценки (проблемы, предупреждения)
    - Практические рекомендации по улучшению условий (точные, с целевыми значениями и направлениями корректировки)
    - Целевые параметры для достижения оптимума на текущей стадии
    Attributes:
        stage: Текущая стадия роста для анализа
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
            Практические советы по исправлению ситуации с точными целевыми значениями
        optimal_parameters: Целевые (оптимальные) параметры на текущей стадии
            К каким значениям нужно стремиться
        parameter_scores: Оценки по каждому параметру (0.0-1.0)
            Детализация: какой именно параметр проблемный
            1.0 = идеально, 0.5 = допустимо, 0.0 = критично
    """
    stage: GrowthStage
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

    def get_survival_percentage(self) -> int:
        """
        Вернуть вероятность выживания в процентах (округлено)
        """
        return round(self.survival_probability * 100)

    def get_yield_percentage(self) -> int:
        """
        Вернуть прогноз урожайности относительно максимума в процентах (округлено)
        """
        return round(self.yield_forecast * 100)