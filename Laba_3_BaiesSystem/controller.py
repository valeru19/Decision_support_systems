import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import logging
from typing import Optional

from model import BayesianProbabilityModel
from view import MainView


class AppController:
    """
    Контроллер связывает модель и представление, управляет потоком вопросов
    и обновлением таблиц вероятностей.
    """

    def __init__(self, model: BayesianProbabilityModel, view: MainView):
        self.model = model
        self.view = view

        # Индексы уровней
        self.l1_index = 0
        self.l2_index = 0
        self.l3_index = 0
        # Счётчик прогресса (отвеченные + пропущенные)
        self.answered_count = 0

        # Меню
        self.view.set_menu_handlers(self._on_open_json, self._on_open_csv, self._on_exit)

        # По новым требованиям: все таблицы показаны сразу
        try:
            self.view.show_book_table()  # покажет также жанры и поджанры
        except Exception:
            pass

        # Выбор книги пользователем (по двойному клику в таблице книг)
        try:
            self.view.book_table.bind_on_double_click(self._on_select_book)
        except Exception:
            pass

        self._chosen_book: Optional[str] = None

        # Первичная отрисовка
        self._render_current_level1_question()
        # первичное обновление таблиц
        self._refresh_tables()
        self._update_progress()

    # -------- меню --------
    def _on_open_json(self):
        path = filedialog.askopenfilename(title="Загрузить JSON", filetypes=(("JSON файлы", "*.json"), ("Все файлы", "*.*")))
        if not path:
            return
        try:
            self.model.load_from_json(path)
            # сброс состояния вопросов
            self.model.user_answers = []
            self.l1_index = self.l2_index = self.l3_index = 0
            self.answered_count = 0
            # Показать все таблицы сразу
            try:
                self.view.show_book_table()
            except Exception:
                pass
            self._render_current_level1_question()
            self._refresh_tables()
            self._update_progress()
            messagebox.showinfo("Загрузка данных", "JSON данные успешно загружены")
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить JSON: {e}")

    def _on_open_csv(self):
        path = filedialog.askopenfilename(title="Загрузить CSV книги", filetypes=(("CSV файлы", "*.csv"), ("Все файлы", "*.*")))
        if not path:
            return
        try:
            self.model.load_books_from_csv(path)
            self.model.user_answers = []
            self.l1_index = self.l2_index = self.l3_index = 0
            self.answered_count = 0
            try:
                self.view.show_book_table()
            except Exception:
                pass
            self._render_current_level1_question()
            self._refresh_tables()
            self._update_progress()
            messagebox.showinfo("Загрузка данных", "Список книг из CSV успешно загружен")
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить CSV: {e}")

    def _on_exit(self):
        try:
            self.view.root.destroy()
        except Exception:
            pass

    # -------- отрисовка вопросов --------
    def _render_current_level1_question(self):
        if self.l1_index >= len(self.model.questions_level_1):
            self._render_current_level2_question()
            return
        q = self.model.questions_level_1[self.l1_index]
        self.view.question_view.render_question(q["question"], q["answers"], self._on_level1_next, on_skip=self._on_level1_skip)
        self._update_progress()

    def _on_level1_next(self, answer: str):
        self.model.user_answers.append(answer)
        self.model.user_answer_levels.append(1)
        logging.info("L1: выбран ответ: %s (q=%d)", answer, self.l1_index)
        self.model.update_with_answer_weighted(answer, 1)
        self._refresh_tables()
        self.answered_count += 1
        self.l1_index += 1
        self._render_current_level1_question()

    def _on_level1_skip(self):
        logging.info("L1: вопрос пропущен (q=%d)", self.l1_index)
        # Ничего не добавляем в ответы, просто двигаемся дальше
        self.answered_count += 1
        self._refresh_tables()
        self.l1_index += 1
        self._render_current_level1_question()

    def _render_current_level2_question(self):
        if self.l2_index >= len(self.model.questions_level_2):
            self._render_current_level3_question()
            return
        q = self.model.questions_level_2[self.l2_index]
        self.view.question_view.render_question(q["question"], q["answers"], self._on_level2_next, on_skip=self._on_level2_skip)
        # Таблицы показаны сразу; просто обновим данные
        if self.l2_index == 0:
            self._refresh_tables()
        self._update_progress()

    def _on_level2_next(self, answer: str):
        self.model.user_answers.append(answer)
        self.model.user_answer_levels.append(2)
        logging.info("L2: выбран ответ: %s (q=%d)", answer, self.l2_index)
        self.model.update_with_answer_weighted(answer, 2)
        self._refresh_tables()
        self.answered_count += 1
        self.l2_index += 1
        self._render_current_level2_question()

    def _on_level2_skip(self):
        logging.info("L2: вопрос пропущен (q=%d)", self.l2_index)
        self.answered_count += 1
        self._refresh_tables()
        self.l2_index += 1
        self._render_current_level2_question()

    def _render_current_level3_question(self):
        if self.l3_index >= len(self.model.questions_level_3):
            self._render_final_screen()
            return
        q = self.model.questions_level_3[self.l3_index]
        self.view.question_view.render_question(q["question"], q["answers"], self._on_level3_next, on_skip=self._on_level3_skip)
        if self.l3_index == 0:
            self._refresh_tables()
        self._update_progress()

    def _on_level3_next(self, answer: str):
        self.model.user_answers.append(answer)
        self.model.user_answer_levels.append(3)
        logging.info("L3: выбран ответ: %s (q=%d)", answer, self.l3_index)
        self.model.update_with_answer_weighted(answer, 3)
        self._refresh_tables()
        self.answered_count += 1
        self.l3_index += 1
        self._render_current_level3_question()

    def _on_level3_skip(self):
        logging.info("L3: вопрос пропущен (q=%d)", self.l3_index)
        self.answered_count += 1
        self._refresh_tables()
        self.l3_index += 1
        self._render_current_level3_question()

    # -------- финальный экран --------
    def _render_final_screen(self):
        # Показать все таблицы и обновить данные
        try:
            self.view.show_book_table()
        except Exception:
            pass
        self._refresh_tables()
        top_books = self.model.prior_book.sort_values(ascending=False).head(3)
        # подготовим подробности по книгам для вывода (автор/жанр/поджанр)
        details = {b.get("title"): {"author": b.get("author"), "genre": b.get("genre"), "subgenre": b.get("subgenre")} for b in self.model.books}
        btns = self.view.render_final(top_books, book_details=details)
        # Кнопка выбора книги из таблицы
        choose_btn = ttk.Button(btns, text="Выбрать книгу", command=self._on_choose_button)
        choose_btn.pack(side=tk.LEFT, padx=(0, 8))
        restart_btn = ttk.Button(btns, text="Начать заново", command=self._reset_and_restart)
        restart_btn.pack(side=tk.LEFT)
        exit_btn = ttk.Button(btns, text="Выход", command=self._on_exit)
        exit_btn.pack(side=tk.LEFT, padx=(8, 0))

    def _reset_and_restart(self):
        self.model.user_answers = []
        self.model.user_answer_levels = []
        self.model.initialize_priors()
        self.l1_index = self.l2_index = self.l3_index = 0
        self.answered_count = 0
        try:
            self.view.show_book_table()
        except Exception:
            pass
        self._refresh_tables()
        self._render_current_level1_question()
        self._update_progress()
        logging.info("Опрос перезапущен пользователем")

    # -------- выбор книги --------
    def _on_select_book(self, title: str):
        self._chosen_book = title
        logging.info("Пользователь выбрал книгу (двойной клик): %s", title)
        try:
            messagebox.showinfo("Выбор книги", f"Вы выбрали: {title}")
        except Exception:
            pass

    def _on_choose_button(self):
        title = self.view.get_selected_book()
        if not title:
            try:
                messagebox.showwarning("Выбор книги", "Пожалуйста, выделите книгу в таблице рекомендаций.")
            except Exception:
                pass
            return
        self._on_select_book(title)

    # -------- утилиты --------
    def _refresh_tables(self, *, genre_only: bool = False):
        if genre_only:
            self.view.update_genre(self.model.prior_genre)
        else:
            self.view.update_genre(self.model.prior_genre)
            self.view.update_subgenre(self.model.prior_subgenre)
            self.view.update_book(self.model.prior_book)

    def _update_progress(self):
        total = len(self.model.questions_level_1) + len(self.model.questions_level_2) + len(self.model.questions_level_3)
        done = self.answered_count
        self.view.update_progress(done, total)
