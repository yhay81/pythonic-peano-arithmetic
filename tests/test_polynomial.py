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

    def test_floordiv(self) -> None:
        dividend = Polynomial(rational(1, 1), rational(2, 1), rational(1, 1))
        divisor = Polynomial(rational(1, 1), rational(1, 1))
        self.assertEqual(
            dividend // divisor, Polynomial(rational(1, 1), rational(1, 1))
        )

    def test_floordiv_with_remainder(self) -> None:
        dividend = Polynomial(rational(1, 1), rational(0, 1), rational(1, 1))
        divisor = Polynomial(rational(1, 1), rational(1, 1))
        quotient = dividend // divisor
        remainder = dividend - divisor * quotient
        self.assertEqual(quotient, Polynomial(rational(-1, 1), rational(1, 1)))
        self.assertEqual(remainder, Polynomial(rational(2, 1)))

    def test_floordiv_zero_divisor(self) -> None:
        with self.assertRaises(ZeroDivisionError):
            Polynomial(rational(1, 1)) // Polynomial(rational(0, 1))

    def test_lt_degree(self) -> None:
        self.assertLess(
            Polynomial(rational(1, 1), rational(1, 1)),
            Polynomial(rational(1, 1), rational(0, 1), rational(1, 1)),
        )

    def test_lt_coefficients(self) -> None:
        self.assertLess(
            Polynomial(rational(1, 1), rational(2, 1), rational(1, 1)),
            Polynomial(rational(1, 1), rational(3, 1), rational(1, 1)),
        )

    def test_int_constant(self) -> None:
        self.assertEqual(int(Polynomial(rational(3, 1))), 3)

    def test_int_non_integer(self) -> None:
        with self.assertRaises(TypeError):
            int(Polynomial(rational(1, 2)))

    def test_int_non_constant(self) -> None:
        with self.assertRaises(TypeError):
            int(Polynomial(rational(1, 1), rational(1, 1)))

    def test_hash(self) -> None:
        self.assertEqual(
            hash(Polynomial(rational(1, 2))), hash(Polynomial(rational(2, 4)))
        )


if __name__ == "__main__":
    unittest.main()
