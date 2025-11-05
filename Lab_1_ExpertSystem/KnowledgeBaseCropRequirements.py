"""
База знаний экспертной системы гидропоники
Содержит реальные агрономические данные о требованиях культур
к условиям выращивания.
Источники данных:
- Научные исследования по гидропонике
- Промышленные стандарты тепличного хозяйства
- Рекомендации агрономов и практиков
Для каждой культуры определены оптимальные параметры
для трех стадий роста: рассада (seedling), вегетация (vegetative), плодоношение (fruiting).
"""

from HydroponicExpertSystemModels import (
    CropType,
    GrowthStage,
    OptimalRange,
    AirRanges,
    LightRanges,
    SolutionRanges,
    StageRequirements,
    CropRequirements
)

class KnowledgeBase:
    """
    База знаний о требованиях сельскохозяйственных культур
    Хранит информацию об оптимальных условиях выращивания
    для каждой культуры по стадиям роста.
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
                "Оптимальная температура 22-26°C, влажность 60-70%."
            ),
            CropType.CUCUMBER: (
                "ОГУРЕЦ - очень теплолюбивая и влаголюбивая культура. "
                "Быстрый рост, высокая продуктивность. "
                "Оптимальная температура 24-28°C, влажность 70-80%."
            ),
            CropType.LETTUCE: (
                "САЛАТ - холодостойкая зеленная культура. "
                "Быстрый цикл 25-45 дней, нетребователен к освещению. "
                "Оптимальная температура 18-22°C, влажность 50-70%."
            ),
            CropType.STRAWBERRY: (
                "КЛУБНИКА - многолетняя культура, требовательна к условиям. "
                "Любит умеренное освещение. "
                "Оптимальная температура 20-24°C, влажность 60-70%."
            ),
            CropType.PEPPER: (
                "ПЕРЕЦ - теплолюбивая культура. "
                "Требует много света и тепла. "
                "Оптимальная температура 24-28°C, влажность 60-70%."
            ),
            CropType.BASIL: (
                "БАЗИЛИК - теплолюбивая ароматная зелень. "
                "Быстрый рост, любит тепло и свет. "
                "Оптимальная температура 22-26°C, влажность 60-70%."
            )
        }
        return descriptions.get(crop_type, "Описание отсутствует")

    def _build_knowledge_base(self) -> dict[CropType, CropRequirements]:
        """
        Построить базу знаний со всеми требованиями культур
        Структура: {CropType: CropRequirements с stages по стадиям роста}
        Parameters в единицах: temperature °C, humidity %, pressure мм рт. ст.,
        wavelength нм, energy Вт/м², hours ч, nutrients мг/л.
        Returns:
            dict: База знаний с требованиями для всех культур
        """
        kb = {}

        # ================================================================
        # ТОМАТ (Solanum lycopersicum)
        # ================================================================
        kb[CropType.TOMATO] = CropRequirements(
            crop_type=CropType.TOMATO,
            stages={
                GrowthStage.SEEDLING: StageRequirements(
                    air=AirRanges(
                        temperature=OptimalRange(min_optimal=22.0, max_optimal=26.0, min_acceptable=18.0, max_acceptable=28.0, critical_min=12.0, critical_max=35.0),
                        humidity=OptimalRange(min_optimal=60.0, max_optimal=70.0, min_acceptable=50.0, max_acceptable=80.0, critical_min=30.0, critical_max=90.0),
                        atmospheric_pressure=OptimalRange(min_optimal=750.0, max_optimal=770.0, min_acceptable=700.0, max_acceptable=800.0, critical_min=600.0, critical_max=900.0)
                    ),
                    light=LightRanges(
                        wavelength=OptimalRange(min_optimal=450.0, max_optimal=500.0, min_acceptable=400.0, max_acceptable=550.0, critical_min=350.0, critical_max=600.0),
                        energy=OptimalRange(min_optimal=100.0, max_optimal=200.0, min_acceptable=50.0, max_acceptable=250.0, critical_min=20.0, critical_max=400.0),
                        hours=OptimalRange(min_optimal=12.0, max_optimal=14.0, min_acceptable=10.0, max_acceptable=16.0, critical_min=8.0, critical_max=18.0)
                    ),
                    solution=SolutionRanges(
                        nitrogen=OptimalRange(min_optimal=90.0, max_optimal=120.0, min_acceptable=70.0, max_acceptable=150.0, critical_min=50.0, critical_max=200.0),
                        phosphorus=OptimalRange(min_optimal=40.0, max_optimal=50.0, min_acceptable=30.0, max_acceptable=60.0, critical_min=20.0, critical_max=80.0),
                        potassium=OptimalRange(min_optimal=140.0, max_optimal=150.0, min_acceptable=120.0, max_acceptable=170.0, critical_min=100.0, critical_max=200.0),
                        calcium=OptimalRange(min_optimal=140.0, max_optimal=150.0, min_acceptable=120.0, max_acceptable=170.0, critical_min=100.0, critical_max=200.0),
                        magnesium=OptimalRange(min_optimal=50.0, max_optimal=70.0, min_acceptable=40.0, max_acceptable=80.0, critical_min=30.0, critical_max=100.0),
                        iron=OptimalRange(min_optimal=2.0, max_optimal=3.0, min_acceptable=1.5, max_acceptable=3.5, critical_min=1.0, critical_max=5.0)
                    ),
                    max_yield_kg_per_m2=0.0  # Нет урожая на стадии рассады
                ),
                GrowthStage.VEGETATIVE: StageRequirements(
                    air=AirRanges(
                        temperature=OptimalRange(min_optimal=20.0, max_optimal=25.0, min_acceptable=18.0, max_acceptable=27.0, critical_min=15.0, critical_max=30.0),
                        humidity=OptimalRange(min_optimal=60.0, max_optimal=70.0, min_acceptable=50.0, max_acceptable=80.0, critical_min=30.0, critical_max=90.0),
                        atmospheric_pressure=OptimalRange(min_optimal=750.0, max_optimal=770.0, min_acceptable=700.0, max_acceptable=800.0, critical_min=600.0, critical_max=900.0)
                    ),
                    light=LightRanges(
                        wavelength=OptimalRange(min_optimal=500.0, max_optimal=600.0, min_acceptable=450.0, max_acceptable=650.0, critical_min=400.0, critical_max=700.0),
                        energy=OptimalRange(min_optimal=200.0, max_optimal=300.0, min_acceptable=150.0, max_acceptable=350.0, critical_min=100.0, critical_max=500.0),
                        hours=OptimalRange(min_optimal=14.0, max_optimal=16.0, min_acceptable=12.0, max_acceptable=18.0, critical_min=10.0, critical_max=20.0)
                    ),
                    solution=SolutionRanges(
                        nitrogen=OptimalRange(min_optimal=120.0, max_optimal=150.0, min_acceptable=100.0, max_acceptable=170.0, critical_min=80.0, critical_max=200.0),
                        phosphorus=OptimalRange(min_optimal=40.0, max_optimal=50.0, min_acceptable=30.0, max_acceptable=60.0, critical_min=20.0, critical_max=80.0),
                        potassium=OptimalRange(min_optimal=300.0, max_optimal=400.0, min_acceptable=250.0, max_acceptable=450.0, critical_min=200.0, critical_max=500.0),
                        calcium=OptimalRange(min_optimal=150.0, max_optimal=170.0, min_acceptable=130.0, max_acceptable=190.0, critical_min=100.0, critical_max=220.0),
                        magnesium=OptimalRange(min_optimal=50.0, max_optimal=70.0, min_acceptable=40.0, max_acceptable=80.0, critical_min=30.0, critical_max=100.0),
                        iron=OptimalRange(min_optimal=2.0, max_optimal=3.0, min_acceptable=1.5, max_acceptable=3.5, critical_min=1.0, critical_max=5.0)
                    ),
                    max_yield_kg_per_m2=0.0  # Урожай на стадии плодоношения
                ),
                GrowthStage.FRUITING: StageRequirements(
                    air=AirRanges(
                        temperature=OptimalRange(min_optimal=18.0, max_optimal=24.0, min_acceptable=16.0, max_acceptable=26.0, critical_min=12.0, critical_max=30.0),
                        humidity=OptimalRange(min_optimal=60.0, max_optimal=70.0, min_acceptable=50.0, max_acceptable=80.0, critical_min=30.0, critical_max=90.0),
                        atmospheric_pressure=OptimalRange(min_optimal=750.0, max_optimal=770.0, min_acceptable=700.0, max_acceptable=800.0, critical_min=600.0, critical_max=900.0)
                    ),
                    light=LightRanges(
                        wavelength=OptimalRange(min_optimal=600.0, max_optimal=700.0, min_acceptable=550.0, max_acceptable=750.0, critical_min=500.0, critical_max=800.0),
                        energy=OptimalRange(min_optimal=300.0, max_optimal=400.0, min_acceptable=250.0, max_acceptable=450.0, critical_min=200.0, critical_max=600.0),
                        hours=OptimalRange(min_optimal=14.0, max_optimal=16.0, min_acceptable=12.0, max_acceptable=18.0, critical_min=10.0, critical_max=20.0)
                    ),
                    solution=SolutionRanges(
                        nitrogen=OptimalRange(min_optimal=180.0, max_optimal=200.0, min_acceptable=150.0, max_acceptable=220.0, critical_min=120.0, critical_max=250.0),
                        phosphorus=OptimalRange(min_optimal=40.0, max_optimal=50.0, min_acceptable=30.0, max_acceptable=60.0, critical_min=20.0, critical_max=80.0),
                        potassium=OptimalRange(min_optimal=300.0, max_optimal=400.0, min_acceptable=250.0, max_acceptable=450.0, critical_min=200.0, critical_max=500.0),
                        calcium=OptimalRange(min_optimal=180.0, max_optimal=220.0, min_acceptable=160.0, max_acceptable=240.0, critical_min=140.0, critical_max=280.0),
                        magnesium=OptimalRange(min_optimal=50.0, max_optimal=70.0, min_acceptable=40.0, max_acceptable=80.0, critical_min=30.0, critical_max=100.0),
                        iron=OptimalRange(min_optimal=2.0, max_optimal=3.0, min_acceptable=1.5, max_acceptable=3.5, critical_min=1.0, critical_max=5.0)
                    ),
                    max_yield_kg_per_m2=60.0
                )
            }
        )

        # ================================================================
        # ОГУРЕЦ (Cucumis sativus)
        # ================================================================
        kb[CropType.CUCUMBER] = CropRequirements(
            crop_type=CropType.CUCUMBER,
            stages={
                GrowthStage.SEEDLING: StageRequirements(
                    air=AirRanges(
                        temperature=OptimalRange(min_optimal=24.0, max_optimal=28.0, min_acceptable=22.0, max_acceptable=30.0, critical_min=18.0, critical_max=35.0),
                        humidity=OptimalRange(min_optimal=70.0, max_optimal=80.0, min_acceptable=65.0, max_acceptable=85.0, critical_min=45.0, critical_max=92.0),
                        atmospheric_pressure=OptimalRange(min_optimal=750.0, max_optimal=770.0, min_acceptable=700.0, max_acceptable=800.0, critical_min=600.0, critical_max=900.0)
                    ),
                    light=LightRanges(
                        wavelength=OptimalRange(min_optimal=450.0, max_optimal=500.0, min_acceptable=400.0, max_acceptable=550.0, critical_min=350.0, critical_max=600.0),
                        energy=OptimalRange(min_optimal=100.0, max_optimal=200.0, min_acceptable=50.0, max_acceptable=250.0, critical_min=20.0, critical_max=400.0),
                        hours=OptimalRange(min_optimal=12.0, max_optimal=14.0, min_acceptable=10.0, max_acceptable=16.0, critical_min=8.0, critical_max=18.0)
                    ),
                    solution=SolutionRanges(
                        nitrogen=OptimalRange(min_optimal=100.0, max_optimal=120.0, min_acceptable=80.0, max_acceptable=140.0, critical_min=50.0, critical_max=200.0),
                        phosphorus=OptimalRange(min_optimal=30.0, max_optimal=40.0, min_acceptable=20.0, max_acceptable=50.0, critical_min=10.0, critical_max=70.0),
                        potassium=OptimalRange(min_optimal=150.0, max_optimal=170.0, min_acceptable=130.0, max_acceptable=190.0, critical_min=100.0, critical_max=220.0),
                        calcium=OptimalRange(min_optimal=100.0, max_optimal=120.0, min_acceptable=80.0, max_acceptable=140.0, critical_min=50.0, critical_max=170.0),
                        magnesium=OptimalRange(min_optimal=40.0, max_optimal=50.0, min_acceptable=30.0, max_acceptable=60.0, critical_min=20.0, critical_max=80.0),
                        iron=OptimalRange(min_optimal=2.0, max_optimal=3.0, min_acceptable=1.5, max_acceptable=3.5, critical_min=1.0, critical_max=5.0)
                    ),
                    max_yield_kg_per_m2=0.0
                ),
                GrowthStage.VEGETATIVE: StageRequirements(
                    air=AirRanges(
                        temperature=OptimalRange(min_optimal=24.0, max_optimal=28.0, min_acceptable=22.0, max_acceptable=30.0, critical_min=18.0, critical_max=35.0),
                        humidity=OptimalRange(min_optimal=70.0, max_optimal=80.0, min_acceptable=65.0, max_acceptable=85.0, critical_min=45.0, critical_max=92.0),
                        atmospheric_pressure=OptimalRange(min_optimal=750.0, max_optimal=770.0, min_acceptable=700.0, max_acceptable=800.0, critical_min=600.0, critical_max=900.0)
                    ),
                    light=LightRanges(
                        wavelength=OptimalRange(min_optimal=500.0, max_optimal=600.0, min_acceptable=450.0, max_acceptable=650.0, critical_min=400.0, critical_max=700.0),
                        energy=OptimalRange(min_optimal=200.0, max_optimal=300.0, min_acceptable=150.0, max_acceptable=350.0, critical_min=100.0, critical_max=500.0),
                        hours=OptimalRange(min_optimal=14.0, max_optimal=16.0, min_acceptable=12.0, max_acceptable=18.0, critical_min=10.0, critical_max=20.0)
                    ),
                    solution=SolutionRanges(
                        nitrogen=OptimalRange(min_optimal=120.0, max_optimal=140.0, min_acceptable=100.0, max_acceptable=160.0, critical_min=80.0, critical_max=200.0),
                        phosphorus=OptimalRange(min_optimal=40.0, max_optimal=50.0, min_acceptable=30.0, max_acceptable=60.0, critical_min=20.0, critical_max=80.0),
                        potassium=OptimalRange(min_optimal=170.0, max_optimal=190.0, min_acceptable=150.0, max_acceptable=210.0, critical_min=120.0, critical_max=240.0),
                        calcium=OptimalRange(min_optimal=120.0, max_optimal=140.0, min_acceptable=100.0, max_acceptable=160.0, critical_min=80.0, critical_max=180.0),
                        magnesium=OptimalRange(min_optimal=50.0, max_optimal=60.0, min_acceptable=40.0, max_acceptable=70.0, critical_min=30.0, critical_max=90.0),
                        iron=OptimalRange(min_optimal=2.0, max_optimal=3.0, min_acceptable=1.5, max_acceptable=3.5, critical_min=1.0, critical_max=5.0)
                    ),
                    max_yield_kg_per_m2=0.0
                ),
                GrowthStage.FRUITING: StageRequirements(
                    air=AirRanges(
                        temperature=OptimalRange(min_optimal=24.0, max_optimal=28.0, min_acceptable=22.0, max_acceptable=30.0, critical_min=18.0, critical_max=35.0),
                        humidity=OptimalRange(min_optimal=70.0, max_optimal=80.0, min_acceptable=65.0, max_acceptable=85.0, critical_min=45.0, critical_max=92.0),
                        atmospheric_pressure=OptimalRange(min_optimal=750.0, max_optimal=770.0, min_acceptable=700.0, max_acceptable=800.0, critical_min=600.0, critical_max=900.0)
                    ),
                    light=LightRanges(
                        wavelength=OptimalRange(min_optimal=600.0, max_optimal=700.0, min_acceptable=550.0, max_acceptable=750.0, critical_min=500.0, critical_max=800.0),
                        energy=OptimalRange(min_optimal=300.0, max_optimal=400.0, min_acceptable=250.0, max_acceptable=450.0, critical_min=200.0, critical_max=600.0),
                        hours=OptimalRange(min_optimal=14.0, max_optimal=16.0, min_acceptable=12.0, max_acceptable=18.0, critical_min=10.0, critical_max=20.0)
                    ),
                    solution=SolutionRanges(
                        nitrogen=OptimalRange(min_optimal=140.0, max_optimal=160.0, min_acceptable=120.0, max_acceptable=180.0, critical_min=100.0, critical_max=220.0),
                        phosphorus=OptimalRange(min_optimal=40.0, max_optimal=50.0, min_acceptable=30.0, max_acceptable=60.0, critical_min=20.0, critical_max=80.0),
                        potassium=OptimalRange(min_optimal=190.0, max_optimal=210.0, min_acceptable=170.0, max_acceptable=230.0, critical_min=150.0, critical_max=260.0),
                        calcium=OptimalRange(min_optimal=140.0, max_optimal=160.0, min_acceptable=120.0, max_acceptable=180.0, critical_min=100.0, critical_max=200.0),
                        magnesium=OptimalRange(min_optimal=50.0, max_optimal=60.0, min_acceptable=40.0, max_acceptable=70.0, critical_min=30.0, critical_max=90.0),
                        iron=OptimalRange(min_optimal=2.0, max_optimal=3.0, min_acceptable=1.5, max_acceptable=3.5, critical_min=1.0, critical_max=5.0)
                    ),
                    max_yield_kg_per_m2=80.0
                )
            }
        )

        # ================================================================
        # САЛАТ (Lactuca sativa)
        # ================================================================
        kb[CropType.LETTUCE] = CropRequirements(
            crop_type=CropType.LETTUCE,
            stages={
                GrowthStage.SEEDLING: StageRequirements(
                    air=AirRanges(
                        temperature=OptimalRange(min_optimal=18.0, max_optimal=22.0, min_acceptable=16.0, max_acceptable=24.0, critical_min=10.0, critical_max=28.0),
                        humidity=OptimalRange(min_optimal=50.0, max_optimal=70.0, min_acceptable=45.0, max_acceptable=75.0, critical_min=30.0, critical_max=85.0),
                        atmospheric_pressure=OptimalRange(min_optimal=750.0, max_optimal=770.0, min_acceptable=700.0, max_acceptable=800.0, critical_min=600.0, critical_max=900.0)
                    ),
                    light=LightRanges(
                        wavelength=OptimalRange(min_optimal=450.0, max_optimal=500.0, min_acceptable=400.0, max_acceptable=550.0, critical_min=350.0, critical_max=600.0),
                        energy=OptimalRange(min_optimal=100.0, max_optimal=150.0, min_acceptable=50.0, max_acceptable=200.0, critical_min=20.0, critical_max=300.0),
                        hours=OptimalRange(min_optimal=10.0, max_optimal=12.0, min_acceptable=8.0, max_acceptable=14.0, critical_min=6.0, critical_max=16.0)
                    ),
                    solution=SolutionRanges(
                        nitrogen=OptimalRange(min_optimal=100.0, max_optimal=150.0, min_acceptable=80.0, max_acceptable=170.0, critical_min=50.0, critical_max=200.0),
                        phosphorus=OptimalRange(min_optimal=30.0, max_optimal=50.0, min_acceptable=20.0, max_acceptable=60.0, critical_min=10.0, critical_max=80.0),
                        potassium=OptimalRange(min_optimal=100.0, max_optimal=150.0, min_acceptable=80.0, max_acceptable=170.0, critical_min=50.0, critical_max=200.0),
                        calcium=OptimalRange(min_optimal=100.0, max_optimal=150.0, min_acceptable=80.0, max_acceptable=170.0, critical_min=50.0, critical_max=200.0),
                        magnesium=OptimalRange(min_optimal=40.0, max_optimal=60.0, min_acceptable=30.0, max_acceptable=70.0, critical_min=20.0, critical_max=80.0),
                        iron=OptimalRange(min_optimal=2.0, max_optimal=3.0, min_acceptable=1.5, max_acceptable=3.5, critical_min=1.0, critical_max=5.0)
                    ),
                    max_yield_kg_per_m2=0.0
                ),
                GrowthStage.VEGETATIVE: StageRequirements(
                    air=AirRanges(
                        temperature=OptimalRange(min_optimal=18.0, max_optimal=22.0, min_acceptable=16.0, max_acceptable=24.0, critical_min=10.0, critical_max=28.0),
                        humidity=OptimalRange(min_optimal=50.0, max_optimal=70.0, min_acceptable=45.0, max_acceptable=75.0, critical_min=30.0, critical_max=85.0),
                        atmospheric_pressure=OptimalRange(min_optimal=750.0, max_optimal=770.0, min_acceptable=700.0, max_acceptable=800.0, critical_min=600.0, critical_max=900.0)
                    ),
                    light=LightRanges(
                        wavelength=OptimalRange(min_optimal=500.0, max_optimal=600.0, min_acceptable=450.0, max_acceptable=650.0, critical_min=400.0, critical_max=700.0),
                        energy=OptimalRange(min_optimal=150.0, max_optimal=200.0, min_acceptable=100.0, max_acceptable=250.0, critical_min=50.0, critical_max=350.0),
                        hours=OptimalRange(min_optimal=12.0, max_optimal=16.0, min_acceptable=10.0, max_acceptable=18.0, critical_min=8.0, critical_max=20.0)
                    ),
                    solution=SolutionRanges(
                        nitrogen=OptimalRange(min_optimal=150.0, max_optimal=200.0, min_acceptable=130.0, max_acceptable=220.0, critical_min=100.0, critical_max=250.0),
                        phosphorus=OptimalRange(min_optimal=40.0, max_optimal=60.0, min_acceptable=30.0, max_acceptable=70.0, critical_min=20.0, critical_max=90.0),
                        potassium=OptimalRange(min_optimal=150.0, max_optimal=200.0, min_acceptable=130.0, max_acceptable=220.0, critical_min=100.0, critical_max=250.0),
                        calcium=OptimalRange(min_optimal=120.0, max_optimal=160.0, min_acceptable=100.0, max_acceptable=180.0, critical_min=80.0, critical_max=200.0),
                        magnesium=OptimalRange(min_optimal=50.0, max_optimal=70.0, min_acceptable=40.0, max_acceptable=80.0, critical_min=30.0, critical_max=100.0),
                        iron=OptimalRange(min_optimal=2.0, max_optimal=3.0, min_acceptable=1.5, max_acceptable=3.5, critical_min=1.0, critical_max=5.0)
                    ),
                    max_yield_kg_per_m2=25.0  # Урожай на стадии зрелости (для зелени)
                ),
                GrowthStage.FRUITING: StageRequirements(
                    air=AirRanges(
                        temperature=OptimalRange(min_optimal=18.0, max_optimal=22.0, min_acceptable=16.0, max_acceptable=24.0, critical_min=10.0, critical_max=28.0),
                        humidity=OptimalRange(min_optimal=50.0, max_optimal=70.0, min_acceptable=45.0, max_acceptable=75.0, critical_min=30.0, critical_max=85.0),
                        atmospheric_pressure=OptimalRange(min_optimal=750.0, max_optimal=770.0, min_acceptable=700.0, max_acceptable=800.0, critical_min=600.0, critical_max=900.0)
                    ),
                    light=LightRanges(
                        wavelength=OptimalRange(min_optimal=600.0, max_optimal=700.0, min_acceptable=550.0, max_acceptable=750.0, critical_min=500.0, critical_max=800.0),
                        energy=OptimalRange(min_optimal=150.0, max_optimal=200.0, min_acceptable=100.0, max_acceptable=250.0, critical_min=50.0, critical_max=350.0),
                        hours=OptimalRange(min_optimal=12.0, max_optimal=16.0, min_acceptable=10.0, max_acceptable=18.0, critical_min=8.0, critical_max=20.0)
                    ),
                    solution=SolutionRanges(
                        nitrogen=OptimalRange(min_optimal=150.0, max_optimal=200.0, min_acceptable=130.0, max_acceptable=220.0, critical_min=100.0, critical_max=250.0),
                        phosphorus=OptimalRange(min_optimal=40.0, max_optimal=60.0, min_acceptable=30.0, max_acceptable=70.0, critical_min=20.0, critical_max=90.0),
                        potassium=OptimalRange(min_optimal=150.0, max_optimal=200.0, min_acceptable=130.0, max_acceptable=220.0, critical_min=100.0, critical_max=250.0),
                        calcium=OptimalRange(min_optimal=120.0, max_optimal=160.0, min_acceptable=100.0, max_acceptable=180.0, critical_min=80.0, critical_max=200.0),
                        magnesium=OptimalRange(min_optimal=50.0, max_optimal=70.0, min_acceptable=40.0, max_acceptable=80.0, critical_min=30.0, critical_max=100.0),
                        iron=OptimalRange(min_optimal=2.0, max_optimal=3.0, min_acceptable=1.5, max_acceptable=3.5, critical_min=1.0, critical_max=5.0)
                    ),
                    max_yield_kg_per_m2=0.0  # Для салата основная стадия - вегетация
                )
            }
        )

        # ================================================================
        # КЛУБНИКА (Fragaria × ananassa)
        # ================================================================
        kb[CropType.STRAWBERRY] = CropRequirements(
            crop_type=CropType.STRAWBERRY,
            stages={
                GrowthStage.SEEDLING: StageRequirements(
                    air=AirRanges(
                        temperature=OptimalRange(min_optimal=20.0, max_optimal=24.0, min_acceptable=18.0, max_acceptable=26.0, critical_min=12.0, critical_max=30.0),
                        humidity=OptimalRange(min_optimal=60.0, max_optimal=70.0, min_acceptable=55.0, max_acceptable=75.0, critical_min=40.0, critical_max=85.0),
                        atmospheric_pressure=OptimalRange(min_optimal=750.0, max_optimal=770.0, min_acceptable=700.0, max_acceptable=800.0, critical_min=600.0, critical_max=900.0)
                    ),
                    light=LightRanges(
                        wavelength=OptimalRange(min_optimal=450.0, max_optimal=500.0, min_acceptable=400.0, max_acceptable=550.0, critical_min=350.0, critical_max=600.0),
                        energy=OptimalRange(min_optimal=100.0, max_optimal=200.0, min_acceptable=50.0, max_acceptable=250.0, critical_min=20.0, critical_max=400.0),
                        hours=OptimalRange(min_optimal=10.0, max_optimal=12.0, min_acceptable=8.0, max_acceptable=14.0, critical_min=6.0, critical_max=16.0)
                    ),
                    solution=SolutionRanges(
                        nitrogen=OptimalRange(min_optimal=70.0, max_optimal=90.0, min_acceptable=60.0, max_acceptable=100.0, critical_min=40.0, critical_max=120.0),
                        phosphorus=OptimalRange(min_optimal=40.0, max_optimal=50.0, min_acceptable=30.0, max_acceptable=60.0, critical_min=20.0, critical_max=80.0),
                        potassium=OptimalRange(min_optimal=90.0, max_optimal=110.0, min_acceptable=80.0, max_acceptable=120.0, critical_min=60.0, critical_max=140.0),
                        calcium=OptimalRange(min_optimal=180.0, max_optimal=220.0, min_acceptable=160.0, max_acceptable=240.0, critical_min=140.0, critical_max=260.0),
                        magnesium=OptimalRange(min_optimal=40.0, max_optimal=60.0, min_acceptable=30.0, max_acceptable=70.0, critical_min=20.0, critical_max=80.0),
                        iron=OptimalRange(min_optimal=2.5, max_optimal=3.5, min_acceptable=2.0, max_acceptable=4.0, critical_min=1.5, critical_max=5.0)
                    ),
                    max_yield_kg_per_m2=0.0
                ),
                GrowthStage.VEGETATIVE: StageRequirements(
                    air=AirRanges(
                        temperature=OptimalRange(min_optimal=20.0, max_optimal=24.0, min_acceptable=18.0, max_acceptable=26.0, critical_min=12.0, critical_max=30.0),
                        humidity=OptimalRange(min_optimal=60.0, max_optimal=70.0, min_acceptable=55.0, max_acceptable=75.0, critical_min=40.0, critical_max=85.0),
                        atmospheric_pressure=OptimalRange(min_optimal=750.0, max_optimal=770.0, min_acceptable=700.0, max_acceptable=800.0, critical_min=600.0, critical_max=900.0)
                    ),
                    light=LightRanges(
                        wavelength=OptimalRange(min_optimal=500.0, max_optimal=600.0, min_acceptable=450.0, max_acceptable=650.0, critical_min=400.0, critical_max=700.0),
                        energy=OptimalRange(min_optimal=200.0, max_optimal=300.0, min_acceptable=150.0, max_acceptable=350.0, critical_min=100.0, critical_max=500.0),
                        hours=OptimalRange(min_optimal=12.0, max_optimal=14.0, min_acceptable=10.0, max_acceptable=16.0, critical_min=8.0, critical_max=18.0)
                    ),
                    solution=SolutionRanges(
                        nitrogen=OptimalRange(min_optimal=70.0, max_optimal=90.0, min_acceptable=60.0, max_acceptable=100.0, critical_min=40.0, critical_max=120.0),
                        phosphorus=OptimalRange(min_optimal=40.0, max_optimal=50.0, min_acceptable=30.0, max_acceptable=60.0, critical_min=20.0, critical_max=80.0),
                        potassium=OptimalRange(min_optimal=90.0, max_optimal=110.0, min_acceptable=80.0, max_acceptable=120.0, critical_min=60.0, critical_max=140.0),
                        calcium=OptimalRange(min_optimal=180.0, max_optimal=220.0, min_acceptable=160.0, max_acceptable=240.0, critical_min=140.0, critical_max=260.0),
                        magnesium=OptimalRange(min_optimal=40.0, max_optimal=60.0, min_acceptable=30.0, max_acceptable=70.0, critical_min=20.0, critical_max=80.0),
                        iron=OptimalRange(min_optimal=2.5, max_optimal=3.5, min_acceptable=2.0, max_acceptable=4.0, critical_min=1.5, critical_max=5.0)
                    ),
                    max_yield_kg_per_m2=0.0
                ),
                GrowthStage.FRUITING: StageRequirements(
                    air=AirRanges(
                        temperature=OptimalRange(min_optimal=20.0, max_optimal=24.0, min_acceptable=18.0, max_acceptable=26.0, critical_min=12.0, critical_max=30.0),
                        humidity=OptimalRange(min_optimal=60.0, max_optimal=70.0, min_acceptable=55.0, max_acceptable=75.0, critical_min=40.0, critical_max=85.0),
                        atmospheric_pressure=OptimalRange(min_optimal=750.0, max_optimal=770.0, min_acceptable=700.0, max_acceptable=800.0, critical_min=600.0, critical_max=900.0)
                    ),
                    light=LightRanges(
                        wavelength=OptimalRange(min_optimal=600.0, max_optimal=700.0, min_acceptable=550.0, max_acceptable=750.0, critical_min=500.0, critical_max=800.0),
                        energy=OptimalRange(min_optimal=250.0, max_optimal=350.0, min_acceptable=200.0, max_acceptable=400.0, critical_min=150.0, critical_max=500.0),
                        hours=OptimalRange(min_optimal=12.0, max_optimal=14.0, min_acceptable=10.0, max_acceptable=16.0, critical_min=8.0, critical_max=18.0)
                    ),
                    solution=SolutionRanges(
                        nitrogen=OptimalRange(min_optimal=70.0, max_optimal=90.0, min_acceptable=60.0, max_acceptable=100.0, critical_min=40.0, critical_max=120.0),
                        phosphorus=OptimalRange(min_optimal=40.0, max_optimal=50.0, min_acceptable=30.0, max_acceptable=60.0, critical_min=20.0, critical_max=80.0),
                        potassium=OptimalRange(min_optimal=90.0, max_optimal=110.0, min_acceptable=80.0, max_acceptable=120.0, critical_min=60.0, critical_max=140.0),
                        calcium=OptimalRange(min_optimal=180.0, max_optimal=220.0, min_acceptable=160.0, max_acceptable=240.0, critical_min=140.0, critical_max=260.0),
                        magnesium=OptimalRange(min_optimal=40.0, max_optimal=60.0, min_acceptable=30.0, max_acceptable=70.0, critical_min=20.0, critical_max=80.0),
                        iron=OptimalRange(min_optimal=2.5, max_optimal=3.5, min_acceptable=2.0, max_acceptable=4.0, critical_min=1.5, critical_max=5.0)
                    ),
                    max_yield_kg_per_m2=15.0
                )
            }
        )

        # ================================================================
        # ПЕРЕЦ (Capsicum annuum)
        # ================================================================
        kb[CropType.PEPPER] = CropRequirements(
            crop_type=CropType.PEPPER,
            stages={
                GrowthStage.SEEDLING: StageRequirements(
                    air=AirRanges(
                        temperature=OptimalRange(min_optimal=24.0, max_optimal=28.0, min_acceptable=20.0, max_acceptable=30.0, critical_min=15.0, critical_max=35.0),
                        humidity=OptimalRange(min_optimal=60.0, max_optimal=70.0, min_acceptable=50.0, max_acceptable=80.0, critical_min=35.0, critical_max=90.0),
                        atmospheric_pressure=OptimalRange(min_optimal=750.0, max_optimal=770.0, min_acceptable=700.0, max_acceptable=800.0, critical_min=600.0, critical_max=900.0)
                    ),
                    light=LightRanges(
                        wavelength=OptimalRange(min_optimal=450.0, max_optimal=500.0, min_acceptable=400.0, max_acceptable=550.0, critical_min=350.0, critical_max=600.0),
                        energy=OptimalRange(min_optimal=100.0, max_optimal=200.0, min_acceptable=50.0, max_acceptable=250.0, critical_min=20.0, critical_max=400.0),
                        hours=OptimalRange(min_optimal=12.0, max_optimal=14.0, min_acceptable=10.0, max_acceptable=16.0, critical_min=8.0, critical_max=18.0)
                    ),
                    solution=SolutionRanges(
                        nitrogen=OptimalRange(min_optimal=100.0, max_optimal=150.0, min_acceptable=80.0, max_acceptable=170.0, critical_min=50.0, critical_max=200.0),
                        phosphorus=OptimalRange(min_optimal=30.0, max_optimal=40.0, min_acceptable=20.0, max_acceptable=50.0, critical_min=10.0, critical_max=70.0),
                        potassium=OptimalRange(min_optimal=150.0, max_optimal=200.0, min_acceptable=130.0, max_acceptable=220.0, critical_min=100.0, critical_max=250.0),
                        calcium=OptimalRange(min_optimal=100.0, max_optimal=150.0, min_acceptable=80.0, max_acceptable=170.0, critical_min=50.0, critical_max=200.0),
                        magnesium=OptimalRange(min_optimal=40.0, max_optimal=60.0, min_acceptable=30.0, max_acceptable=70.0, critical_min=20.0, critical_max=80.0),
                        iron=OptimalRange(min_optimal=2.0, max_optimal=3.0, min_acceptable=1.5, max_acceptable=3.5, critical_min=1.0, critical_max=5.0)
                    ),
                    max_yield_kg_per_m2=0.0
                ),
                GrowthStage.VEGETATIVE: StageRequirements(
                    air=AirRanges(
                        temperature=OptimalRange(min_optimal=24.0, max_optimal=28.0, min_acceptable=20.0, max_acceptable=30.0, critical_min=15.0, critical_max=35.0),
                        humidity=OptimalRange(min_optimal=60.0, max_optimal=70.0, min_acceptable=50.0, max_acceptable=80.0, critical_min=35.0, critical_max=90.0),
                        atmospheric_pressure=OptimalRange(min_optimal=750.0, max_optimal=770.0, min_acceptable=700.0, max_acceptable=800.0, critical_min=600.0, critical_max=900.0)
                    ),
                    light=LightRanges(
                        wavelength=OptimalRange(min_optimal=500.0, max_optimal=600.0, min_acceptable=450.0, max_acceptable=650.0, critical_min=400.0, critical_max=700.0),
                        energy=OptimalRange(min_optimal=200.0, max_optimal=300.0, min_acceptable=150.0, max_acceptable=350.0, critical_min=100.0, critical_max=500.0),
                        hours=OptimalRange(min_optimal=14.0, max_optimal=16.0, min_acceptable=12.0, max_acceptable=18.0, critical_min=10.0, critical_max=20.0)
                    ),
                    solution=SolutionRanges(
                        nitrogen=OptimalRange(min_optimal=150.0, max_optimal=200.0, min_acceptable=130.0, max_acceptable=220.0, critical_min=100.0, critical_max=250.0),
                        phosphorus=OptimalRange(min_optimal=40.0, max_optimal=60.0, min_acceptable=30.0, max_acceptable=70.0, critical_min=20.0, critical_max=90.0),
                        potassium=OptimalRange(min_optimal=200.0, max_optimal=250.0, min_acceptable=180.0, max_acceptable=270.0, critical_min=150.0, critical_max=300.0),
                        calcium=OptimalRange(min_optimal=150.0, max_optimal=200.0, min_acceptable=130.0, max_acceptable=220.0, critical_min=100.0, critical_max=250.0),
                        magnesium=OptimalRange(min_optimal=50.0, max_optimal=70.0, min_acceptable=40.0, max_acceptable=80.0, critical_min=30.0, critical_max=100.0),
                        iron=OptimalRange(min_optimal=2.0, max_optimal=3.0, min_acceptable=1.5, max_acceptable=3.5, critical_min=1.0, critical_max=5.0)
                    ),
                    max_yield_kg_per_m2=0.0
                ),
                GrowthStage.FRUITING: StageRequirements(
                    air=AirRanges(
                        temperature=OptimalRange(min_optimal=24.0, max_optimal=28.0, min_acceptable=20.0, max_acceptable=30.0, critical_min=15.0, critical_max=35.0),
                        humidity=OptimalRange(min_optimal=60.0, max_optimal=70.0, min_acceptable=50.0, max_acceptable=80.0, critical_min=35.0, critical_max=90.0),
                        atmospheric_pressure=OptimalRange(min_optimal=750.0, max_optimal=770.0, min_acceptable=700.0, max_acceptable=800.0, critical_min=600.0, critical_max=900.0)
                    ),
                    light=LightRanges(
                        wavelength=OptimalRange(min_optimal=600.0, max_optimal=700.0, min_acceptable=550.0, max_acceptable=750.0, critical_min=500.0, critical_max=800.0),
                        energy=OptimalRange(min_optimal=300.0, max_optimal=400.0, min_acceptable=250.0, max_acceptable=450.0, critical_min=200.0, critical_max=600.0),
                        hours=OptimalRange(min_optimal=14.0, max_optimal=16.0, min_acceptable=12.0, max_acceptable=18.0, critical_min=10.0, critical_max=20.0)
                    ),
                    solution=SolutionRanges(
                        nitrogen=OptimalRange(min_optimal=120.0, max_optimal=170.0, min_acceptable=100.0, max_acceptable=190.0, critical_min=80.0, critical_max=220.0),
                        phosphorus=OptimalRange(min_optimal=50.0, max_optimal=70.0, min_acceptable=40.0, max_acceptable=80.0, critical_min=30.0, critical_max=100.0),
                        potassium=OptimalRange(min_optimal=250.0, max_optimal=300.0, min_acceptable=220.0, max_acceptable=330.0, critical_min=200.0, critical_max=350.0),
                        calcium=OptimalRange(min_optimal=150.0, max_optimal=200.0, min_acceptable=130.0, max_acceptable=220.0, critical_min=100.0, critical_max=250.0),
                        magnesium=OptimalRange(min_optimal=50.0, max_optimal=70.0, min_acceptable=40.0, max_acceptable=80.0, critical_min=30.0, critical_max=100.0),
                        iron=OptimalRange(min_optimal=2.0, max_optimal=3.0, min_acceptable=1.5, max_acceptable=3.5, critical_min=1.0, critical_max=5.0)
                    ),
                    max_yield_kg_per_m2=35.0
                )
            }
        )

        # ================================================================
        # БАЗИЛИК (Ocimum basilicum)
        # ================================================================
        kb[CropType.BASIL] = CropRequirements(
            crop_type=CropType.BASIL,
            stages={
                GrowthStage.SEEDLING: StageRequirements(
                    air=AirRanges(
                        temperature=OptimalRange(min_optimal=22.0, max_optimal=26.0, min_acceptable=20.0, max_acceptable=28.0, critical_min=15.0, critical_max=32.0),
                        humidity=OptimalRange(min_optimal=60.0, max_optimal=70.0, min_acceptable=50.0, max_acceptable=75.0, critical_min=35.0, critical_max=85.0),
                        atmospheric_pressure=OptimalRange(min_optimal=750.0, max_optimal=770.0, min_acceptable=700.0, max_acceptable=800.0, critical_min=600.0, critical_max=900.0)
                    ),
                    light=LightRanges(
                        wavelength=OptimalRange(min_optimal=450.0, max_optimal=500.0, min_acceptable=400.0, max_acceptable=550.0, critical_min=350.0, critical_max=600.0),
                        energy=OptimalRange(min_optimal=100.0, max_optimal=150.0, min_acceptable=50.0, max_acceptable=200.0, critical_min=20.0, critical_max=300.0),
                        hours=OptimalRange(min_optimal=10.0, max_optimal=12.0, min_acceptable=8.0, max_acceptable=14.0, critical_min=6.0, critical_max=16.0)
                    ),
                    solution=SolutionRanges(
                        nitrogen=OptimalRange(min_optimal=100.0, max_optimal=150.0, min_acceptable=80.0, max_acceptable=170.0, critical_min=50.0, critical_max=200.0),
                        phosphorus=OptimalRange(min_optimal=20.0, max_optimal=30.0, min_acceptable=15.0, max_acceptable=35.0, critical_min=10.0, critical_max=50.0),
                        potassium=OptimalRange(min_optimal=100.0, max_optimal=150.0, min_acceptable=80.0, max_acceptable=170.0, critical_min=50.0, critical_max=200.0),
                        calcium=OptimalRange(min_optimal=60.0, max_optimal=100.0, min_acceptable=50.0, max_acceptable=120.0, critical_min=40.0, critical_max=150.0),
                        magnesium=OptimalRange(min_optimal=30.0, max_optimal=50.0, min_acceptable=20.0, max_acceptable=60.0, critical_min=10.0, critical_max=80.0),
                        iron=OptimalRange(min_optimal=2.0, max_optimal=3.0, min_acceptable=1.5, max_acceptable=3.5, critical_min=1.0, critical_max=5.0)
                    ),
                    max_yield_kg_per_m2=0.0
                ),
                GrowthStage.VEGETATIVE: StageRequirements(
                    air=AirRanges(
                        temperature=OptimalRange(min_optimal=22.0, max_optimal=26.0, min_acceptable=20.0, max_acceptable=28.0, critical_min=15.0, critical_max=32.0),
                        humidity=OptimalRange(min_optimal=60.0, max_optimal=70.0, min_acceptable=50.0, max_acceptable=75.0, critical_min=35.0, critical_max=85.0),
                        atmospheric_pressure=OptimalRange(min_optimal=750.0, max_optimal=770.0, min_acceptable=700.0, max_acceptable=800.0, critical_min=600.0, critical_max=900.0)
                    ),
                    light=LightRanges(
                        wavelength=OptimalRange(min_optimal=500.0, max_optimal=600.0, min_acceptable=450.0, max_acceptable=650.0, critical_min=400.0, critical_max=700.0),
                        energy=OptimalRange(min_optimal=150.0, max_optimal=200.0, min_acceptable=100.0, max_acceptable=250.0, critical_min=50.0, critical_max=350.0),
                        hours=OptimalRange(min_optimal=14.0, max_optimal=16.0, min_acceptable=12.0, max_acceptable=18.0, critical_min=10.0, critical_max=20.0)
                    ),
                    solution=SolutionRanges(
                        nitrogen=OptimalRange(min_optimal=140.0, max_optimal=160.0, min_acceptable=120.0, max_acceptable=180.0, critical_min=100.0, critical_max=200.0),
                        phosphorus=OptimalRange(min_optimal=25.0, max_optimal=35.0, min_acceptable=20.0, max_acceptable=40.0, critical_min=15.0, critical_max=50.0),
                        potassium=OptimalRange(min_optimal=120.0, max_optimal=130.0, min_acceptable=100.0, max_acceptable=150.0, critical_min=80.0, critical_max=180.0),
                        calcium=OptimalRange(min_optimal=70.0, max_optimal=90.0, min_acceptable=60.0, max_acceptable=100.0, critical_min=50.0, critical_max=120.0),
                        magnesium=OptimalRange(min_optimal=50.0, max_optimal=70.0, min_acceptable=40.0, max_acceptable=80.0, critical_min=30.0, critical_max=100.0),
                        iron=OptimalRange(min_optimal=2.0, max_optimal=3.0, min_acceptable=1.5, max_acceptable=3.5, critical_min=1.0, critical_max=5.0)
                    ),
                    max_yield_kg_per_m2=8.0  # Урожай на стадии вегетации для зелени
                ),
                GrowthStage.FRUITING: StageRequirements(
                    air=AirRanges(
                        temperature=OptimalRange(min_optimal=22.0, max_optimal=26.0, min_acceptable=20.0, max_acceptable=28.0, critical_min=15.0, critical_max=32.0),
                        humidity=OptimalRange(min_optimal=60.0, max_optimal=70.0, min_acceptable=50.0, max_acceptable=75.0, critical_min=35.0, critical_max=85.0),
                        atmospheric_pressure=OptimalRange(min_optimal=750.0, max_optimal=770.0, min_acceptable=700.0, max_acceptable=800.0, critical_min=600.0, critical_max=900.0)
                    ),
                    light=LightRanges(
                        wavelength=OptimalRange(min_optimal=600.0, max_optimal=700.0, min_acceptable=550.0, max_acceptable=750.0, critical_min=500.0, critical_max=800.0),
                        energy=OptimalRange(min_optimal=150.0, max_optimal=200.0, min_acceptable=100.0, max_acceptable=250.0, critical_min=50.0, critical_max=350.0),
                        hours=OptimalRange(min_optimal=14.0, max_optimal=16.0, min_acceptable=12.0, max_acceptable=18.0, critical_min=10.0, critical_max=20.0)
                    ),
                    solution=SolutionRanges(
                        nitrogen=OptimalRange(min_optimal=140.0, max_optimal=160.0, min_acceptable=120.0, max_acceptable=180.0, critical_min=100.0, critical_max=200.0),
                        phosphorus=OptimalRange(min_optimal=25.0, max_optimal=35.0, min_acceptable=20.0, max_acceptable=40.0, critical_min=15.0, critical_max=50.0),
                        potassium=OptimalRange(min_optimal=120.0, max_optimal=130.0, min_acceptable=100.0, max_acceptable=150.0, critical_min=80.0, critical_max=180.0),
                        calcium=OptimalRange(min_optimal=70.0, max_optimal=90.0, min_acceptable=60.0, max_acceptable=100.0, critical_min=50.0, critical_max=120.0),
                        magnesium=OptimalRange(min_optimal=50.0, max_optimal=70.0, min_acceptable=40.0, max_acceptable=80.0, critical_min=30.0, critical_max=100.0),
                        iron=OptimalRange(min_optimal=2.0, max_optimal=3.0, min_acceptable=1.5, max_acceptable=3.5, critical_min=1.0, critical_max=5.0)
                    ),
                    max_yield_kg_per_m2=0.0  # Для базилика основная стадия - вегетация
                )
            }
        )

        return kb