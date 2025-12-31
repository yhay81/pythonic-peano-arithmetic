import sys
import time
import unittest

from peano.polynomial import Polynomial
from peano.rational import rational

sys.setrecursionlimit(1 << 16)


class TestPolynomial(unittest.TestCase):
    def setUp(self) -> None:
        self.startTime = time.time()

    def tearDown(self) -> None:
        t = time.time() - self.startTime
        print("{}: {}ms".format(self.id(), int(t * 1000)))

    def test_eq_missing_coefficients(self) -> None:
        self.assertEqual(
            Polynomial(rational(1, 1), rational(0, 1)),
            Polynomial(rational(1, 1)),
        )

    def test_add_different_degree(self) -> None:
        self.assertEqual(
            Polynomial(rational(1, 1), rational(1, 1)) + Polynomial(rational(1, 1)),
            Polynomial(rational(2, 1), rational(1, 1)),
        )

    def test_mul(self) -> None:
        self.assertEqual(
            Polynomial(rational(1, 1), rational(1, 1))
            * Polynomial(rational(1, 1), rational(1, 1)),
            Polynomial(rational(1, 1), rational(2, 1), rational(1, 1)),
        )

    def test_len_trailing_zero(self) -> None:
        self.assertEqual(len(Polynomial(rational(1, 1), rational(0, 1))), 1)


if __name__ == "__main__":
    unittest.main()
