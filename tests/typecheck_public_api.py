"""Ensure ty does not regress public operation types to ``Any``."""

from typing_extensions import assert_type

from peano import (
    N_ONE,
    P_ONE,
    Q_ONE,
    Z_ONE,
    Integer,
    NaturalNumber,
    Polynomial,
    Rational,
)

assert_type(N_ONE + N_ONE, NaturalNumber)
assert_type(N_ONE / N_ONE, Rational)
assert_type(-N_ONE, Integer)
assert_type(N_ONE.structural_str(), str)
assert_type(Z_ONE + Z_ONE, Integer)
assert_type(Z_ONE / Z_ONE, Rational)
assert_type(Q_ONE + Q_ONE, Rational)
assert_type(P_ONE + P_ONE, Polynomial)
