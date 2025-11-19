import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Callable, Optional


class ProbabilityTableView:
    def __init__(self, parent, title: str, first_col_title: str, first_width: int = 160):
        self.frame = ttk.Labelframe(parent, text=title)
        self.table = ttk.Treeview(self.frame, columns=("name", "prob"), show="headings", height=8, style="Prob.Treeview")
        self.table.heading("name", text=first_col_title)
        self.table.heading("prob", text="P, %")
        self.table.column("name", width=first_width, anchor=tk.W)
        self.table.column("prob", width=96, anchor=tk.E)
        self.table.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self._dblclick_callback = None

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def clear(self):
        for item in self.table.get_children():
            self.table.delete(item)

    def update_data(self, series):
        self.clear()
        if series is None:
            return
        data = series.sort_values(ascending=False)
        eps = 1e-9  # бесконечно малая для отображения
        for name, p in data.items():
            p_float = float(p)
            p_disp = p_float if p_float > 0 else eps
            percent = p_disp * 100.0
            iid = self.table.insert("", tk.END, values=(name, f"{percent:.2f}%"))
            _colorize_row(self.table, iid, p_disp)

    def bind_on_double_click(self, callback):
        """Привязать обработчик двойного щелчка по строке таблицы."""
        self._dblclick_callback = callback
        try:
            self.table.bind("<Double-1>", lambda e: self._on_dbl_click(), add="+")
        except Exception:
            pass

    def _on_dbl_click(self):
        if not self._dblclick_callback:
            return
        name = self.get_selected_name()
        if name:
            try:
                self._dblclick_callback(name)
            except Exception:
                pass

    def get_selected_name(self) -> Optional[str]:
        try:
            sel = self.table.selection()
            if not sel:
                return None
            vals = self.table.item(sel[0], "values")
            return vals[0] if vals else None
        except Exception:
            return None


class QuestionView:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, padding=12)
        # Отдельные области, которые могут пересоздаваться (после финального экрана)
        self.question_area = ttk.Frame(self.frame)
        self.question_area.pack(fill=tk.X, anchor=tk.N, pady=(0, 6))
        self.answers_area = ttk.Frame(self.frame)
        self.answers_area.pack(fill=tk.X, anchor=tk.N)
        self.nav_area = ttk.Frame(self.frame)
        self.nav_area.pack(fill=tk.X, anchor=tk.N, pady=(8, 0))
        self._answer_var = tk.StringVar(value="")

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def render_question(self, text: str, options: list[str], on_next: Callable[[str], None], on_skip: Optional[Callable[[], None]] = None):
        # Убедиться, что области существуют (могли быть уничтожены на финальном экране)
        self._ensure_areas()
        # очистить содержимое областей
        for c in list(self.question_area.winfo_children()):
            c.destroy()
        for c in list(self.answers_area.winfo_children()):
            c.destroy()
        for c in list(self.nav_area.winfo_children()):
            c.destroy()

        ttk.Label(self.question_area, text=text, style="Question.TLabel").pack(anchor=tk.W, pady=(0, 8))
        self._answer_var.set("")
        for ans in options:
            ttk.Radiobutton(self.answers_area, text=ans, value=ans, variable=self._answer_var).pack(anchor=tk.W)

        def _next():
            val = self._answer_var.get()
            if not val:
                ttk.Label(self.nav_area, text="Пожалуйста, выберите вариант ответа.", style="Warn.TLabel").pack(anchor=tk.W, pady=(6, 0))
                return
            on_next(val)

        nav_buttons = ttk.Frame(self.nav_area)
        nav_buttons.pack(fill=tk.X, anchor=tk.W)

        btn_next = ttk.Button(nav_buttons, text="Следующий вопрос", command=_next)
        btn_next.pack(side=tk.LEFT)
        _attach_tooltip(btn_next, "Перейти к следующему вопросу, применив выбранный ответ.")

        if on_skip is not None:
            def _skip():
                try:
                    on_skip()
                except Exception:
                    pass
            btn_skip = ttk.Button(nav_buttons, text="Пропустить", command=_skip)
            btn_skip.pack(side=tk.LEFT, padx=(8, 0))
            _attach_tooltip(btn_skip, "Пропустить этот вопрос без влияния на вероятности.")

    def _ensure_areas(self):
        try:
            # Если какая-либо область была уничтожена, пересоздать её
            if not self._widget_exists(self.question_area):
                self.question_area = ttk.Frame(self.frame)
                self.question_area.pack(fill=tk.X, anchor=tk.N, pady=(0, 6))
            if not self._widget_exists(self.answers_area):
                self.answers_area = ttk.Frame(self.frame)
                self.answers_area.pack(fill=tk.X, anchor=tk.N)
            if not self._widget_exists(self.nav_area):
                self.nav_area = ttk.Frame(self.frame)
                self.nav_area.pack(fill=tk.X, anchor=tk.N, pady=(8, 0))
        except Exception:
            # В крайнем случае перестроим всё заново
            for child in list(self.frame.winfo_children()):
                try:
                    child.destroy()
                except Exception:
                    pass
            self.question_area = ttk.Frame(self.frame)
            self.question_area.pack(fill=tk.X, anchor=tk.N, pady=(0, 6))
            self.answers_area = ttk.Frame(self.frame)
            self.answers_area.pack(fill=tk.X, anchor=tk.N)
            self.nav_area = ttk.Frame(self.frame)
            self.nav_area.pack(fill=tk.X, anchor=tk.N, pady=(8, 0))

    @staticmethod
    def _widget_exists(widget) -> bool:
        try:
            return bool(widget) and int(widget.winfo_exists()) == 1
        except Exception:
            return False


