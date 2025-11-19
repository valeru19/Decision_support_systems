import unittest
import pandas as pd

from main import BookRecommender


class TestBayesModel(unittest.TestCase):
    def setUp(self):
        # headless режим без GUI
        self.app = BookRecommender(build_gui=False)

    def test_priors_are_uniform_and_normalized(self):
        g = self.app.prior_genre
        sg = self.app.prior_subgenre
        bk = self.app.prior_book
        # суммы равны 1
        self.assertAlmostEqual(g.sum(), 1.0, places=9)
        self.assertAlmostEqual(sg.sum(), 1.0, places=9)
        self.assertAlmostEqual(bk.sum(), 1.0, places=9)
        # равномерность (все значения равны между собой)
        self.assertTrue((g.nunique() == 1))
        self.assertTrue((sg.nunique() == 1))
        self.assertTrue((bk.nunique() == 1))

    def test_unknown_answer_does_not_change_distribution(self):
        # копии до
        g0 = self.app.prior_genre.copy()
        sg0 = self.app.prior_subgenre.copy()
        bk0 = self.app.prior_book.copy()
        # ответ, которого нет в матрицах
        self.app.update_with_answer("НЕИЗВЕСТНЫЙ_ОТВЕТ")
        pd.testing.assert_series_equal(self.app.prior_genre, g0)
        pd.testing.assert_series_equal(self.app.prior_subgenre, sg0)
        pd.testing.assert_series_equal(self.app.prior_book, bk0)

    def test_bayes_update_basic(self):
        # Выберем ответ, который точно присутствует в genre_likelihoods
        answer = next(iter(self.app.pr_answer_to_genre.keys()))
        prior_before = self.app.prior_genre.copy()
        self.app.update_with_answer(answer)
        # Распределение должно остаться нормализованным и отличаться от априорного
        self.assertAlmostEqual(self.app.prior_genre.sum(), 1.0, places=9)
        self.assertFalse(self.app.prior_genre.equals(prior_before))

    def test_calculate_posterior_probabilities_sequence(self):
        # последовательность ответов (некоторые влияют на жанр/поджанр/книги)
        answers = ["Классическая литература", "Магические", "Сюжет"]
        self.app.user_answers = []
        for a in answers:
            self.app.user_answers.append(a)
        res = self.app.calculate_posterior_probabilities()
        # проверим наличие ключей и нормировку
        self.assertIn("genre", res)
        self.assertIn("subgenre", res)
        self.assertIn("book", res)
        self.assertAlmostEqual(res["genre"].sum(), 1.0, places=9)
        self.assertAlmostEqual(res["subgenre"].sum(), 1.0, places=9)
        self.assertAlmostEqual(res["book"].sum(), 1.0, places=9)


if __name__ == '__main__':
    unittest.main()
