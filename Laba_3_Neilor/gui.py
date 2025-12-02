"""
Исправленный графический интерфейс с поддержкой разных типов вопросов
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, Dict
import webbrowser

from diagnostic_engine import DiagnosticEngine
from probability_visualizer import ProbabilityVisualizer
from results_logger import ResultsLogger
from disease_database import DISEASES_DATABASE, SYMPTOM_QUESTIONS

class MedicalDiagnosticGUI:
    def __init__(self):
        self.diagnostic_engine = DiagnosticEngine()
        self.results_logger = ResultsLogger()
        self.current_question_data: Optional[Dict] = None

        self.setup_gui()
        self.start_new_diagnosis()

    def setup_gui(self):
        """Настройка графического интерфейса"""
        self.root = tk.Tk()
        self.root.title("Медицинская диагностическая система - Улучшенная версия")
        self.root.geometry("1300x850")

        # Настройка стилей
        self.setup_styles()

        # Создание виджетов
        self.create_widgets()

    def setup_styles(self):
        """Настройка стилей виджетов"""
        style = ttk.Style()
        style.theme_use('clam')

        # Кастомные стили
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'))
        style.configure('Question.TLabel', font=('Arial', 14))
        style.configure('Result.TLabel', font=('Arial', 16, 'bold'), foreground='green')
        style.configure('Option.TRadiobutton', font=('Arial', 12))

    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка весов
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)

        # Левая панель - вопросы и ответы
        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(0, weight=1)
        left_panel.rowconfigure(1, weight=2)

        # Панель вопроса
        self.question_panel = ttk.LabelFrame(left_panel, text="Диагностический опрос", padding="20")
        self.question_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.question_panel.columnconfigure(0, weight=1)

        # Текст вопроса
        self.question_label = ttk.Label(self.question_panel, text="",
                                       style='Question.TLabel', wraplength=600)
        self.question_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 20))

        # Панель ответов (будет меняться в зависимости от типа вопроса)
        self.answer_frame = ttk.Frame(self.question_panel)
        self.answer_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        # Кнопки ответа
        button_frame = ttk.Frame(self.question_panel)
        button_frame.grid(row=2, column=0, sticky=tk.E)

        ttk.Button(button_frame, text="Пропустить вопрос",
                  command=self.skip_question, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Ответить",
                  command=self.process_answer, width=20).pack(side=tk.LEFT, padx=5)

        # Панель истории вопросов
        history_panel = ttk.LabelFrame(left_panel, text="История ответов", padding="15")
        history_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        history_panel.columnconfigure(0, weight=1)
        history_panel.rowconfigure(0, weight=1)

        # Текстовое поле для истории
        self.history_text = scrolledtext.ScrolledText(history_panel, height=12, width=60,
                                                     font=('Arial', 10))
        self.history_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.history_text.config(state='disabled')

        # Правая панель - вероятности и информация
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=3)
        right_panel.rowconfigure(1, weight=2)

        # Панель визуализации вероятностей
        viz_panel = ttk.LabelFrame(right_panel, text="Вероятности заболеваний", padding="10")
        viz_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        viz_panel.columnconfigure(0, weight=1)
        viz_panel.rowconfigure(0, weight=1)

        # Создаем визуализатор вероятностей
        self.visualizer = ProbabilityVisualizer(viz_panel)

        # Панель информации о диагнозе
        info_panel = ttk.LabelFrame(right_panel, text="Информация о диагнозе", padding="15")
        info_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        info_panel.columnconfigure(0, weight=1)
        info_panel.rowconfigure(0, weight=1)

        # Текстовое поле для информации
        self.info_text = scrolledtext.ScrolledText(info_panel, height=10, width=45,
                                                  font=('Arial', 10))
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.info_text.config(state='disabled')

        # Статусная панель
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))

        self.status_label = ttk.Label(status_frame, text="Готов к диагностике", font=('Arial', 11))
        self.status_label.pack(side=tk.LEFT)

        self.progress_label = ttk.Label(status_frame, text="Вопросов: 0/25", font=('Arial', 11))
        self.progress_label.pack(side=tk.RIGHT)

        # Кнопки управления внизу
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, sticky=tk.E, pady=(10, 0))

        ttk.Button(control_frame, text="Новая диагностика",
                  command=self.start_new_diagnosis, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Сохранить результаты",
                  command=self.save_results, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="История",
                  command=self.show_history, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Справка",
                  command=self.show_help, width=20).pack(side=tk.LEFT, padx=5)

    def setup_answer_widgets(self, question_type: str, options: Dict = None):
        """Настроить виджеты для ответа в зависимости от типа вопроса"""
        # Очищаем предыдущие виджеты
        for widget in self.answer_frame.winfo_children():
            widget.destroy()

        self.answer_var = tk.StringVar(value="")

        if question_type == "binary" and options:
            # Бинарный вопрос с вариантами
            row = 0
            for option_text, option_value in options.items():
                rb = ttk.Radiobutton(self.answer_frame, text=option_text,
                                    variable=self.answer_var, value=str(option_value),
                                    style='Option.TRadiobutton')
                rb.grid(row=row, column=0, sticky=tk.W, pady=5)
                row += 1

        elif question_type == "scale":
            # Шкала от 1 до 10
            scale_frame = ttk.Frame(self.answer_frame)
            scale_frame.grid(row=0, column=0, sticky=tk.W)

            ttk.Label(scale_frame, text="Выберите значение:").grid(row=0, column=0, columnspan=10, sticky=tk.W)

            # Создаем радиокнопки для шкалы 1-10
            for i in range(1, 11):
                rb_frame = ttk.Frame(scale_frame)
                rb_frame.grid(row=1, column=i-1, padx=2)

                rb = ttk.Radiobutton(rb_frame, text=str(i), variable=self.answer_var, value=str(i))
                rb.grid(row=0, column=0)

                if i == 1:
                    ttk.Label(rb_frame, text="Нет").grid(row=1, column=0)
                elif i == 10:
                    ttk.Label(rb_frame, text="Макс").grid(row=1, column=0)

        elif question_type == "range" and options:
            # Диапазон значений
            row = 0
            for option_text, option_value in options.items():
                rb = ttk.Radiobutton(self.answer_frame, text=option_text,
                                    variable=self.answer_var, value=str(option_value),
                                    style='Option.TRadiobutton')
                rb.grid(row=row, column=0, sticky=tk.W, pady=5)
                row += 1

        elif question_type == "options" and options:
            # Множественный выбор
            row = 0
            for option_text, option_value in options.items():
                rb = ttk.Radiobutton(self.answer_frame, text=option_text,
                                    variable=self.answer_var, value=str(option_value),
                                    style='Option.TRadiobutton')
                rb.grid(row=row, column=0, sticky=tk.W, pady=5)
                row += 1

        else:
            # По умолчанию - шкала уверенности
            confidence_frame = ttk.Frame(self.answer_frame)
            confidence_frame.grid(row=0, column=0, sticky=tk.W)

            ttk.Label(confidence_frame, text="Ваша уверенность:").grid(row=0, column=0,
                                                                       columnspan=11, sticky=tk.W)

            # Переменная для хранения уверенности
            self.confidence_var = tk.IntVar(value=0)

            # Создаем радиокнопки для шкалы -5..+5
            values = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
            labels = ["-5", "-4", "-3", "-2", "-1", "0", "1", "2", "3", "4", "+5"]
            tooltips = [
                "Определенно нет",
                "Скорее нет",
                "Вероятно нет",
                "Слегка нет",
                "Скорее нет, чем да",
                "Не знаю/Не уверен",
                "Скорее да, чем нет",
                "Слегка да",
                "Вероятно да",
                "Скорее да",
                "Определенно да"
            ]

            for i, (val, label, tooltip) in enumerate(zip(values, labels, tooltips)):
                rb_frame = ttk.Frame(confidence_frame)
                rb_frame.grid(row=1, column=i, padx=2)

                rb = ttk.Radiobutton(rb_frame, variable=self.confidence_var, value=val)
                rb.grid(row=0, column=0)
                self.create_tooltip(rb, tooltip)

                lbl = ttk.Label(rb_frame, text=label)
                lbl.grid(row=1, column=0)
                self.create_tooltip(lbl, tooltip)

            self.answer_var = self.confidence_var

    def ask_next_question(self):
        """Задать следующий вопрос"""
        # Проверяем, следует ли продолжать диагностику
        if not self.diagnostic_engine.should_continue_diagnosis():
            self.show_diagnosis_results()
            return

        # Получаем следующий вопрос
        symptom, question_text, question_data = self.diagnostic_engine.get_next_question()

        if not question_text:
            self.show_diagnosis_results()
            return

        self.current_question_data = {
            "symptom": symptom,
            "question_data": question_data
        }

        # Обновляем текст вопроса
        question_num = len(self.diagnostic_engine.question_manager.question_history) + 1
        max_questions = self.diagnostic_engine.max_questions
        self.question_label.config(text=f"Вопрос {question_num}/{max_questions}:\n{question_text}")

        # Настраиваем виджеты для ответа
        question_type = question_data.get("type", "confidence")
        options = question_data.get("options", None)
        self.setup_answer_widgets(question_type, options)

        # Добавляем в историю
        self.add_to_history(f"Вопрос {question_num}: {question_text}")

        # Обновляем визуализацию
        self.update_visualization()

        # Обновляем статус
        self.update_status()

    def create_tooltip(self, widget, text):
        """Создать всплывающую подсказку"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

            label = ttk.Label(tooltip, text=text, background="#ffffe0",
                            relief="solid", borderwidth=1, padding=5)
            label.pack()

            def hide_tooltip(event):
                tooltip.destroy()

            widget.bind('<Leave>', hide_tooltip)

        widget.bind('<Enter>', show_tooltip)

    def start_new_diagnosis(self):
        """Начать новую диагностику"""
        self.diagnostic_engine.reset()
        self.current_question_data = None

        # Очищаем историю
        self.history_text.config(state='normal')
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state='disabled')

        # Очищаем информацию
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state='disabled')

        # Очищаем панель ответов
        for widget in self.answer_frame.winfo_children():
            widget.destroy()

        # Обновляем статус
        self.status_label.config(text="Начата новая диагностика")

        # Задаем первый вопрос
        self.ask_next_question()

    def ask_next_question(self):
        """Задать следующий вопрос"""
        # Проверяем, завершена ли диагностика
        if self.diagnostic_engine.is_diagnosis_complete():
            self.show_diagnosis_results()
            return

        # Получаем следующий вопрос
        symptom, question_text, question_data = self.diagnostic_engine.get_next_question()

        if not question_text:
            self.show_diagnosis_results()
            return

        self.current_question_data = {
            "symptom": symptom,
            "question_data": question_data
        }

        # Обновляем текст вопроса
        question_num = len(self.diagnostic_engine.question_manager.question_history) + 1
        max_questions = self.diagnostic_engine.max_questions
        self.question_label.config(text=f"Вопрос {question_num}/{max_questions}:\n{question_text}")

        # Настраиваем виджеты для ответа
        question_type = question_data.get("type", "confidence")
        options = question_data.get("options", None)
        self.setup_answer_widgets(question_type, options)

        # Добавляем в историю
        self.add_to_history(f"Вопрос {question_num}: {question_text}")

        # Обновляем визуализацию
        self.update_visualization()

        # Обновляем статус
        self.update_status()

    def process_answer(self):
        """Обработать ответ пользователя"""
        if not self.current_question_data:
            return

        # Получаем ответ в зависимости от типа вопроса
        symptom = self.current_question_data["symptom"]
        question_data = self.current_question_data["question_data"]
        question_type = question_data.get("type", "confidence")

        confidence = 0.5  # По умолчанию

        if question_type in ["binary", "range", "options"]:
            # Для вопросов с вариантами ответа
            answer_str = self.answer_var.get()
            if answer_str:
                try:
                    confidence = float(answer_str)
                except ValueError:
                    messagebox.showwarning("Ошибка", "Пожалуйста, выберите ответ")
                    return
            else:
                messagebox.showwarning("Ошибка", "Пожалуйста, выберите ответ")
                return

        elif question_type == "scale":
            # Для шкалы 1-10
            answer_str = self.answer_var.get()
            if answer_str:
                try:
                    # Преобразуем 1-10 в 0-1
                    scale_value = int(answer_str)
                    confidence = (scale_value - 1) / 9.0  # 1->0, 10->1
                except ValueError:
                    messagebox.showwarning("Ошибка", "Пожалуйста, выберите значение")
                    return
            else:
                messagebox.showwarning("Ошибка", "Пожалуйста, выберите значение")
                return

        else:
            # Для шкалы уверенности -5..+5
            confidence = self.confidence_var.get()
            # Преобразуем -5..+5 в 0..1
            confidence = (confidence + 5) / 10.0

        # Обновляем диагностическую систему
        self.diagnostic_engine.update_with_response(symptom, confidence)

        # Добавляем в историю
        self.add_to_history(f"  Ответ: {confidence:.2f}")

        # Задаем следующий вопрос
        self.ask_next_question()

    def skip_question(self):
        """Пропустить текущий вопрос"""
        if self.current_question_data:
            symptom = self.current_question_data["symptom"]
            # Записываем пропуск как нейтральный ответ (0.5)
            self.diagnostic_engine.update_with_response(symptom, 0.5)
            self.add_to_history(f"  Ответ: пропущено (0.50)")
            self.ask_next_question()

    def add_to_history(self, text: str):
        """Добавить запись в историю"""
        self.history_text.config(state='normal')
        self.history_text.insert(tk.END, text + "\n")
        self.history_text.see(tk.END)
        self.history_text.config(state='disabled')

    def update_visualization(self):
        """Обновить визуализацию вероятностей"""
        summary = self.diagnostic_engine.get_diagnosis_summary()
        accepted = summary["accepted_diagnosis"]

        self.visualizer.update_probabilities(summary["probabilities"], accepted)

    def update_status(self):
        """Обновить статусную строку"""
        summary = self.diagnostic_engine.get_diagnosis_summary()
        accepted = summary["accepted_diagnosis"]
        questions_asked = summary["questions_asked"]
        max_questions = self.diagnostic_engine.max_questions

        if accepted:
            prob = summary["probabilities"][accepted]
            self.status_label.config(text=f"Предварительный диагноз: {accepted} ({prob:.2%})")
        else:
            active = len(summary["active_diseases"])
            self.status_label.config(text=f"Рассматривается {active} заболеваний")

        self.progress_label.config(text=f"Вопросов: {questions_asked}/{max_questions}")

        # Обновляем информацию о заболеваниях
        self.update_disease_info()

    def update_disease_info(self):
        """Обновить информацию о заболеваниях"""
        summary = self.diagnostic_engine.get_diagnosis_summary()
        active_diseases = summary["active_diseases"][:3]  # Топ-3

        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)

        if active_diseases:
            self.info_text.insert(tk.END, "ТОП-3 ВОЗМОЖНЫХ ДИАГНОЗОВ:\n")
            self.info_text.insert(tk.END, "=" * 40 + "\n\n")

            for disease in active_diseases:
                prob = summary["probabilities"][disease]
                disease_info = DISEASES_DATABASE.get(disease, {})

                self.info_text.insert(tk.END, f"{disease}:\n")
                self.info_text.insert(tk.END, f"  Вероятность: {prob:.2%}\n")
                self.info_text.insert(tk.END, f"  Описание: {disease_info.get('description', '')}\n")
                self.info_text.insert(tk.END, f"  Тяжесть: {disease_info.get('severity', 0)}/10\n\n")
        else:
            self.info_text.insert(tk.END, "Нет активных диагнозов\n")

        self.info_text.config(state='disabled')

    def show_diagnosis_results(self):
        """Показать результаты диагностики"""
        summary = self.diagnostic_engine.get_diagnosis_summary()
        accepted = summary["accepted_diagnosis"]

        # Обновляем визуализацию
        self.update_visualization()

        # Показываем результаты в отдельном окне
        result_window = tk.Toplevel(self.root)
        result_window.title("Результаты диагностики")
        result_window.geometry("900x700")

        # Центрируем окно
        result_window.transient(self.root)
        result_window.grab_set()

        # Содержимое окна результатов
        main_frame = ttk.Frame(result_window, padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        if accepted == "Здоров":
            title_text = "✓ ВЫ ЗДОРОВЫ"
            color = "green"
            ttk.Label(main_frame, text=title_text,
                     font=('Arial', 16, 'bold'), foreground=color).pack(pady=(0, 15))

            info_frame = ttk.LabelFrame(main_frame, text="Комментарий", padding="15")
            info_frame.pack(fill=tk.X, pady=(0, 15))
            ttk.Label(info_frame, text="По вашим ответам характерных симптомов не выявлено. Вероятные заболевания исключены.",
                     wraplength=800, justify=tk.LEFT).pack(anchor=tk.W, pady=5)
            ttk.Label(info_frame, text="Если самочувствие ухудшится или появятся новые симптомы, повторите опрос или обратитесь к врачу.",
                     wraplength=800, justify=tk.LEFT).pack(anchor=tk.W, pady=5)

        elif accepted:
            disease_info = DISEASES_DATABASE.get(accepted, {})
            prob = summary["probabilities"][accepted]

            if prob >= 0.85:
                title_text = f"✓ ДИАГНОЗ УСТАНОВЛЕН: {accepted}"
                color = "green"
            elif prob >= 0.7:
                title_text = f"⚠ ВЕРОЯТНЫЙ ДИАГНОЗ: {accepted}"
                color = "orange"
            else:
                title_text = f"? ПРЕДПОЛОЖИТЕЛЬНЫЙ ДИАГНОЗ: {accepted}"
                color = "blue"

            ttk.Label(main_frame, text=title_text,
                     font=('Arial', 16, 'bold'), foreground=color).pack(pady=(0, 15))

            # Информация о диагнозе
            info_frame = ttk.LabelFrame(main_frame, text="Информация о диагнозе", padding="15")
            info_frame.pack(fill=tk.X, pady=(0, 15))

            ttk.Label(info_frame, text=f"Описание: {disease_info.get('description', '')}",
                     wraplength=800, justify=tk.LEFT).pack(anchor=tk.W, pady=5)
            ttk.Label(info_frame, text=f"Вероятность: {prob:.2%}",
                     font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)
            ttk.Label(info_frame, text=f"Тяжесть заболевания: {disease_info.get('severity', 0)}/10",
                     foreground='red' if disease_info.get('severity', 0) >= 7 else 'orange').pack(anchor=tk.W, pady=5)

            # Рекомендации
            rec_frame = ttk.LabelFrame(main_frame, text="Рекомендации", padding="15")
            rec_frame.pack(fill=tk.X, pady=(0, 15))

            severity = disease_info.get('severity', 0)
            if severity >= 8:
                recommendation = "🚨 НЕМЕДЛЕННО ОБРАТИТЕСЬ К ВРАЧУ! Это может быть серьезное заболевание, требующее срочного лечения."
            elif severity >= 5:
                recommendation = "⚠ Рекомендуется обратиться к врачу в ближайшие 1-2 дня для подтверждения диагноза и назначения лечения."
            elif severity >= 3:
                recommendation = "ℹ Можете начать с домашнего лечения, но при ухудшении состояния обратитесь к врачу."
            else:
                recommendation = "✅ Легкое заболевание. Можно лечиться дома, соблюдая рекомендации по режиму и симптоматическому лечению."

            ttk.Label(rec_frame, text=recommendation, wraplength=800,
                     justify=tk.LEFT, foreground='red' if severity >= 8 else 'orange' if severity >= 5 else 'black').pack(anchor=tk.W, pady=5)

        else:
            # Нет уверенного диагноза — показываем самый вероятный на текущий момент
            probs = summary["probabilities"] or {}
            if probs:
                # Исключаем «Здоров» из кандидатов, чтобы подсказать именно заболевание
                candidates = {k: v for k, v in probs.items() if k != "Здоров"}
                # Если после исключения пусто — вернем «Здоров» как подсказку состояния
                if not candidates:
                    candidates = probs
                top_disease = max(candidates, key=candidates.get)
                top_prob = candidates[top_disease]

                title_text = "Наиболее вероятный диагноз (уточняется)"
                ttk.Label(main_frame, text=title_text,
                         font=('Arial', 16, 'bold'), foreground='blue').pack(pady=(0, 15))

                info_frame = ttk.LabelFrame(main_frame, text="Предположительный диагноз", padding="15")
                info_frame.pack(fill=tk.X, pady=(0, 15))

                disease_info = DISEASES_DATABASE.get(top_disease, {})
                ttk.Label(info_frame, text=f"{top_disease}", font=('Arial', 13, 'bold')).pack(anchor=tk.W)
                ttk.Label(info_frame, text=f"Текущая вероятность: {top_prob:.2%}",
                         font=('Arial', 12)).pack(anchor=tk.W, pady=4)
                if disease_info:
                    ttk.Label(info_frame, text=f"Описание: {disease_info.get('description', '')}",
                             wraplength=800, justify=tk.LEFT).pack(anchor=tk.W, pady=4)

                # Подсказка пользователю, что система может задать дополнительные вопросы, если лимит будет расширен
                hint_text = (
                    "Система продолжит задавать уточняющие вопросы при необходимости,"
                    " чтобы повысить уверенность в диагнозе."
                )
                ttk.Label(main_frame, text=hint_text, wraplength=800, justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 10))
            else:
                ttk.Label(main_frame, text="Диагноз не установлен",
                         font=('Arial', 16, 'bold'), foreground='blue').pack(pady=(0, 15))

        # Статистика диагностики
        stat_frame = ttk.LabelFrame(main_frame, text="Статистика диагностики", padding="15")
        stat_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(stat_frame, text=f"Задано вопросов: {summary['questions_asked']}").pack(anchor=tk.W, pady=2)
        ttk.Label(stat_frame, text=f"Рассмотрено заболеваний: {summary['total_diseases']}").pack(anchor=tk.W, pady=2)
        ttk.Label(stat_frame, text=f"Активных заболеваний: {len(summary['active_diseases'])}").pack(anchor=tk.W, pady=2)

        # Другие возможные диагнозы
        if len(summary['active_diseases']) > 1:
            other_frame = ttk.LabelFrame(main_frame, text="Другие возможные диагнозы", padding="15")
            other_frame.pack(fill=tk.X, pady=(0, 15))

            for i, disease in enumerate(summary['active_diseases'][:4], 1):
                if disease != accepted:
                    prob = summary["probabilities"][disease]
                    ttk.Label(other_frame, text=f"{i}. {disease}: {prob:.2%}").pack(anchor=tk.W, pady=2)

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Сохранить результаты",
                  command=lambda: self.save_results_from_window(result_window)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Новая диагностика",
                  command=lambda: [result_window.destroy(), self.start_new_diagnosis()]).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Закрыть",
                  command=result_window.destroy).pack(side=tk.LEFT, padx=5)

    def save_results(self):
        """Сохранить результаты диагностики"""
        summary = self.diagnostic_engine.get_diagnosis_summary()

        # Сохраняем в файл
        filepath = self.results_logger.log_diagnosis(summary)

        # Показываем сообщение
        messagebox.showinfo("Результаты сохранены",
                           f"Результаты диагностики сохранены в файл:\n{filepath}")

    def save_results_from_window(self, window):
        """Сохранить результаты из окна результатов"""
        self.save_results()
        window.destroy()

    def show_history(self):
        """Показать историю предыдущих диагностик"""
        logs = self.results_logger.load_recent_logs(10)

        history_window = tk.Toplevel(self.root)
        history_window.title("История диагностик")
        history_window.geometry("700x500")

        main_frame = ttk.Frame(history_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="История последних диагностик",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Создаем Treeview для отображения истории
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(tree_frame, columns=('date', 'diagnosis', 'probability', 'questions'),
                           show='headings', height=15)

        tree.heading('date', text='Дата и время')
        tree.heading('diagnosis', text='Диагноз')
        tree.heading('probability', text='Вероятность')
        tree.heading('questions', text='Вопросов')

        tree.column('date', width=180)
        tree.column('diagnosis', width=180)
        tree.column('probability', width=100)
        tree.column('questions', width=80)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)

        # Заполняем данными
        for log in logs:
            diagnosis = log.get('accepted_diagnosis', 'Не установлен')
            questions = log.get('questions_asked', 0)
            date = log.get('datetime', '').replace('T', ' ')[:19]

            if diagnosis != 'Не установлен':
                prob = log.get('probabilities', {}).get(diagnosis, 0)
                probability = f"{prob:.1%}"
            else:
                probability = "-"

            tree.insert('', tk.END, values=(date, diagnosis, probability, questions))

        # Кнопка закрытия
        ttk.Button(main_frame, text="Закрыть",
                  command=history_window.destroy).pack(pady=10)

    def show_help(self):
        """Показать справку"""
        help_text = """
        РУКОВОДСТВО ПО ИСПОЛЬЗОВАНИЮ:

        1. Система задаст 10-25 вопросов для точной диагностики
        2. Отвечайте честно на все вопросы
        3. Если не знаете ответ - используйте средние значения или пропустите вопрос
        4. Типы вопросов:
           • Бинарные: да/нет с вариантами
           • Шкала: от 1 (нет) до 10 (максимально)
           • Диапазон: выбор из нескольких вариантов
        5. Система автоматически остановится при установлении диагноза
        6. Результаты можно сохранить для истории

        Точность системы зависит от:
        • Количества и качества ответов
        • Четкости описания симптомов
        • Правильности выбора вариантов ответа

        ВНИМАНИЕ: Эта система не заменяет консультацию врача!
        Все диагнозы носят предварительный характер.
        """

        messagebox.showinfo("Справка", help_text)

    def run(self):
        """Запустить GUI"""
        self.root.mainloop()