class MainView:
    def __init__(self, root: Optional[tk.Tk] = None):
        self.root = root or tk.Tk()
        self.root.title("Байесовская система рекомендаций книг")
        _setup_styles(self.root)

        # Меню (обработчики устанавливает контроллер)
        menubar = tk.Menu(self.root)
        self.file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=self.file_menu)
        self.root.config(menu=menubar)

        # Заголовок
        ttk.Label(self.root, text="Система рекомендаций книг (Байес)", style="Title.TLabel").pack(pady=(12, 6))

        # Прогресс
        progress_container = ttk.Frame(self.root)
        progress_container.pack(fill=tk.X, padx=12, pady=(0, 10))
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress = ttk.Progressbar(progress_container, variable=self.progress_var, maximum=100)
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress_label = ttk.Label(progress_container, text="0/0", style="Small.TLabel")
        self.progress_label.pack(side=tk.LEFT, padx=(8, 0))
        _attach_tooltip(self.progress, "Прогресс прохождения опроса. Отвечайте на вопросы, чтобы получить рекомендации.")

        # Основной лейаут
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.question_view = QuestionView(main_frame)
        self.question_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = ttk.Frame(main_frame, padding=(12, 12, 12, 12))
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        self.genre_table = ProbabilityTableView(right, "Вероятности жанров", "Жанр", 140)
        self.subgenre_table = ProbabilityTableView(right, "Вероятности поджанров", "Поджанр", 160)
        self.book_table = ProbabilityTableView(right, "Вероятности книг", "Книга", 200)

        # По умолчанию таблицы скрыты — будут показаны по мере прохождения уровней
        # (см. методы show_*)

        self._final_buttons = None

    # ---- управление видимостью таблиц ----
    def hide_all_tables(self):
        try:
            self.genre_table.frame.pack_forget()
            self.subgenre_table.frame.pack_forget()
            self.book_table.frame.pack_forget()
        except Exception:
            pass

    def show_genre_table(self):
        # показывается после завершения уровня 1
        try:
            self.genre_table.pack(fill=tk.BOTH, expand=True)
        except Exception:
            pass

    def show_subgenre_table(self):
        # показывается после завершения уровня 2
        try:
            # убедимся, что жанровая тоже показана (безопасно вызывать повторно)
            self.show_genre_table()
            self.subgenre_table.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        except Exception:
            pass

    def show_book_table(self):
        # показывается после завершения уровня 3 (финал)
        try:
            self.show_subgenre_table()
            self.book_table.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        except Exception:
            pass

    # Утилита для получения выбранной в таблице книги
    def get_selected_book(self) -> Optional[str]:
        return self.book_table.get_selected_name()

    # ---- меню ----
    def set_menu_handlers(self, on_open_json: Callable[[], None], on_open_csv: Callable[[], None], on_exit: Callable[[], None]):
        fm = self.file_menu
        fm.delete(0, tk.END)
        fm.add_command(label="Загрузить JSON…", command=on_open_json)
        fm.add_command(label="Загрузить CSV книги…", command=on_open_csv)
        fm.add_separator()
        fm.add_command(label="Выход", command=on_exit)

    # ---- прогресс ----
    def update_progress(self, done: int, total: int):
        pct = (done / total) * 100 if total else 0
        self.progress_var.set(pct)
        self.progress_label.config(text=f"{done}/{total}")

    # ---- таблицы ----
    def update_genre(self, series):
        self.genre_table.update_data(series)

    def update_subgenre(self, series):
        self.subgenre_table.update_data(series)

    def update_book(self, series):
        self.book_table.update_data(series)

    # ---- финальный экран ----
    def render_final(self, top_books_series, book_details: Optional[dict] = None):
        # Полная очистка области вопросов и отрисовка итогов
        for child in list(self.question_view.frame.winfo_children()):
            try:
                child.destroy()
            except Exception:
                pass
        ttk.Label(self.question_view.frame, text="Результаты и рекомендации", font=("Segoe UI", 14, "bold")).pack(anchor=tk.W, pady=(0, 8))
        ttk.Label(self.question_view.frame, text="Топ-3 рекомендации:", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=(4, 6))
        eps = 1e-9
        for title, p in top_books_series.items():
            if book_details and title in book_details:
                info = book_details.get(title) or {}
                author = info.get("author", "?")
                genre = info.get("genre", "?")
                subg = info.get("subgenre", "?")
                p_disp = float(p) if float(p) > 0 else eps
                text = f"• {title} — {author}  |  {genre} → {subg}  |  {p_disp*100:.2f}%"
            else:
                p_disp = float(p) if float(p) > 0 else eps
                text = f"• {title} — {p_disp*100:.2f}%"
            ttk.Label(self.question_view.frame, text=text).pack(anchor=tk.W)

        btns = ttk.Frame(self.question_view.frame)
        btns.pack(anchor=tk.W, pady=(12, 0))
        self._final_buttons = btns
        return btns  # контроллер навесит команды


