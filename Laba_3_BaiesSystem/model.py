from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
import pandas as pd
import numpy as np
import json
import logging
from copy import deepcopy

# База знаний по умолчанию вынесена отдельно
from knowledge_base import (
    DEFAULT_BOOKS,
    DEFAULT_GENRE_HIERARCHY,
    DEFAULT_QUESTIONS_L1,
    DEFAULT_QUESTIONS_L2,
    DEFAULT_QUESTIONS_L3,
    DEFAULT_PR_ANSWER_TO_GENRE,
    DEFAULT_PR_ANSWER_TO_SUBGENRE,
    DEFAULT_PR_ANSWER_TO_BOOK,
)


@dataclass
class BookModel:
    title: str
    author: str
    genre: str
    subgenre: str


@dataclass
class Question:
    level: int
    text: str
    options: List[str]


class BayesianProbabilityModel:
    """
    Бизнес-логика: хранение данных, априоры, правдоподобия, байесовские обновления,
    загрузка данных. Не содержит UI-кода.
    """

    def __init__(self, *, enable_logging: bool = True):
        if enable_logging:
            self._setup_logging()

        # Книги (список словарей для совместимости с существующими данными)
        self.books: List[Dict[str, str]] = deepcopy(DEFAULT_BOOKS)

        # Иерархия жанров -> поджанров
        self.genre_hierarchy: Dict[str, List[str]] = deepcopy(DEFAULT_GENRE_HIERARCHY)

        # Вопросы (храним в исходном виде для совместимости)
        self.questions_level_1: List[Dict[str, Any]] = deepcopy(DEFAULT_QUESTIONS_L1)
        self.questions_level_2: List[Dict[str, Any]] = deepcopy(DEFAULT_QUESTIONS_L2)
        self.questions_level_3: List[Dict[str, Any]] = deepcopy(DEFAULT_QUESTIONS_L3)

        # Вероятности (ответ -> сущность)
        self.pr_answer_to_genre: Dict[str, Dict[str, float]] = deepcopy(DEFAULT_PR_ANSWER_TO_GENRE)
        self.pr_answer_to_subgenre: Dict[str, Dict[str, float]] = deepcopy(DEFAULT_PR_ANSWER_TO_SUBGENRE)
        self.pr_answer_to_book: Dict[str, Dict[str, float]] = deepcopy(DEFAULT_PR_ANSWER_TO_BOOK)

        # Ответы пользователя
        self.user_answers: List[str] = []
        # Уровни для каждого ответа (1,2,3) — используются для взвешенных обновлений
        self.user_answer_levels: List[int] = []

        # Подготовка множеств, априоров и матриц правдоподобия
        self._rebuild_indexes_and_priors()
        self._build_likelihood_matrices()

        # Кэш столбцов правдоподобия для скорости
        self._genre_col_cache: Dict[str, pd.Series] = {col: self.genre_likelihoods[col].copy() for col in self.genre_likelihoods.columns}
        self._subgenre_col_cache: Dict[str, pd.Series] = {col: self.subgenre_likelihoods[col].copy() for col in self.subgenre_likelihoods.columns}
        self._book_col_cache: Dict[str, pd.Series] = {col: self.book_likelihoods[col].copy() for col in self.book_likelihoods.columns}

        # Веса влияния уровней вопросов на разные иерархии (нелинейность через экспоненты)
        # Чем больше альфа, тем сильнее влияние ответа на соответствующее распределение
        self.level_weights = {
            1: {"genre": 2.2, "subgenre": 3.3, "book": 4.15},
            2: {"genre": 1.3, "subgenre": 2.1, "book": 3.35},
            3: {"genre": 1.05, "subgenre": 1.15, "book": 2.2},
        }
        # Небольшое сглаживание, чтобы вероятность не занулялась и всегда была хотя бы минимальной
        self.smoothing_tau: float = 0.02

    # --------- Инициализация ---------
    def _rebuild_indexes_and_priors(self):
        self.genres = list(self.genre_hierarchy.keys())
        subgenres_set = set()
        for subs in self.genre_hierarchy.values():
            subgenres_set.update(subs)
        for b in self.books:
            subgenres_set.add(b.get("subgenre"))
        self.subgenres = sorted([s for s in subgenres_set if s])
        # Список названий книг и объекты BookModel для удобной интеграции
        self.book_titles = [b.get("title") for b in self.books if b.get("title")]
        # Построим объекты и быстрые индексы
        self.book_models: List[BookModel] = []
        self.title_to_book: Dict[str, BookModel] = {}
        for b in self.books:
            try:
                bm = BookModel(
                    title=str(b.get("title") or ""),
                    author=str(b.get("author") or ""),
                    genre=str(b.get("genre") or ""),
                    subgenre=str(b.get("subgenre") or ""),
                )
            except Exception:
                # На всякий случай игнорируем битые записи
                continue
            if not bm.title:
                continue
            self.book_models.append(bm)
            self.title_to_book[bm.title] = bm

        # Быстрые связи для индукции правдоподобий
        self.subgenre_to_genre: Dict[str, Optional[str]] = {}
        for g, subs in self.genre_hierarchy.items():
            for sg in subs:
                self.subgenre_to_genre[sg] = g
        # Списки книг по жанру и поджанру
        self.genre_to_books: Dict[str, List[str]] = {g: [] for g in self.genres}
        self.subgenre_to_books: Dict[str, List[str]] = {sg: [] for sg in self.subgenres}
        for b in self.books:
            title = b.get("title")
            g = b.get("genre")
            sg = b.get("subgenre")
            if title and g in self.genre_to_books:
                self.genre_to_books[g].append(title)
            if title and sg in self.subgenre_to_books:
                self.subgenre_to_books[sg].append(title)

        self.prior_genre_initial = pd.Series(1.0 / max(1, len(self.genres)), index=self.genres, dtype=float)
        self.prior_subgenre_initial = pd.Series(1.0 / max(1, len(self.subgenres)), index=self.subgenres, dtype=float)
        self.prior_book_initial = pd.Series(1.0 / max(1, len(self.book_titles)), index=self.book_titles, dtype=float)
        self.initialize_priors()

    def _build_likelihood_matrices(self, epsilon: float = 1e-9):
        genre_answers = list(self.pr_answer_to_genre.keys())
        self.genre_likelihoods = pd.DataFrame(epsilon, index=self.genres, columns=genre_answers, dtype=float)
        for ans, dist in self.pr_answer_to_genre.items():
            for g, p in dist.items():
                if g in self.genre_likelihoods.index:
                    self.genre_likelihoods.at[g, ans] = float(p)

        subgenre_answers = list(self.pr_answer_to_subgenre.keys())
        self.subgenre_likelihoods = pd.DataFrame(epsilon, index=self.subgenres, columns=subgenre_answers, dtype=float)
        for ans, dist in self.pr_answer_to_subgenre.items():
            for sg, p in dist.items():
                if sg in self.subgenre_likelihoods.index:
                    self.subgenre_likelihoods.at[sg, ans] = float(p)

        book_answers = list(self.pr_answer_to_book.keys())
        self.book_likelihoods = pd.DataFrame(epsilon, index=self.book_titles, columns=book_answers, dtype=float)
        for ans, dist in self.pr_answer_to_book.items():
            for title, p in dist.items():
                if title in self.book_likelihoods.index:
                    self.book_likelihoods.at[title, ans] = float(p)

    # --------- Байес ---------
    @staticmethod
    def _normalize_series(s: pd.Series) -> pd.Series:
        s = s.fillna(0.0).astype(float)
        total = s.sum()
        if total > 0:
            return s / total
        n = len(s)
        if n == 0:
            return s
        return pd.Series(1.0 / n, index=s.index, dtype=float)

    def initialize_priors(self) -> None:
        self.prior_genre = self.prior_genre_initial.copy()
        self.prior_subgenre = self.prior_subgenre_initial.copy()
        self.prior_book = self.prior_book_initial.copy()

    def _bayes_update(self, prior: pd.Series, likelihoods: pd.DataFrame, answer: str) -> pd.Series:
        # Попробуем получить столбец правдоподобия. Если его нет — попробуем синтезировать
        induced_like: Optional[pd.Series] = None
        if answer not in likelihoods.columns:
            try:
                if likelihoods is self.subgenre_likelihoods:
                    induced_like = self._induce_subgenre_like(answer, index=prior.index)
                elif likelihoods is self.book_likelihoods:
                    induced_like = self._induce_book_like(answer, index=prior.index)
            except Exception:
                logging.exception("Не удалось синтезировать правдоподобия для ответа '%s'", answer)
            if induced_like is None:
                return prior.copy()
        try:
            if likelihoods is self.genre_likelihoods and answer in self._genre_col_cache:
                like = self._genre_col_cache[answer].reindex(prior.index).fillna(0.0).astype(float)
            elif likelihoods is self.subgenre_likelihoods and answer in self._subgenre_col_cache:
                like = self._subgenre_col_cache[answer].reindex(prior.index).fillna(0.0).astype(float)
            elif likelihoods is self.book_likelihoods and answer in self._book_col_cache:
                like = self._book_col_cache[answer].reindex(prior.index).fillna(0.0).astype(float)
            else:
                if answer in likelihoods.columns:
                    like = likelihoods[answer].reindex(prior.index).fillna(0.0).astype(float)
                else:
                    like = induced_like.reindex(prior.index).fillna(0.0).astype(float) if induced_like is not None else pd.Series(0.0, index=prior.index)
        except Exception as e:
            logging.exception("Ошибка при получении столбца правдоподобия: %s", e)
            like = likelihoods.get(answer, pd.Series(0.0, index=prior.index)).reindex(prior.index).fillna(0.0).astype(float)
        numerator = like * prior
        evidence = numerator.sum()
        if evidence <= 0:
            return self._normalize_series(numerator)
        posterior = numerator / evidence
        return self._normalize_series(posterior)

    def _bayes_update_weighted(self, prior: pd.Series, likelihoods: pd.DataFrame, answer: str, alpha: float) -> pd.Series:
        """Взвешенное (нелинейное) обновление: правдоподобия возводятся в степень alpha
        и применяется сглаживание, чтобы все элементы сохраняли минимальную массу."""
        # Получаем столбец через существующую логику (со всеми индукциями)
        base_posterior = self._bayes_update(prior, likelihoods, answer)
        # Если ответ не дал информации (вернулся prior без изменений) — пытаемся получить like напрямую
        # и применяем веса к правдоподобию
        # Для устойчивости извлечём like похожим способом, что и в _bayes_update
        induced_like: Optional[pd.Series] = None
        if answer not in likelihoods.columns:
            try:
                if likelihoods is self.subgenre_likelihoods:
                    induced_like = self._induce_subgenre_like(answer, index=prior.index)
                elif likelihoods is self.book_likelihoods:
                    induced_like = self._induce_book_like(answer, index=prior.index)
            except Exception:
                induced_like = None
        try:
            if likelihoods is self.genre_likelihoods and answer in self._genre_col_cache:
                like = self._genre_col_cache[answer].reindex(prior.index).fillna(0.0).astype(float)
            elif likelihoods is self.subgenre_likelihoods and answer in self._subgenre_col_cache:
                like = self._subgenre_col_cache[answer].reindex(prior.index).fillna(0.0).astype(float)
            elif likelihoods is self.book_likelihoods and answer in self._book_col_cache:
                like = self._book_col_cache[answer].reindex(prior.index).fillna(0.0).astype(float)
                # Важно: если ответ имеет явный столбец для книг, добавим индуцированный сигнал,
                # чтобы новые книги внутри затронутых жанров/поджанров тоже получали массу.
                try:
                    induced_like = self._induce_book_like(answer, index=prior.index)
                except Exception:
                    induced_like = None
                if induced_like is not None:
                    like = self._normalize_series(like + induced_like)
            else:
                if answer in likelihoods.columns:
                    like = likelihoods[answer].reindex(prior.index).fillna(0.0).astype(float)
                    # Аналогично: для матриц книг добавим индуцированный сигнал
                    if likelihoods is self.book_likelihoods:
                        try:
                            induced_like = self._induce_book_like(answer, index=prior.index)
                        except Exception:
                            induced_like = None
                        if induced_like is not None:
                            like = self._normalize_series(like + induced_like)
                else:
                    like = induced_like if induced_like is not None else pd.Series(1.0, index=prior.index, dtype=float)
        except Exception:
            like = pd.Series(1.0, index=prior.index, dtype=float)

        # Нелинейность: акцентировать влияние ответа
        like = like.clip(lower=1e-12) ** float(max(alpha, 1e-6))
        like = self._normalize_series(like)
        numerator = like * prior
        posterior = self._normalize_series(numerator)
        # Сглаживание: примешиваем небольшую равномерную массу
        tau = float(max(0.0, min(0.2, self.smoothing_tau)))
        if tau > 0:
            uniform = pd.Series(1.0 / len(prior), index=prior.index, dtype=float)
            posterior = (1 - tau) * posterior + tau * uniform
            posterior = self._normalize_series(posterior)
        return posterior

    # ---- Индукция правдоподобий для отсутствующих ответов ----
    def _induce_subgenre_like(self, answer: str, *, index) -> Optional[pd.Series]:
        # Если есть явное распределение по поджанрам, ничего не делаем (обычно столбец уже есть)
        if answer in self.pr_answer_to_subgenre:
            try:
                dist = {k: float(v) for k, v in self.pr_answer_to_subgenre[answer].items()}
                s = pd.Series(0.0, index=index, dtype=float)
                for sg, p in dist.items():
                    if sg in s.index:
                        s.at[sg] = p
                return self._normalize_series(s)
            except Exception:
                pass
        # Попытаемся вывести из жанров: распределим массу жанра по его поджанрам равномерно
        if answer in self.pr_answer_to_genre:
            s = pd.Series(0.0, index=index, dtype=float)
            for g, p in self.pr_answer_to_genre[answer].items():
                subs = self.genre_hierarchy.get(g) or []
                subs = [sg for sg in subs if sg in s.index]
                if not subs:
                    continue
                add = float(p) / len(subs)
                for sg in subs:
                    s.at[sg] += add
            if s.sum() > 0:
                logging.info("Синтезировано P(answer|subgenre) из жанров для ответа: %s", answer)
                return self._normalize_series(s)
        return None

    def _induce_book_like(self, answer: str, *, index) -> Optional[pd.Series]:
        """Собрать/синтезировать столбец правдоподобий P(answer|book).

        Важно: комбинируем явные связи (answer->book) с индукцией из
        поджанров/жанров, чтобы влияние вопросов распространялось на весь
        актуальный список книг, включая новые.
        """
        s_explicit = pd.Series(0.0, index=index, dtype=float)
        s_induced = pd.Series(0.0, index=index, dtype=float)

        # 1) Явные распределения по книгам
        if answer in self.pr_answer_to_book:
            try:
                for title, p in self.pr_answer_to_book[answer].items():
                    if title in s_explicit.index:
                        s_explicit.at[title] = float(p)
            except Exception:
                # На случай некорректных данных — игнорируем
                pass

        # 2) Индукция из поджанров
        total_signal = 0.0
        if answer in self.pr_answer_to_subgenre:
            for sg, p in self.pr_answer_to_subgenre[answer].items():
                books = self.subgenre_to_books.get(sg, [])
                books = [t for t in books if t in s_induced.index]
                if not books:
                    continue
                add = float(p) / len(books)
                for t in books:
                    s_induced.at[t] += add
                total_signal += float(p)

        # 3) Индукция из жанров
        if answer in self.pr_answer_to_genre:
            for g, p in self.pr_answer_to_genre[answer].items():
                books = self.genre_to_books.get(g, [])
                books = [t for t in books if t in s_induced.index]
                if not books:
                    continue
                add = float(p) / len(books)
                for t in books:
                    s_induced.at[t] += add
                total_signal += float(p)

        # 4) Комбинация источников: если есть явные значения — сохраняем их акцент,
        # одновременно добавляя сигнал индукции, чтобы охватить больше книг.
        s = s_explicit + s_induced
        if s.sum() > 0:
            # Лёгкая нормализация, чтобы вернуть вероятности
            s = self._normalize_series(s)
            # Лог лишь если была использована индукция
            if s_induced.sum() > 0 and (answer in self.pr_answer_to_subgenre or answer in self.pr_answer_to_genre):
                logging.info("Скомбинировано P(answer|book) из явных связей и жанров/поджанров для ответа: %s", answer)
            return s

        # 5) Если нет ни явных, ни индуцированных сигналов — вернуть None
        return None

    def update_with_answer(self, answer: str) -> None:
        try:
            self.prior_genre = self._bayes_update(self.prior_genre, self.genre_likelihoods, answer)
            self.prior_subgenre = self._bayes_update(self.prior_subgenre, self.subgenre_likelihoods, answer)
            self.prior_book = self._bayes_update(self.prior_book, self.book_likelihoods, answer)
            logging.info("Ответ пользователя принят: %s", answer)
        except Exception:
            logging.exception("Не удалось обновить распределения по ответу: %s", answer)

    # --------- Утилиты по книгам ---------
    def get_book_by_title(self, title: str) -> Optional[BookModel]:
        """Вернуть объект BookModel по названию (если есть)."""
        return self.title_to_book.get(title)

    def get_book_details_map(self) -> Dict[str, Dict[str, str]]:
        """Карта названия -> {author, genre, subgenre} для удобства отображения в UI."""
        details: Dict[str, Dict[str, str]] = {}
        for bm in self.book_models:
            details[bm.title] = {"author": bm.author, "genre": bm.genre, "subgenre": bm.subgenre}
        return details

    def update_with_answer_weighted(self, answer: str, level: int) -> None:
        """Обновление с учётом уровня вопроса: L1 сильнее влияет на жанры, L2 — на поджанры, L3 — на книги."""
        try:
            w = self.level_weights.get(int(level), self.level_weights[1])
            self.prior_genre = self._bayes_update_weighted(self.prior_genre, self.genre_likelihoods, answer, w["genre"])
            self.prior_subgenre = self._bayes_update_weighted(self.prior_subgenre, self.subgenre_likelihoods, answer, w["subgenre"])
            self.prior_book = self._bayes_update_weighted(self.prior_book, self.book_likelihoods, answer, w["book"])
            logging.info("Ответ (уровень %s) принят: %s", level, answer)
        except Exception:
            logging.exception("Не удалось выполнить взвешенное обновление по ответу: %s", answer)

    def calculate_posterior_probabilities(self) -> Dict[str, pd.Series]:
        g = self.prior_genre_initial.copy()
        sg = self.prior_subgenre_initial.copy()
        bk = self.prior_book_initial.copy()
        # если уровни известны — использовать взвешенные обновления
        if self.user_answer_levels and len(self.user_answer_levels) == len(self.user_answers):
            for ans, lvl in zip(self.user_answers, self.user_answer_levels):
                w = self.level_weights.get(int(lvl), self.level_weights[1])
                g = self._bayes_update_weighted(g, self.genre_likelihoods, ans, w["genre"])
                sg = self._bayes_update_weighted(sg, self.subgenre_likelihoods, ans, w["subgenre"])
                bk = self._bayes_update_weighted(bk, self.book_likelihoods, ans, w["book"])
        else:
            for ans in self.user_answers:
                g = self._bayes_update(g, self.genre_likelihoods, ans)
                sg = self._bayes_update(sg, self.subgenre_likelihoods, ans)
                bk = self._bayes_update(bk, self.book_likelihoods, ans)
        self.prior_genre, self.prior_subgenre, self.prior_book = g, sg, bk
        return {"genre": g, "subgenre": sg, "book": bk}

    # --------- Загрузка данных ---------
    def _rebuild_state_after_data_change(self, reset_user: bool = True):
        self._rebuild_indexes_and_priors()
        self._build_likelihood_matrices()
        if reset_user:
            self.user_answers = []
            self.user_answer_levels = []

    def load_from_json(self, path: str):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Ожидался объект JSON с полями конфигурации")
            if "books" in data:
                self.books = list(data["books"]) or []
            if "genre_hierarchy" in data:
                self.genre_hierarchy = dict(data["genre_hierarchy"]) or {}
            if "pr_answer_to_genre" in data:
                self.pr_answer_to_genre = dict(data["pr_answer_to_genre"]) or {}
            if "pr_answer_to_subgenre" in data:
                self.pr_answer_to_subgenre = dict(data["pr_answer_to_subgenre"]) or {}
            if "pr_answer_to_book" in data:
                self.pr_answer_to_book = dict(data["pr_answer_to_book"]) or {}
            if "questions_level_1" in data:
                self.questions_level_1 = list(data["questions_level_1"]) or self.questions_level_1
            if "questions_level_2" in data:
                self.questions_level_2 = list(data["questions_level_2"]) or self.questions_level_2
            if "questions_level_3" in data:
                self.questions_level_3 = list(data["questions_level_3"]) or self.questions_level_3
            self._rebuild_state_after_data_change()
            logging.info("JSON данные успешно загружены: %s", path)
        except Exception as e:
            logging.exception("Ошибка загрузки JSON из %s: %s", path, e)
            raise

    def load_books_from_csv(self, path: str):
        try:
            import pandas as pd
            df = pd.read_csv(path)
            required = {"title", "author", "genre", "subgenre"}
            if not required.issubset(df.columns):
                missing = required - set(df.columns)
                raise ValueError(f"В CSV отсутствуют столбцы: {', '.join(missing)}")
            self.books = df[["title", "author", "genre", "subgenre"]].astype(str).to_dict(orient="records")
            self._rebuild_state_after_data_change()
            logging.info("CSV книги успешно загружены: %s (n=%d)", path, len(self.books))
        except Exception as e:
            logging.exception("Ошибка загрузки CSV из %s: %s", path, e)
            raise

    # --------- Логирование ---------
    def _setup_logging(self):
        try:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s %(levelname)s %(message)s',
                filename='app.log',
                filemode='a',
                encoding='utf-8'
            )
            logging.info("Модель инициализирована")
        except Exception:
            logging.getLogger().setLevel(logging.INFO)
