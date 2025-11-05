"""
Содержит графический интерфейс пользователя (GUI) на основе Tkinter
для ввода параметров для трех стадий роста одновременно,
выбора культуры, запуска анализа и вывода результатов.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict
from HydroponicExpertSystemModels import (
    CropType, GrowthStage, EnvironmentParameters, AirParameters,
    LightParameters, SolutionParameters, AnalysisResult
)
from KnowledgeBaseCropRequirements import KnowledgeBase
from InferenceEngineAnalysis import InferenceEngine

class HydroponicGUI:
    """
    Класс графического интерфейса для экспертной системы гидропоники
    """
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("Экспертная система гидропоники")
        self.master.geometry("1200x800")

        # Инициализация базы знаний и движка анализа
        self.kb = KnowledgeBase()
        self.engine = InferenceEngine()

        # Словарь для хранения переменных по стадиям
        self.param_vars = {
            GrowthStage.SEEDLING: self._create_param_vars(),
            GrowthStage.VEGETATIVE: self._create_param_vars(),
            GrowthStage.FRUITING: self._create_param_vars()
        }

        # Создание виджетов GUI
        self._create_widgets()

    def _create_param_vars(self):
        """Создание набора переменных для одной стадии"""
        return {
            'temperature': tk.DoubleVar(value=25.0),
            'humidity': tk.DoubleVar(value=60.0),
            'atmospheric_pressure': tk.DoubleVar(value=760.0),
            'wavelength': tk.DoubleVar(value=550.0),
            'energy': tk.DoubleVar(value=200.0),
            'hours': tk.DoubleVar(value=14.0),
            'nitrogen': tk.DoubleVar(value=100.0),
            'phosphorus': tk.DoubleVar(value=40.0),
            'potassium': tk.DoubleVar(value=150.0),
            'calcium': tk.DoubleVar(value=100.0),
            'magnesium': tk.DoubleVar(value=50.0),
            'iron': tk.DoubleVar(value=2.0)
        }

    def _create_widgets(self):
        """Создание элементов интерфейса"""
        # Фрейм для выбора культуры
        selection_frame = ttk.LabelFrame(self.master, text="Выбор культуры")
        selection_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(selection_frame, text="Культура:").grid(row=0, column=0, padx=5, pady=5)
        self.crop_var = tk.StringVar()
        crop_combo = ttk.Combobox(
            selection_frame,
            textvariable=self.crop_var,
            values=[crop.value for crop in CropType],
            state="readonly"
        )
        crop_combo.grid(row=0, column=1, padx=5, pady=5)
        crop_combo.current(0)

        # Фрейм для ввода параметров по стадиям
        params_notebook = ttk.Notebook(self.master)
        params_notebook.pack(pady=10, padx=10, fill="both", expand=True)

        for stage in GrowthStage:
            stage_frame = ttk.Frame(params_notebook)
            params_notebook.add(stage_frame, text=stage.value)

            # Параметры воздуха
            air_frame = ttk.LabelFrame(stage_frame, text="Параметры воздуха")
            air_frame.grid(row=0, column=0, padx=10, pady=5, sticky="n")

            ttk.Label(air_frame, text="Температура (°C):").grid(row=0, column=0)
            ttk.Entry(air_frame, textvariable=self.param_vars[stage]['temperature']).grid(row=0, column=1)

            ttk.Label(air_frame, text="Влажность (%):").grid(row=1, column=0)
            ttk.Entry(air_frame, textvariable=self.param_vars[stage]['humidity']).grid(row=1, column=1)

            ttk.Label(air_frame, text="Давление (мм рт. ст.):").grid(row=2, column=0)
            ttk.Entry(air_frame, textvariable=self.param_vars[stage]['atmospheric_pressure']).grid(row=2, column=1)

            # Параметры освещения
            light_frame = ttk.LabelFrame(stage_frame, text="Параметры освещения")
            light_frame.grid(row=0, column=1, padx=10, pady=5, sticky="n")

            ttk.Label(light_frame, text="Длина волны (нм):").grid(row=0, column=0)
            ttk.Entry(light_frame, textvariable=self.param_vars[stage]['wavelength']).grid(row=0, column=1)

            ttk.Label(light_frame, text="Энергия (Вт/м²):").grid(row=1, column=0)
            ttk.Entry(light_frame, textvariable=self.param_vars[stage]['energy']).grid(row=1, column=1)

            ttk.Label(light_frame, text="Световой день (ч):").grid(row=2, column=0)
            ttk.Entry(light_frame, textvariable=self.param_vars[stage]['hours']).grid(row=2, column=1)

            # Параметры раствора
            solution_frame = ttk.LabelFrame(stage_frame, text="Параметры раствора (мг/л)")
            solution_frame.grid(row=0, column=2, padx=10, pady=5, sticky="n")

            ttk.Label(solution_frame, text="Азот (N):").grid(row=0, column=0)
            ttk.Entry(solution_frame, textvariable=self.param_vars[stage]['nitrogen']).grid(row=0, column=1)

            ttk.Label(solution_frame, text="Фосфор (P):").grid(row=1, column=0)
            ttk.Entry(solution_frame, textvariable=self.param_vars[stage]['phosphorus']).grid(row=1, column=1)

            ttk.Label(solution_frame, text="Калий (K):").grid(row=2, column=0)
            ttk.Entry(solution_frame, textvariable=self.param_vars[stage]['potassium']).grid(row=2, column=1)

            ttk.Label(solution_frame, text="Кальций (Ca):").grid(row=3, column=0)
            ttk.Entry(solution_frame, textvariable=self.param_vars[stage]['calcium']).grid(row=3, column=1)

            ttk.Label(solution_frame, text="Магний (Mg):").grid(row=4, column=0)
            ttk.Entry(solution_frame, textvariable=self.param_vars[stage]['magnesium']).grid(row=4, column=1)

            ttk.Label(solution_frame, text="Железо (Fe):").grid(row=5, column=0)
            ttk.Entry(solution_frame, textvariable=self.param_vars[stage]['iron']).grid(row=5, column=1)

        # Кнопка анализа
        analyze_button = ttk.Button(self.master, text="Анализировать все стадии", command=self._analyze)
        analyze_button.pack(pady=10)

        # Область для вывода результатов
        self.result_text = tk.Text(self.master, height=15, wrap="word")
        self.result_text.pack(pady=10, padx=10, fill="both", expand=True)

    def _analyze(self):
        """Запуск анализа для всех трех стадий"""
        try:
            # Получение выбранной культуры
            crop_name = self.crop_var.get()
            crop_type = next((ct for ct in CropType if ct.value == crop_name), None)
            if not crop_type:
                raise ValueError("Выберите культуру")

            # Получение требований
            requirements = self.kb.get_requirements(crop_type)

            results = {}
            for stage in GrowthStage:
                vars_dict = self.param_vars[stage]
                air = AirParameters(
                    temperature=vars_dict['temperature'].get(),
                    humidity=vars_dict['humidity'].get(),
                    atmospheric_pressure=vars_dict['atmospheric_pressure'].get()
                )
                light = LightParameters(
                    wavelength=vars_dict['wavelength'].get(),
                    energy=vars_dict['energy'].get(),
                    hours=vars_dict['hours'].get()
                )
                solution = SolutionParameters(
                    nitrogen=vars_dict['nitrogen'].get(),
                    phosphorus=vars_dict['phosphorus'].get(),
                    potassium=vars_dict['potassium'].get(),
                    calcium=vars_dict['calcium'].get(),
                    magnesium=vars_dict['magnesium'].get(),
                    iron=vars_dict['iron'].get()
                )
                current_params = EnvironmentParameters(air=air, light=light, solution=solution)

                # Запуск анализа для стадии
                result = self.engine.analyze(current_params, requirements, stage)
                results[stage] = result

            # Совокупный прогноз урожайности: учитываем все стадии, но показываем только на стадии плодоношения
            cumulative_yield = 1.0
            for st, res in results.items():
                # Страхуемся от выхода за 0..1
                yf = max(0.0, min(1.0, res.yield_forecast))
                cumulative_yield *= yf

            # Применяем итоговый прогноз только к стадии плодоношения
            fruiting_stage = GrowthStage.FRUITING
            if fruiting_stage in results:
                fr_res = results[fruiting_stage]
                fr_res.yield_forecast = max(0.0, min(1.0, cumulative_yield))
                fr_res.max_yield_kg_per_m2 = fr_res.yield_forecast * requirements.stages[fruiting_stage].max_yield_kg_per_m2

            # На ранних стадиях урожай не отображаем
            for st in (GrowthStage.SEEDLING, GrowthStage.VEGETATIVE):
                if st in results:
                    results[st].yield_forecast = 0.0
                    results[st].max_yield_kg_per_m2 = 0.0

            # Вывод результатов
            self._display_results(results)

        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка анализа", f"Произошла ошибка: {str(e)}")

    def _display_results(self, results: Dict[GrowthStage, AnalysisResult]):
        """Отображение результатов анализа для всех стадий в текстовом поле"""
        self.result_text.delete(1.0, tk.END)

        for stage, result in results.items():
            text = f"=== Стадия: {stage.value} ===\n"
            text += f"Статус: {result.get_status_text()}\n"
            text += f"Оценка здоровья: {result.health_score}\n"
            text += f"Вероятность выживания: {result.get_survival_percentage()}%\n"
            if stage == GrowthStage.FRUITING:
                text += f"Прогноз урожайности: {result.get_yield_percentage()}% от максимума ({result.max_yield_kg_per_m2} кг/м²)\n\n"
            else:
                text += "\n"

            if result.critical_issues:
                text += "Критические проблемы:\n"
                for issue in result.critical_issues:
                    text += f"- {issue}\n"

            if result.warnings:
                text += "\nПредупреждения:\n"
                for warning in result.warnings:
                    text += f"- {warning}\n"

            if result.recommendations:
                text += "\nРекомендации:\n"
                for rec in result.recommendations:
                    text += f"- {rec}\n"

            text += "\n"
            self.result_text.insert(tk.END, text)

def main():
    """Запуск приложения"""
    root = tk.Tk()
    app = HydroponicGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()