# ----- стили/утилиты (UI-only) -----
def _setup_styles(root):
    try:
        style = ttk.Style()
        style.theme_use('clam')
        root.option_add("*Font", "{Segoe UI} 11")
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Question.TLabel", font=("Segoe UI", 13, "bold"))
        style.configure("Small.TLabel", font=("Segoe UI", 10))
        style.configure("Warn.TLabel", foreground="#b00020")
        style.configure("Prob.Treeview", rowheight=22)
        style.configure("TLabelframe.Label", font=("Segoe UI", 12, "bold"))
    except Exception:
        pass


def _prob_to_hex(p: float) -> str:
    p = max(0.0, min(1.0, float(p)))
    r1, g1, b1 = 231, 76, 60
    r2, g2, b2 = 46, 204, 113
    r = int(r1 + (r2 - r1) * p)
    g = int(g1 + (g2 - g1) * p)
    b = int(b1 + (b2 - b1) * p)
    return f"#{r:02x}{g:02x}{b:02x}"


def _colorize_row(tree: ttk.Treeview, iid: str, p: float):
    try:
        color = _prob_to_hex(float(p))
        tag_name = f"bg_{color}"
        existing = getattr(tree, "_existing_tags", set())
        if tag_name not in existing:
            tree.tag_configure(tag_name, background=color)
            existing.add(tag_name)
            tree._existing_tags = existing
        tree.item(iid, tags=(tag_name,))
    except Exception:
        pass


def _attach_tooltip(widget, text: str):
    Tooltip(widget, text)


class Tooltip:
    def __init__(self, widget, text: str, delay_ms: int = 400):
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self._tipwindow = None
        self._after_id = None
        try:
            widget.bind("<Enter>", self._on_enter, add="+")
            widget.bind("<Leave>", self._on_leave, add="+")
            widget.bind("<ButtonPress>", self._on_leave, add="+")
        except Exception:
            pass

    def _on_enter(self, _=None):
        self._unschedule()
        self._after_id = self.widget.after(self.delay_ms, self._show)

    def _on_leave(self, _=None):
        self._unschedule()
        self._hide()

    def _unschedule(self):
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show(self):
        if self._tipwindow or not self.text:
            return
        try:
            x = self.widget.winfo_rootx() + 10
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        except Exception:
            x, y = 0, 0
        tw = tk.Toplevel(self.widget)
        self._tipwindow = tw
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(tw, text=self.text, justify=tk.LEFT, relief=tk.SOLID, borderwidth=1, background="#ffffe0")
        label.pack(ipadx=6, ipady=3)

    def _hide(self):
        tw = self._tipwindow
        if tw:
            try:
                tw.destroy()
            except Exception:
                pass
            self._tipwindow = None
