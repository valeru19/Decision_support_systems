"""
Визуализация вероятностей заболеваний
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class ProbabilityVisualizer:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.setup_visualization()

    def setup_visualization(self):
        """Настройка визуализации"""
        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Настройка внешнего вида графика
        self.ax.set_facecolor('#f0f0f0')
        self.fig.patch.set_facecolor('#f0f0f0')

    def update_probabilities(self, probabilities: Dict[str, float],
                             accepted_diagnosis: str = None):
        """Обновить график вероятностей"""
        self.ax.clear()

        # Фильтруем заболевания с вероятностью > 0
        filtered_probs = {k: v for k, v in probabilities.items() if v > 0.001} if probabilities else {}

        # Шкала «Здоров» теперь является такой же гипотезой, как и остальные диагнозы.
        # Если она присутствует в словаре вероятностей, используем её значение.
        # Если по каким-то причинам её нет (обратная совместимость), вычисляем как 1 - max(probabilities).
        if probabilities:
            if "Здоров" not in probabilities:
                max_prob = max(probabilities.values()) if probabilities else 0.0
                healthy_prob = max(0.0, 1.0 - max_prob)
                filtered_probs["Здоров"] = healthy_prob
            else:
                # Гарантируем, что «Здоров» всегда присутствует на графике
                filtered_probs["Здоров"] = probabilities.get("Здоров", 0.0)
        else:
            # Если вероятностей нет, показываем только «Здоров» как 100%
            filtered_probs = {"Здоров": 1.0}

        if not filtered_probs:
            self.ax.text(0.5, 0.5, "Нет данных", ha='center', va='center', fontsize=14)
            self.canvas.draw()
            return

        diseases = list(filtered_probs.keys())
        probs = list(filtered_probs.values())

        # Сортируем по вероятности
        sorted_indices = np.argsort(probs)
        diseases = [diseases[i] for i in sorted_indices]
        probs = [probs[i] for i in sorted_indices]

        # Создаем цветовую схему
        colors = []
        for disease in diseases:
            if disease == accepted_diagnosis:
                colors.append('#4CAF50')  # Зеленый для принятого диагноза
            elif disease == "Здоров":
                # Нейтрально-зеленый оттенок для шкалы «Здоров»,
                # если он не является принятым диагнозом
                colors.append('#7BC67B')
            elif filtered_probs[disease] > 0.5:
                colors.append('#FF9800')  # Оранжевый для вероятных диагнозов
            elif filtered_probs[disease] > 0.1:
                colors.append('#2196F3')  # Синий для возможных диагнозов
            else:
                colors.append('#9E9E9E')  # Серый для маловероятных

        # Создаем горизонтальную столбчатую диаграмму
        bars = self.ax.barh(range(len(diseases)), probs, color=colors, height=0.6)

        # Добавляем значения вероятностей
        for i, (bar, prob) in enumerate(zip(bars, probs)):
            # Выводим проценты, чтобы соответствовать остальным текстовым блокам
            self.ax.text(min(0.98, prob + 0.01), bar.get_y() + bar.get_height() / 2,
                         f'{prob:.2%}', va='center')

        # Настройка осей
        self.ax.set_yticks(range(len(diseases)))
        self.ax.set_yticklabels(diseases, fontsize=10)
        self.ax.set_xlabel('Вероятность', fontsize=12)
        self.ax.set_title('Вероятности заболеваний', fontsize=14, pad=15)

        # Ограничиваем оси
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(-0.5, len(diseases) - 0.5)

        # Добавляем сетку
        self.ax.grid(True, axis='x', alpha=0.3)

        # Добавляем легенду
        legend_items = ['Диагноз принят', 'Здоров (оценка)', 'Вероятный', 'Возможный', 'Маловероятный']
        self.ax.legend(legend_items, loc='upper right', bbox_to_anchor=(1.0, -0.1))

        self.fig.tight_layout()
        self.canvas.draw()