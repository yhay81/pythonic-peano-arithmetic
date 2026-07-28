import unittest

from peano import (
    N_ONE,
    N_ZERO,
    P_ONE,
    P_ZERO,
    Q_ONE,
    Q_ZERO,
    Z_ONE,
    Z_ZERO,
    Integer,
    NaturalNumber,
    Polynomial,
    Rational,
    integer,
    natural_number,
)

NumericValue = NaturalNumber | Integer | Rational | Polynomial


class TestNumericTower(unittest.TestCase):
    def setUp(self) -> None:
        self.values: tuple[NumericValue, ...] = (N_ONE, Z_ONE, Q_ONE, P_ONE)

    def test_equal_values_have_equal_hashes(self) -> None:
        for left in self.values:
            for right in self.values:
                self.assertEqual(left, right)
                self.assertEqual(hash(left), hash(right))
        self.assertEqual(len(set(self.values)), 1)

    def test_zero_values_have_equal_hashes_and_integer_conversion(self) -> None:
        values: tuple[NumericValue, ...] = (N_ZERO, Z_ZERO, Q_ZERO, P_ZERO)
        for left in values:
            for right in values:
                self.assertEqual(left, right)
                self.assertEqual(hash(left), hash(right))
        self.assertEqual(len(set(values)), 1)
        self.assertEqual(int(P_ZERO), 0)

    def test_mixed_addition_promotes_to_higher_type(self) -> None:
        expected_types = (
            (type(N_ONE), type(Z_ONE), type(Q_ONE), type(P_ONE)),
            (type(Z_ONE), type(Z_ONE), type(Q_ONE), type(P_ONE)),
            (type(Q_ONE), type(Q_ONE), type(Q_ONE), type(P_ONE)),
            (type(P_ONE), type(P_ONE), type(P_ONE), type(P_ONE)),
        )
        for i, left in enumerate(self.values):
            for j, right in enumerate(self.values):
                result = left + right
                self.assertIsInstance(result, expected_types[i][j])
                self.assertEqual(result, N_ONE + N_ONE)

    def test_mixed_subtraction_and_multiplication_are_symmetric(self) -> None:
        for left in self.values:
            for right in self.values:
                self.assertFalse(left - right)
                self.assertEqual(left * right, left)
                self.assertEqual(left * right, right)

    def test_mixed_division_promotes_to_rational(self) -> None:
        values = (N_ONE, Z_ONE, Q_ONE)
        for left in values:
            for right in values:
                result = left / right
                self.assertIsInstance(result, Rational)
                self.assertEqual(result, Q_ONE)

    def test_mixed_comparisons_are_symmetric(self) -> None:
        for left in self.values:
            for right in self.values:
                self.assertLessEqual(left, right)
                self.assertGreaterEqual(left, right)
                self.assertFalse(left < right)
                self.assertFalse(left > right)

    def test_mixed_polynomial_floor_division(self) -> None:
        polynomial = Polynomial(Q_ONE, Q_ONE)
        self.assertEqual(P_ONE // Q_ONE, P_ONE)
        self.assertFalse(polynomial.__rfloordiv__(Q_ONE))
        self.assertEqual(divmod(Q_ONE, polynomial), (P_ZERO, P_ONE))

    def test_mixed_integer_floor_division_is_symmetric(self) -> None:
        for natural_value in range(4):
            dividend = natural_number(natural_value)
            for integer_value in range(-3, 4):
                if integer_value == 0:
                    continue
                divisor = integer(integer_value)
                quotient, remainder = divmod(natural_value, integer_value)

                self.assertIsInstance(dividend // divisor, Integer)
                self.assertEqual(dividend // divisor, integer(quotient))
                self.assertIsInstance(dividend % divisor, Integer)
                self.assertEqual(dividend % divisor, integer(remainder))
                self.assertEqual(
                    divmod(dividend, divisor),
                    (integer(quotient), integer(remainder)),
                )


if __name__ == "__main__":
    unittest.main()
