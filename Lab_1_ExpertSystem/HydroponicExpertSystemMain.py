"""
Экспертная система для гидропоники
Главный файл запуска программы
"""

import os
from HydroponicExpertSystemModels import (
    CropType, EnvironmentParameters
)
from KnowledgeBaseCropRequirements import KnowledgeBase
from InferenceEngineAnalysis import InferenceEngine


def clear_screen():
    """Очистка экрана консоли"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(text):
    """Печать заголовка секции"""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70 + "\n")


def print_separator():
    """Печать разделителя"""
    print("-" * 70)


def input_float(prompt, min_val, max_val, default):
    """
    Ввод числа с плавающей точкой с валидацией

    Args:
        prompt: Текст приглашения
        min_val: Минимальное допустимое значение
        max_val: Максимальное допустимое значение
        default: Значение по умолчанию

    Returns:
        float: Введенное число
    """
    while True:
        user_input = input(f"{prompt} [по умолчанию {default}]: ").strip()

        if not user_input:
            return default

        try:
            num = float(user_input)
            if min_val <= num <= max_val:
                return num
            else:
                print(f"   Ошибка: значение должно быть от {min_val} до {max_val}")
        except ValueError:
            print("   Ошибка: введите корректное число")


def input_int(prompt, min_val, max_val):
    """
    Ввод целого числа с валидацией

    Args:
        prompt: Текст приглашения
        min_val: Минимальное допустимое значение
        max_val: Максимальное допустимое значение

    Returns:
        int: Введенное число
    """
    while True:
        user_input = input(f"{prompt} ({min_val}-{max_val}): ").strip()

        try:
            num = int(user_input)
            if min_val <= num <= max_val:
                return num
            else:
                print(f"   Ошибка: выберите число от {min_val} до {max_val}")
        except ValueError:
            print("   Ошибка: введите целое число")


def select_crop(kb):
    """
    ШАГ 1: Выбор культуры

    Args:
        kb: База знаний

    Returns:
        CropType: Выбранная культура
    """
    clear_screen()
    print_header("ШАГ 1: ВЫБОР КУЛЬТУРЫ")

    # Список доступных культур
    crops = kb.get_all_crops()
    print("Доступные культуры:\n")
    for i, crop in enumerate(crops, 1):
        print(f"  {i}. {crop.value.upper()}")

    # Выбор культуры
    crop_choice = input_int("\nВыберите номер культуры", 1, len(crops))
    selected_crop = crops[crop_choice - 1]

    print_separator()
    print(f"\nВыбрано: {selected_crop.value.upper()}")

    # Показываем информацию о культуре
    print(f"\n{kb.get_crop_info(selected_crop)}")

    # Показываем оптимальные параметры для выбранной культуры
    try:
        req = kb.get_requirements(selected_crop)
        print("\nОптимальные параметры для этой культуры:")
        print(f"  Температура: {req.temperature.min_optimal}-{req.temperature.max_optimal} C")
        print(f"  Влажность: {req.humidity.min_optimal}-{req.humidity.max_optimal} %")
        print(f"  pH: {req.ph.min_optimal}-{req.ph.max_optimal}")
        print(f"  EC: {req.ec.min_optimal}-{req.ec.max_optimal} mS/cm")
        print(f"  Освещенность: {req.light_intensity.min_optimal}-{req.light_intensity.max_optimal} µmol/m²/s")
        print(f"  Световой день: {req.light_hours.min_optimal}-{req.light_hours.max_optimal} ч")
    except ValueError as e:
        print(f"\nВнимание: {str(e)}")

    input("\nНажмите Enter для продолжения...")
    return selected_crop


def input_parameters():
    """
    ШАГ 2: Ввод параметров среды

    Returns:
        EnvironmentParameters: Объект с параметрами или None при ошибке
    """
    clear_screen()
    print_header("ШАГ 2: ВВОД ПАРАМЕТРОВ СРЕДЫ")

    print("Введите текущие параметры вашей гидропонной системы.\n")
    print("Вы можете нажать Enter для использования значений по умолчанию.\n")

    try:
        # Ввод температуры
        temperature = input_float(
            "Температура воздуха (C)",
            min_val=0, max_val=50, default=24.0
        )

        # Ввод влажности
        humidity = input_float(
            "Влажность воздуха (%)",
            min_val=0, max_val=100, default=65.0
        )

        # Ввод pH
        ph = input_float(
            "pH раствора",
            min_val=0, max_val=14, default=6.0
        )

        # Ввод EC
        ec = input_float(
            "EC - электропроводность (mS/cm)",
            min_val=0, max_val=10, default=2.0
        )

        # Ввод освещенности
        light_intensity = input_float(
            "Освещенность (µmol/m²/s)",
            min_val=0, max_val=2000, default=600.0
        )

        # Ввод продолжительности светового дня
        light_hours = input_float(
            "Продолжительность светового дня (часов)",
            min_val=0, max_val=24, default=16.0
        )

        # Создаем объект с параметрами
        params = EnvironmentParameters(
            temperature=temperature,
            humidity=humidity,
            ph=ph,
            ec=ec,
            light_intensity=light_intensity,
            light_hours=light_hours
        )

        # Подтверждение введенных данных
        print_separator()
        print("\nВведенные параметры:")
        print(f"  Температура: {params.temperature} C")
        print(f"  Влажность: {params.humidity} %")
        print(f"  pH: {params.ph}")
        print(f"  EC: {params.ec} mS/cm")
        print(f"  Освещенность: {params.light_intensity} µmol/m²/s")
        print(f"  Световой день: {params.light_hours} ч")

        input("\nНажмите Enter для продолжения к анализу...")
        return params

    except ValueError as e:
        print(f"\nОшибка валидации: {str(e)}")
        input("\nНажмите Enter для продолжения...")
        return None


def analyze_and_show_results(params, crop, kb, engine):
    """
    ШАГ 3: Анализ условий и вывод результатов

    Args:
        params: Параметры среды
        crop: Тип культуры
        kb: База знаний
        engine: Движок анализа
    """
    clear_screen()
    print_header("ШАГ 3: АНАЛИЗ УСЛОВИЙ И РЕЗУЛЬТАТЫ")

    print(f"Культура: {crop.value.upper()}")

    print("\nВаши текущие параметры:")
    print(f"  Температура: {params.temperature} C")
    print(f"  Влажность: {params.humidity} %")
    print(f"  pH: {params.ph}")
    print(f"  EC: {params.ec} mS/cm")
    print(f"  Освещенность: {params.light_intensity} µmol/m²/s")
    print(f"  Световой день: {params.light_hours} ч")

    print("\nВыполняется анализ условий...")

    try:
        # Получаем требования для выбранной культуры
        requirements = kb.get_requirements(crop)

        # Выполняем анализ
        result = engine.analyze(params, requirements)

        # Выводим результаты анализа
        print("\n" + "=" * 70)
        print("РЕЗУЛЬТАТЫ АНАЛИЗА".center(70))
        print("=" * 70)

        # Основные показатели
        print(f"\nОбщая оценка здоровья растения: {result.health_score:.1f}/100")
        print(f"Вероятность выживания: {result.survival_probability * 100:.1f}%")
        print(f"Прогноз урожайности: {result.yield_forecast * 100:.1f}% от максимума")
        print(f"Ожидаемая урожайность: {result.max_yield_kg_per_m2:.1f} кг/м^2 в год")

        max_yield = requirements.max_yield_kg_per_m2
        print(f"(Максимум для {crop.value}: {max_yield:.1f} кг/м² в год)")

        # Детальные оценки параметров
        print("\nОценки по каждому параметру:")
        print("(0.0 - критично, 0.5 - допустимо, 1.0 - идеально)\n")

        for param_name, score in result.parameter_scores.items():
            # Визуальная шкала
            bar_length = int(score * 20)
            bar = "#" * bar_length + "-" * (20 - bar_length)
            print(f"  {param_name:20s}: {score:.2f} [{bar}]")

        # Критические проблемы
        if result.critical_issues:
            print("\n" + "=" * 70)
            print(f"КРИТИЧЕСКИЕ ПРОБЛЕМЫ ({len(result.critical_issues)}):")
            print("=" * 70)
            for i, issue in enumerate(result.critical_issues, 1):
                print(f"\n{i}. {issue}")

        # Предупреждения
        if result.warnings:
            print("\n" + "=" * 70)
            print(f"ПРЕДУПРЕЖДЕНИЯ ({len(result.warnings)}):")
            print("=" * 70)
            for i, warning in enumerate(result.warnings, 1):
                print(f"\n{i}. {warning}")

        # Рекомендации
        if result.recommendations:
            print("\n" + "=" * 70)
            print("РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ УСЛОВИЙ:")
            print("=" * 70)
            for i, rec in enumerate(result.recommendations, 1):
                print(f"\n{i}. {rec}")

        # Целевые (оптимальные) параметры
        print("\n" + "=" * 70)
        print("ЦЕЛЕВЫЕ ПАРАМЕТРЫ (К ЧЕМУ СТРЕМИТЬСЯ):")
        print("=" * 70)
        opt = result.optimal_parameters
        print(f"\n  Температура: {opt.temperature:.1f} C")
        print(f"  Влажность: {opt.humidity:.1f} %")
        print(f"  pH: {opt.ph:.2f}")
        print(f"  EC: {opt.ec:.2f} mS/cm")
        print(f"  Освещенность: {opt.light_intensity:.0f} µmol/m²/s")
        print(f"  Световой день: {opt.light_hours:.1f} ч")

        print("\n" + "=" * 70)

    except ValueError as e:
        print(f"\nОшибка при анализе: {str(e)}")
        print("Проверьте корректность введенных данных.")


def main():
    """
    Главная функция программы
    """
    # Инициализация системы
    kb = KnowledgeBase()
    engine = InferenceEngine()

    # Очистка экрана и приветствие
    clear_screen()
    print("=" * 70)
    print("ЭКСПЕРТНАЯ СИСТЕМА ДЛЯ ГИДРОПОНИКИ".center(70))
    print("=" * 70)
    print("\nАнализ условий выращивания растений")
    print("Прогнозирование урожайности и выживаемости")
    print("\nВерсия: 1.0")
    print("\nРабота программы состоит из 3 шагов:")
    print("  1. Выбор культуры")
    print("  2. Ввод текущих параметров среды")
    print("  3. Получение анализа и рекомендаций")

    input("\nНажмите Enter для начала работы...")

    # Главный цикл программы
    while True:
        # ШАГ 1: Выбор культуры
        crop = select_crop(kb)

        # ШАГ 2: Ввод параметров среды
        params = input_parameters()

        # Проверка корректности ввода
        if params is None:
            print("\nОшибка при вводе параметров.")
            retry = input("Попробовать снова? (y/n): ").strip().lower()
            if retry != 'y':
                break
            continue

        # ШАГ 3: Анализ и вывод результатов
        analyze_and_show_results(params, crop, kb, engine)

        # Предложение выполнить еще один анализ
        print("\n")
        again = input("Выполнить анализ для другой культуры? (y/n): ").strip().lower()
        if again != 'y':
            break

    # Завершение работы
    clear_screen()
    print("\n" + "=" * 70)
    print("Спасибо за использование экспертной системы!".center(70))
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()