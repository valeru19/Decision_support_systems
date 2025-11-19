import tkinter as tk
import logging
from typing import Optional, Any

from model import BayesianProbabilityModel
from view import MainView
from controller import AppController


class BookRecommender:
    """
    Обёртка для совместимости с существующими тестами и кодом.
    Делегирует бизнес-логику модели BayesianProbabilityModel.
    При build_gui=True инициализирует полноценное MVC-приложение.
    """

    def __init__(self, root: Optional[tk.Tk] = None, *, build_gui: bool = True):
        self.model = BayesianProbabilityModel(enable_logging=True)
        self.root = None
        self.view = None
        self.controller = None
        if build_gui:
            self.root = root or tk.Tk()
            self.view = MainView(self.root)
            self.controller = AppController(self.model, self.view)

    # ---- делегирование атрибутов, используемых тестами ----
    def __getattr__(self, name: str) -> Any:
        # Доступ к полям модели: priors, likelihoods, вопросы, словари вероятностей, user_answers
        if hasattr(self.model, name):
            return getattr(self.model, name)
        raise AttributeError(name)

    # ---- методы-делегаты ----
    def update_with_answer(self, answer: str) -> None:
        self.model.update_with_answer(answer)

    def calculate_posterior_probabilities(self):
        return self.model.calculate_posterior_probabilities()

    def initialize_priors(self) -> None:
        self.model.initialize_priors()

    def load_from_json(self, path: str):
        return self.model.load_from_json(path)

    def load_books_from_csv(self, path: str):
        return self.model.load_books_from_csv(path)


if __name__ == '__main__':
    app = BookRecommender(build_gui=True)
    app.view.root.minsize(480, 320)
    app.view.root.mainloop()
