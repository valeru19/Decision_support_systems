"""
База знаний экспертной системы гидропоники

Содержит реальные агрономические данные о требованиях культур
к условиям выращивания.

Источники данных:
- Научные исследования по гидропонике
- Промышленные стандарты тепличного хозяйства
- Рекомендации агрономов и практиков

Для каждой культуры определены усредненные оптимальные параметры
для всего цикла выращивания.
"""

from HydroponicExpertSystemModels import (
    CropType,
    OptimalRange,
    CropRequirements
)


class KnowledgeBase:
    """
    База знаний о требованиях сельскохозяйственных культур

    Хранит информацию об оптимальных условиях выращивания
    для каждой культуры (усредненные параметры для всего цикла).
    """

    def __init__(self):
        """Инициализация базы знаний"""
        self._requirements = self._build_knowledge_base()

    def get_requirements(self, crop_type: CropType) -> CropRequirements:
        """
        Получить требования для конкретной культуры

        Args:
            crop_type: Тип культуры

        Returns:
            CropRequirements: Требования к условиям выращивания

        Raises:
            ValueError: Если культура не найдена в базе знаний
        """
        if crop_type not in self._requirements:
            raise ValueError(
                f"Требования для культуры '{crop_type.value}' не найдены в базе знаний"
            )

        return self._requirements[crop_type]

    def get_all_crops(self) -> list[CropType]:
        """
        Получить список всех доступных культур

        Returns:
            list[CropType]: Список типов культур
        """
        return list(CropType)

    def get_crop_info(self, crop_type: CropType) -> str:
        """
        Получить краткое описание культуры

        Args:
            crop_type: Тип культуры

        Returns:
            str: Текстовое описание особенностей культуры
        """
        descriptions = {
            CropType.TOMATO: (
                "ТОМАТ - светолюбивая теплолюбивая культура. "
                "Требует много питания для хорошего урожая. "
                "Оптимальная температура 22-26C, pH 5.8-6.5, EC 2.0-3.0."
            ),
            CropType.CUCUMBER: (
                "ОГУРЕЦ - очень теплолюбивая и влаголюбивая культура. "
                "Быстрый рост, высокая продуктивность. "
                "Оптимальная температура 24-28C, pH 5.5-6.5, высокая влажность 70-80%."
            ),
            CropType.LETTUCE: (
                "САЛАТ - холодостойкая зеленная культура. "
                "Быстрый цикл 25-45 дней, нетребователен к освещению. "
                "Оптимальная температура 18-22C, pH 5.8-6.5, низкий EC 1.2-1.8."
            ),
            CropType.STRAWBERRY: (
                "КЛУБНИКА - многолетняя культура, требовательна к условиям. "
                "Любит кислую среду (pH 5.5-6.2), умеренное освещение. "
                "Оптимальная температура 20-24C."
            ),
            CropType.PEPPER: (
                "ПЕРЕЦ - теплолюбивая культура. "
                "Требует много света и тепла. "
                "Оптимальная температура 24-28C, pH 6.0-6.5, EC 2.0-2.5."
            ),
            CropType.BASIL: (
                "БАЗИЛИК - теплолюбивая ароматная зелень. "
                "Быстрый рост, любит тепло и свет. "
                "Оптимальная температура 22-26C, pH 5.5-6.5, EC 1.0-1.6."
            )
        }

        return descriptions.get(crop_type, "Описание отсутствует")

    def _build_knowledge_base(self) -> dict[CropType, CropRequirements]:
        """
        Построить базу знаний со всеми требованиями культур

        Структура словаря: {CropType: CropRequirements}
        Параметры усреднены для всего цикла выращивания

        Returns:
            dict: База знаний с требованиями для всех культур
        """
        kb = {}

        # ================================================================
        # ТОМАТ (Solanum lycopersicum)
        # Одна из самых популярных культур для гидропоники
        # Характеристики: светолюбивое, теплолюбивое растение
        # ================================================================
        kb[CropType.TOMATO] = CropRequirements(
            crop_type=CropType.TOMATO,

            max_yield_kg_per_m2=60.0,

            # Температура: усредненная для всего цикла
            temperature=OptimalRange(
                min_optimal=22.0, max_optimal=26.0,
                min_acceptable=18.0, max_acceptable=28.0,
                critical_min=12.0, critical_max=35.0
            ),

            # Влажность: средняя, не слишком высокая
            humidity=OptimalRange(
                min_optimal=60.0, max_optimal=70.0,
                min_acceptable=50.0, max_acceptable=80.0,
                critical_min=30.0, critical_max=90.0
            ),

            # pH: слегка кислая среда
            ph=OptimalRange(
                min_optimal=5.8, max_optimal=6.5,
                min_acceptable=5.5, max_acceptable=6.8,
                critical_min=4.5, critical_max=7.5
            ),

            # EC: средний-высокий для хорошего питания
            ec=OptimalRange(
                min_optimal=2.0, max_optimal=3.0,
                min_acceptable=1.5, max_acceptable=3.5,
                critical_min=0.8, critical_max=4.5
            ),

            # Освещенность: высокая (светолюбивый)
            light_intensity=OptimalRange(
                min_optimal=600.0, max_optimal=800.0,
                min_acceptable=400.0, max_acceptable=1000.0,
                critical_min=150.0, critical_max=1500.0
            ),

            # Световой день: длинный
            light_hours=OptimalRange(
                min_optimal=14.0, max_optimal=16.0,
                min_acceptable=12.0, max_acceptable=18.0,
                critical_min=10.0, critical_max=24.0
            )
        )

        # ================================================================
        # ОГУРЕЦ (Cucumis sativus)
        # Характеристики: очень влаго- и теплолюбивое растение
        # Быстрый рост, высокая продуктивность
        # ================================================================
        kb[CropType.CUCUMBER] = CropRequirements(
            crop_type=CropType.CUCUMBER,
            max_yield_kg_per_m2=80.0,
            # Температура: высокая (очень теплолюбив)
            temperature=OptimalRange(
                min_optimal=24.0, max_optimal=28.0,
                min_acceptable=22.0, max_acceptable=30.0,
                critical_min=18.0, critical_max=35.0
            ),

            # Влажность: высокая (влаголюбив)
            humidity=OptimalRange(
                min_optimal=70.0, max_optimal=80.0,
                min_acceptable=65.0, max_acceptable=85.0,
                critical_min=45.0, critical_max=92.0
            ),

            # pH: кислая среда
            ph=OptimalRange(
                min_optimal=5.5, max_optimal=6.5,
                min_acceptable=5.3, max_acceptable=6.8,
                critical_min=4.5, critical_max=7.2
            ),

            # EC: средний-высокий
            ec=OptimalRange(
                min_optimal=2.0, max_optimal=2.8,
                min_acceptable=1.5, max_acceptable=3.2,
                critical_min=0.8, critical_max=4.0
            ),

            # Освещенность: средняя-высокая
            light_intensity=OptimalRange(
                min_optimal=500.0, max_optimal=700.0,
                min_acceptable=400.0, max_acceptable=900.0,
                critical_min=150.0, critical_max=1400.0
            ),

            # Световой день: длинный
            light_hours=OptimalRange(
                min_optimal=14.0, max_optimal=16.0,
                min_acceptable=12.0, max_acceptable=18.0,
                critical_min=10.0, critical_max=24.0
            )
        )

        # ================================================================
        # САЛАТ (Lactuca sativa)
        # Характеристики: холодостойкая зеленная культура
        # Быстрый цикл выращивания, нетребователен к освещению
        # ================================================================
        kb[CropType.LETTUCE] = CropRequirements(
            crop_type=CropType.LETTUCE,
            max_yield_kg_per_m2=25.0,
            # Температура: прохладная (холодостойкий)
            temperature=OptimalRange(
                min_optimal=18.0, max_optimal=22.0,
                min_acceptable=16.0, max_acceptable=24.0,
                critical_min=10.0, critical_max=28.0
            ),

            # Влажность: средняя
            humidity=OptimalRange(
                min_optimal=50.0, max_optimal=70.0,
                min_acceptable=45.0, max_acceptable=75.0,
                critical_min=30.0, critical_max=85.0
            ),

            # pH: слегка кислая-нейтральная
            ph=OptimalRange(
                min_optimal=5.8, max_optimal=6.5,
                min_acceptable=5.5, max_acceptable=7.0,
                critical_min=5.0, critical_max=7.5
            ),

            # EC: низкий (мало питания)
            ec=OptimalRange(
                min_optimal=1.2, max_optimal=1.8,
                min_acceptable=1.0, max_acceptable=2.2,
                critical_min=0.5, critical_max=3.0
            ),

            # Освещенность: низкая-средняя
            light_intensity=OptimalRange(
                min_optimal=250.0, max_optimal=400.0,
                min_acceptable=200.0, max_acceptable=500.0,
                critical_min=100.0, critical_max=700.0
            ),

            # Световой день: средний
            light_hours=OptimalRange(
                min_optimal=12.0, max_optimal=16.0,
                min_acceptable=10.0, max_acceptable=18.0,
                critical_min=8.0, critical_max=20.0
            )
        )

        # ================================================================
        # КЛУБНИКА (Fragaria × ananassa)
        # Характеристики: многолетнее растение, требовательна к условиям
        # ================================================================
        kb[CropType.STRAWBERRY] = CropRequirements(
            crop_type=CropType.STRAWBERRY,
            max_yield_kg_per_m2=15.0,
            # Температура: умеренная
            temperature=OptimalRange(
                min_optimal=20.0, max_optimal=24.0,
                min_acceptable=18.0, max_acceptable=26.0,
                critical_min=12.0, critical_max=30.0
            ),

            # Влажность: средняя
            humidity=OptimalRange(
                min_optimal=60.0, max_optimal=70.0,
                min_acceptable=55.0, max_acceptable=75.0,
                critical_min=40.0, critical_max=85.0
            ),

            # pH: кислая среда (любит кислую почву)
            ph=OptimalRange(
                min_optimal=5.5, max_optimal=6.2,
                min_acceptable=5.3, max_acceptable=6.5,
                critical_min=4.8, critical_max=7.2
            ),

            # EC: средний
            ec=OptimalRange(
                min_optimal=1.5, max_optimal=2.0,
                min_acceptable=1.2, max_acceptable=2.5,
                critical_min=0.6, critical_max=3.0
            ),

            # Освещенность: средняя-высокая
            light_intensity=OptimalRange(
                min_optimal=400.0, max_optimal=600.0,
                min_acceptable=300.0, max_acceptable=750.0,
                critical_min=150.0, critical_max=1000.0
            ),

            # Световой день: средний (короткий день стимулирует цветение)
            light_hours=OptimalRange(
                min_optimal=12.0, max_optimal=14.0,
                min_acceptable=10.0, max_acceptable=16.0,
                critical_min=8.0, critical_max=18.0
            )
        )

        # ================================================================
        # ПЕРЕЦ (Capsicum annuum)
        # Характеристики: теплолюбивая культура, требует много света
        # ================================================================
        kb[CropType.PEPPER] = CropRequirements(
            crop_type=CropType.PEPPER,
            max_yield_kg_per_m2=35.0,
            # Температура: высокая (теплолюбив)
            temperature=OptimalRange(
                min_optimal=24.0, max_optimal=28.0,
                min_acceptable=20.0, max_acceptable=30.0,
                critical_min=15.0, critical_max=35.0
            ),

            # Влажность: средняя
            humidity=OptimalRange(
                min_optimal=60.0, max_optimal=70.0,
                min_acceptable=50.0, max_acceptable=80.0,
                critical_min=35.0, critical_max=90.0
            ),

            # pH: слегка кислая-нейтральная
            ph=OptimalRange(
                min_optimal=6.0, max_optimal=6.5,
                min_acceptable=5.8, max_acceptable=6.8,
                critical_min=5.0, critical_max=7.5
            ),

            # EC: средний-высокий
            ec=OptimalRange(
                min_optimal=2.0, max_optimal=2.5,
                min_acceptable=1.8, max_acceptable=3.0,
                critical_min=1.0, critical_max=4.0
            ),

            # Освещенность: высокая (светолюбив)
            light_intensity=OptimalRange(
                min_optimal=600.0, max_optimal=900.0,
                min_acceptable=500.0, max_acceptable=1100.0,
                critical_min=200.0, critical_max=1500.0
            ),

            # Световой день: длинный
            light_hours=OptimalRange(
                min_optimal=14.0, max_optimal=16.0,
                min_acceptable=12.0, max_acceptable=18.0,
                critical_min=10.0, critical_max=24.0
            )
        )

        # ================================================================
        # БАЗИЛИК (Ocimum basilicum)
        # Характеристики: теплолюбивая ароматная зелень
        # ================================================================
        kb[CropType.BASIL] = CropRequirements(
            crop_type=CropType.BASIL,
            max_yield_kg_per_m2=8.0,
            # Температура: умеренно-высокая
            temperature=OptimalRange(
                min_optimal=22.0, max_optimal=26.0,
                min_acceptable=20.0, max_acceptable=28.0,
                critical_min=15.0, critical_max=32.0
            ),

            # Влажность: средняя
            humidity=OptimalRange(
                min_optimal=60.0, max_optimal=70.0,
                min_acceptable=50.0, max_acceptable=75.0,
                critical_min=35.0, critical_max=85.0
            ),

            # pH: слегка кислая-нейтральная
            ph=OptimalRange(
                min_optimal=5.5, max_optimal=6.5,
                min_acceptable=5.3, max_acceptable=6.8,
                critical_min=5.0, critical_max=7.2
            ),

            # EC: низкий-средний
            ec=OptimalRange(
                min_optimal=1.0, max_optimal=1.6,
                min_acceptable=0.8, max_acceptable=2.0,
                critical_min=0.4, critical_max=2.5
            ),

            # Освещенность: средняя-высокая
            light_intensity=OptimalRange(
                min_optimal=400.0, max_optimal=600.0,
                min_acceptable=300.0, max_acceptable=800.0,
                critical_min=150.0, critical_max=1200.0
            ),

            # Световой день: длинный
            light_hours=OptimalRange(
                min_optimal=14.0, max_optimal=16.0,
                min_acceptable=12.0, max_acceptable=18.0,
                critical_min=10.0, critical_max=24.0
            )
        )

        return kb