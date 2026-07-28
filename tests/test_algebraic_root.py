import unittest

from peano import (
    Q_ONE,
    Q_ZERO,
    AlgebraicRoot,
    Polynomial,
    RationalInterval,
    algebraic_root,
    count_real_roots,
    natural_number,
    rational,
    sturm_sequence,
)


class TestAlgebraicRoot(unittest.TestCase):
    def setUp(self) -> None:
        self.sqrt_two_polynomial = Polynomial(rational(-2, 1), Q_ZERO, Q_ONE)

    def test_sturm_count_for_two_real_roots(self) -> None:
        self.assertEqual(
            count_real_roots(
                self.sqrt_two_polynomial,
                rational(-2, 1),
                rational(2, 1),
            ),
            2,
        )
        self.assertEqual(len(sturm_sequence(self.sqrt_two_polynomial)), 3)

    def test_sturm_count_removes_repeated_factors_without_intermediate_blowup(
        self,
    ) -> None:
        repeated_root_polynomial = Polynomial(
            rational(-1, 1),
            rational(-1, 1),
            rational(1, 1),
            rational(1, 1),
        )

        self.assertEqual(
            repeated_root_polynomial.square_free(),
            Polynomial(rational(-1, 1), Q_ZERO, Q_ONE),
        )
        self.assertEqual(
            count_real_roots(
                repeated_root_polynomial,
                rational(-5, 2),
                rational(5, 2),
            ),
            2,
        )

    def test_polynomial_is_readable_and_differentiable(self) -> None:
        self.assertEqual(str(self.sqrt_two_polynomial), "-2 + x^2")
        self.assertEqual(
            self.sqrt_two_polynomial.derivative(),
            Polynomial(Q_ZERO, rational(2, 1)),
        )
        self.assertEqual(
            self.sqrt_two_polynomial.evaluate(rational(3, 2)),
            rational(1, 4),
        )

    def test_bisection_keeps_one_root_and_halves_width(self) -> None:
        root = algebraic_root(
            self.sqrt_two_polynomial,
            (1, 1),
            (2, 1),
        )

        approximation = root.approximate(3)

        self.assertEqual(approximation.width, rational(1, 8))
        self.assertLess(
            self.sqrt_two_polynomial.sign_at(approximation.lower),
            0,
        )
        self.assertGreater(
            self.sqrt_two_polynomial.sign_at(approximation.upper),
            0,
        )
        self.assertEqual(len(root.trace(3)), 4)

    def test_more_steps_remain_practical_with_peano_endpoints(self) -> None:
        root = algebraic_root(self.sqrt_two_polynomial, (1, 1), (2, 1))

        approximation = root.approximate(natural_number(8))

        self.assertEqual(approximation.lower.as_integer_ratio(), (181, 128))
        self.assertEqual(approximation.upper.as_integer_ratio(), (363, 256))
        self.assertEqual(approximation.width.as_integer_ratio(), (1, 256))

    def test_exact_midpoint_root_becomes_point_interval(self) -> None:
        identity = Polynomial(Q_ZERO, Q_ONE)
        root = algebraic_root(identity, (-1, 1), (1, 1))

        approximation = root.approximate(1)

        self.assertTrue(approximation.is_point)
        self.assertEqual(approximation.midpoint, Q_ZERO)

    def test_invalid_isolating_interval_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            algebraic_root(self.sqrt_two_polynomial, (2, 1), (3, 1))

    def test_interval_with_multiple_roots_is_rejected(self) -> None:
        three_roots = Polynomial(
            Q_ZERO,
            rational(-1, 1),
            Q_ZERO,
            Q_ONE,
        )
        self.assertEqual(
            count_real_roots(three_roots, rational(-2, 1), rational(2, 1)),
            3,
        )
        with self.assertRaisesRegex(ValueError, "exactly one"):
            AlgebraicRoot(
                three_roots,
                RationalInterval(rational(-2, 1), rational(2, 1)),
            )

    def test_invalid_step_count_is_rejected(self) -> None:
        root = algebraic_root(self.sqrt_two_polynomial, (1, 1), (2, 1))
        with self.assertRaises(ValueError):
            root.approximate(-1)
        with self.assertRaises(TypeError):
            root.approximate(1.5)  # ty: ignore[invalid-argument-type]


if __name__ == "__main__":
    unittest.main()
