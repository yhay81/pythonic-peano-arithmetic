"""Observe non-rational roots through shrinking rational intervals."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .natural_number import NaturalNumber
from .polynomial import Polynomial, count_real_roots
from .rational import Rational, rational
from .utils import LogMessage, log, translate


@dataclass(frozen=True, slots=True)
class RationalInterval:
    """A closed interval with rational endpoints.

    Equal endpoints are allowed and represent one exact rational point.
    """

    lower: Rational
    upper: Rational

    def __post_init__(self) -> None:
        if not isinstance(self.lower, Rational) or not isinstance(self.upper, Rational):
            raise TypeError("interval endpoints must be Rational values")
        lower_fraction = _as_fraction(self.lower)
        upper_fraction = _as_fraction(self.upper)
        if lower_fraction > upper_fraction:
            raise ValueError("lower must be less than or equal to upper")
        object.__setattr__(self, "lower", _from_fraction(lower_fraction))
        object.__setattr__(self, "upper", _from_fraction(upper_fraction))

    @property
    def width(self) -> Rational:
        return _from_fraction(_as_fraction(self.upper) - _as_fraction(self.lower))

    @property
    def midpoint(self) -> Rational:
        return _from_fraction((_as_fraction(self.lower) + _as_fraction(self.upper)) / 2)

    @property
    def is_point(self) -> bool:
        return _as_fraction(self.lower) == _as_fraction(self.upper)

    def contains(self, value: Rational) -> bool:
        point = _as_fraction(value)
        return _as_fraction(self.lower) <= point <= _as_fraction(self.upper)

    def __str__(self) -> str:
        return f"[{self.lower}, {self.upper}]"


@dataclass(frozen=True, slots=True, eq=False)
class AlgebraicRoot:
    """Identify one real polynomial root by an isolating interval.

    This educational object is not a complete real-number type. It deliberately
    omits arithmetic and general equality and focuses on shrinking rational
    intervals while preserving one root.
    """

    polynomial: Polynomial
    interval: RationalInterval

    def __post_init__(self) -> None:
        if not isinstance(self.polynomial, Polynomial):
            raise TypeError("polynomial must be a Polynomial")
        if not isinstance(self.interval, RationalInterval):
            raise TypeError("interval must be a RationalInterval")
        if self.polynomial.degree <= 0:
            raise ValueError("a root-defining polynomial must have positive degree")
        if self.interval.is_point:
            raise ValueError("the initial interval must have positive width")

        lower_sign = self.polynomial.sign_at(self.interval.lower)
        upper_sign = self.polynomial.sign_at(self.interval.upper)
        if lower_sign == 0 or upper_sign == 0:
            raise ValueError("initial interval endpoints cannot be roots")
        if lower_sign == upper_sign:
            raise ValueError("the polynomial must change sign across the endpoints")

        number_of_roots = count_real_roots(
            self.polynomial,
            self.interval.lower,
            self.interval.upper,
        )
        if number_of_roots != 1:
            raise ValueError(
                "the initial interval must contain exactly one distinct real root "
                f"(found {number_of_roots})"
            )

    def approximate(self, steps: int | NaturalNumber) -> RationalInterval:
        """Bisect ``steps`` times and return a closed interval containing the root."""

        count = _step_count(steps)
        interval = self.interval
        for _ in range(count):
            if interval.is_point:
                break
            interval = _bisect(self.polynomial, interval)
        return interval

    def trace(self, steps: int | NaturalNumber) -> tuple[RationalInterval, ...]:
        """Return every bisection interval, including the initial interval."""

        count = _step_count(steps)
        intervals = [self.interval]
        for _ in range(count):
            if intervals[-1].is_point:
                break
            intervals.append(_bisect(self.polynomial, intervals[-1]))
        return tuple(intervals)

    def __repr__(self) -> str:
        return f"<AlgebraicRoot({self.polynomial!r}, {self.interval})>"

    def __str__(self) -> str:
        return f"root of {self.polynomial} in {self.interval}"


@log(log_level=41)
def _bisect(
    polynomial_value: Polynomial,
    interval: RationalInterval,
) -> tuple[RationalInterval, LogMessage]:
    midpoint = interval.midpoint
    midpoint_sign = polynomial_value.sign_at(midpoint)

    if midpoint_sign == 0:
        result = RationalInterval(midpoint, midpoint)
        return (
            result,
            lambda: translate(
                "midpoint_root",
                polynomial=repr(polynomial_value),
                midpoint=repr(midpoint),
            ),
        )

    lower_sign = polynomial_value.sign_at(interval.lower)
    if lower_sign != midpoint_sign:
        result = RationalInterval(interval.lower, midpoint)
    else:
        result = RationalInterval(midpoint, interval.upper)
    return (
        result,
        lambda: f"{polynomial_value!r}: {interval} -> {result}",
    )


def algebraic_root(
    polynomial_value: Polynomial,
    lower: tuple[int, int],
    upper: tuple[int, int],
) -> AlgebraicRoot:
    """Construct an algebraic root from Python integer endpoint pairs."""

    return AlgebraicRoot(
        polynomial_value,
        RationalInterval(rational(*lower), rational(*upper)),
    )


def _step_count(value: int | NaturalNumber) -> int:
    if isinstance(value, NaturalNumber):
        return int(value)
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("steps must be an int or NaturalNumber")
    if value < 0:
        raise ValueError("steps must be non-negative")
    return value


def _as_fraction(value: Rational) -> Fraction:
    return Fraction(int(value.p), int(value.q))


def _from_fraction(value: Fraction) -> Rational:
    return rational(value.numerator, value.denominator)
