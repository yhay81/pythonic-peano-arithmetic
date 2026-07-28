"""Polynomials over the rationals and minimal tools for studying real roots."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import total_ordering
from itertools import zip_longest
from typing import Iterator, cast

from .integer import Z_ONE, Integer
from .natural_number import N_ONE, N_ZERO, NaturalNumber
from .rational import (
    Q_ONE,
    Q_ZERO,
    Rational,
    cast2r,
    n2r,
    rational,
    z2r,
)
from .utils import LogMessage, log


@total_ordering
@dataclass(frozen=True, slots=True, init=False, eq=False, repr=False)
class Polynomial:
    """Treat a finite sequence ``(a0, ..., an)`` as a polynomial over Q.

    Coefficients are ordered from the constant term upward. Trailing zeroes
    are removed and every coefficient is reduced, giving each polynomial,
    including zero, one canonical representation.
    """

    _coefficients: tuple[Rational, ...]

    def __init__(self, *coefficients: Rational) -> None:
        if not coefficients:
            coefficients = (Q_ZERO,)
        if any(not isinstance(value, Rational) for value in coefficients):
            raise TypeError("Polynomial coefficients must be Rational")

        normalized = [value.reduction() for value in coefficients]
        while len(normalized) > 1 and normalized[-1] == Q_ZERO:
            normalized.pop()
        object.__setattr__(self, "_coefficients", tuple(normalized))

    @property
    def k(self) -> tuple[Rational, ...]:
        """Return the coefficient sequence exposed by the original API."""

        return self._coefficients

    @property
    def coefficients(self) -> tuple[Rational, ...]:
        return self._coefficients

    @property
    def degree(self) -> int:
        """Return the degree, using -1 for the zero polynomial."""

        return -1 if not self else len(self.coefficients) - 1

    @property
    def leading_coefficient(self) -> Rational:
        if not self:
            raise ValueError("the zero polynomial has no leading coefficient")
        return self.coefficients[-1]

    def __eq__(self, other: object) -> bool:
        converted = _coerce_polynomial(other)
        if converted is None:
            return cast(bool, NotImplemented)
        return self.coefficients == converted.coefficients

    def _order_key(self) -> tuple[int, tuple[Rational, ...]]:
        return self.degree, tuple(reversed(self.coefficients))

    def __lt__(self, other: object) -> bool:
        converted = _coerce_polynomial(other)
        if converted is None:
            return cast(bool, NotImplemented)
        return self._order_key() < converted._order_key()

    def __le__(self, other: object) -> bool:
        converted = _coerce_polynomial(other)
        if converted is None:
            return cast(bool, NotImplemented)
        return self._order_key() <= converted._order_key()

    def __add__(self, other: object) -> Polynomial:
        converted = _coerce_polynomial(other)
        if converted is None:
            return cast(Polynomial, NotImplemented)
        coefficients = [
            a + b
            for a, b in zip_longest(
                self.coefficients,
                converted.coefficients,
                fillvalue=Q_ZERO,
            )
        ]
        return Polynomial(*coefficients)

    def __radd__(self, other: object) -> Polynomial:
        return self + other

    def __neg__(self) -> Polynomial:
        return Polynomial(*(-coefficient for coefficient in self))

    def __sub__(self, other: object) -> Polynomial:
        converted = _coerce_polynomial(other)
        if converted is None:
            return cast(Polynomial, NotImplemented)
        return self + -converted

    def __rsub__(self, other: object) -> Polynomial:
        converted = _coerce_polynomial(other)
        if converted is None:
            return cast(Polynomial, NotImplemented)
        return converted - self

    def __mul__(self, other: object) -> Polynomial:
        converted = _coerce_polynomial(other)
        if converted is None:
            return cast(Polynomial, NotImplemented)
        if not self or not converted:
            return P_ZERO
        result = [Q_ZERO] * (len(self.coefficients) + len(converted.coefficients) - 1)
        for i, left in enumerate(self.coefficients):
            for j, right in enumerate(converted.coefficients):
                product = (left * right).reduction()
                result[i + j] = (result[i + j] + product).reduction()
        return Polynomial(*result)

    def __rmul__(self, other: object) -> Polynomial:
        return self * other

    def __divmod__(self, other: object) -> tuple[Polynomial, Polynomial]:
        divisor = _coerce_polynomial(other)
        if divisor is None:
            return cast(tuple[Polynomial, Polynomial], NotImplemented)
        if not divisor:
            raise ZeroDivisionError("cannot divide by the zero polynomial")
        if self.degree < divisor.degree:
            return P_ZERO, self

        quotient = [Q_ZERO] * (self.degree - divisor.degree + 1)
        remainder = self
        while remainder and remainder.degree >= divisor.degree:
            degree_difference = remainder.degree - divisor.degree
            leading = (
                remainder.leading_coefficient / divisor.leading_coefficient
            ).reduction()
            quotient[degree_difference] = leading
            term = Polynomial(*([Q_ZERO] * degree_difference + [leading]))
            remainder = remainder - divisor * term
        return Polynomial(*quotient), remainder

    def __rdivmod__(self, other: object) -> tuple[Polynomial, Polynomial]:
        dividend = _coerce_polynomial(other)
        if dividend is None:
            return cast(tuple[Polynomial, Polynomial], NotImplemented)
        return divmod(dividend, self)

    def __floordiv__(self, other: object) -> Polynomial:
        divisor = _coerce_polynomial(other)
        if divisor is None:
            return cast(Polynomial, NotImplemented)
        result = self.__divmod__(divisor)
        quotient, _ = result
        return quotient

    def __rfloordiv__(self, other: object) -> Polynomial:
        dividend = _coerce_polynomial(other)
        if dividend is None:
            return cast(Polynomial, NotImplemented)
        return dividend // self

    def __mod__(self, other: object) -> Polynomial:
        divisor = _coerce_polynomial(other)
        if divisor is None:
            return cast(Polynomial, NotImplemented)
        result = self.__divmod__(divisor)
        _, remainder = result
        return remainder

    def __rmod__(self, other: object) -> Polynomial:
        dividend = _coerce_polynomial(other)
        if dividend is None:
            return cast(Polynomial, NotImplemented)
        return dividend % self

    def __pow__(self, exponent: object) -> Polynomial:
        if not isinstance(exponent, NaturalNumber):
            return cast(Polynomial, NotImplemented)
        if exponent == N_ZERO:
            return P_ONE
        return (self ** (exponent - N_ONE)) * self

    @log(log_level=31)
    def evaluate(self, value: object) -> tuple[Rational, LogMessage]:
        """Evaluate at ``x=value`` with Horner's method."""

        point = cast2r(value)
        result = Q_ZERO
        for coefficient in reversed(self.coefficients):
            result = (result * point + coefficient).reduction()
        return result, lambda: f"{self!r}: x={point!r} -> {result!r}"

    def sign_at(self, value: object) -> int:
        """Return the exact sign at a point as ``-1``, ``0``, or ``1``.

        Denominators grow exponentially while refining a root interval. When
        only the sign is needed, there is no educational value in constructing
        enormous intermediate Peano values. The same ratios are therefore
        mapped to Python's arbitrary-precision integers and evaluated exactly.
        """

        point = _as_fraction(cast2r(value))
        result = Fraction(0)
        for coefficient in reversed(self.coefficients):
            result = result * point + _as_fraction(coefficient)
        return (result > 0) - (result < 0)

    def derivative(self) -> Polynomial:
        """Return the formal derivative."""

        if self.degree <= 0:
            return P_ZERO
        return Polynomial(
            *(
                coefficient * rational(power, 1)
                for power, coefficient in enumerate(self.coefficients[1:], start=1)
            )
        )

    def monic(self) -> Polynomial:
        """Return a copy whose leading coefficient is one."""

        if not self:
            return P_ZERO
        leading = self.leading_coefficient
        return Polynomial(*(coefficient / leading for coefficient in self.coefficients))

    def gcd(self, other: Polynomial) -> Polynomial:
        """Return the monic greatest common divisor using Euclid's algorithm."""

        if not isinstance(other, Polynomial):
            raise TypeError("gcd expects a Polynomial")
        left, right = self, other
        while right:
            left, right = right, left % right
        return left.monic()

    def square_free(self) -> Polynomial:
        """Return the square-free part with repeated roots removed."""

        if self.degree <= 0:
            return self
        common = self.gcd(self.derivative())
        return (self // common).monic()

    def reduction(self) -> Polynomial:
        return Polynomial(*self.coefficients)

    def __len__(self) -> int:
        return len(self.coefficients)

    def __bool__(self) -> bool:
        return not (len(self.coefficients) == 1 and self.coefficients[0] == Q_ZERO)

    def __int__(self) -> int:
        if self.degree > 0:
            raise TypeError("only constant polynomials can be converted to int")
        coefficient = self.coefficients[0]
        if coefficient.q != Z_ONE:
            raise TypeError("a non-integral constant cannot be converted to int")
        return int(coefficient.p)

    def __hash__(self) -> int:
        if self.degree <= 0:
            # Equal values across the numeric tower must have equal hashes.
            return hash(self.coefficients[0])
        return hash(("Polynomial", self.coefficients))

    def __iter__(self) -> Iterator[Rational]:
        return iter(self.coefficients)

    def __pos__(self) -> Polynomial:
        return self

    def __str__(self) -> str:
        terms: list[tuple[bool, str]] = []
        for power, coefficient in enumerate(self.coefficients):
            if coefficient == Q_ZERO:
                continue
            negative = coefficient < Q_ZERO
            magnitude = abs(coefficient).reduction()
            coefficient_text = _format_rational(magnitude)
            if power == 0:
                body = coefficient_text
            else:
                variable = "x" if power == 1 else f"x^{power}"
                body = (
                    variable if magnitude == Q_ONE else f"{coefficient_text}{variable}"
                )
            terms.append((negative, body))

        if not terms:
            return "0"
        first_negative, first_body = terms[0]
        rendered = f"-{first_body}" if first_negative else first_body
        for negative, body in terms[1:]:
            rendered += f" {'-' if negative else '+'} {body}"
        return rendered

    def __repr__(self) -> str:
        return f"<P({self})>"


class PolynomialIterator:
    """A simple coefficient iterator retained for API compatibility."""

    def __init__(self, *coefficients: Rational) -> None:
        self._iterator = iter(Polynomial(*coefficients).coefficients)

    def __iter__(self) -> PolynomialIterator:
        return self

    def __next__(self) -> Rational:
        return next(self._iterator)


def polynomial(*coefficients: tuple[int, int]) -> Polynomial:
    """Construct a polynomial from ``(numerator, denominator)`` pairs."""

    return Polynomial(*(rational(p, q) for p, q in coefficients))


def n2p(value: NaturalNumber) -> Polynomial:
    return Polynomial(n2r(value))


def z2p(value: Integer) -> Polynomial:
    return Polynomial(z2r(value))


def r2p(value: Rational) -> Polynomial:
    if not isinstance(value, Rational):
        raise TypeError("r2p expects a Rational")
    return Polynomial(value)


def _coerce_polynomial(value: object) -> Polynomial | None:
    if isinstance(value, NaturalNumber):
        return n2p(value)
    if isinstance(value, Integer):
        return z2p(value)
    if isinstance(value, Rational):
        return r2p(value)
    if isinstance(value, Polynomial):
        return value
    return None


def cast2p(value: object) -> Polynomial:
    converted = _coerce_polynomial(value)
    if converted is None:
        raise TypeError(f"{value!r} is not a Polynomial")
    return converted


def sturm_sequence(value: Polynomial) -> tuple[Polynomial, ...]:
    """Return the Sturm sequence used to count real roots."""

    if not isinstance(value, Polynomial):
        raise TypeError("sturm_sequence expects a Polynomial")
    if value.degree <= 0:
        raise ValueError("a constant polynomial has no Sturm sequence")

    square_free = value.square_free()
    sequence = [square_free, square_free.derivative()]
    while sequence[-1]:
        remainder = sequence[-2] % sequence[-1]
        if not remainder:
            break
        sequence.append(-remainder)
    return tuple(sequence)


def sign_variations(sequence: tuple[Polynomial, ...], point: Rational) -> int:
    """Count nonzero sign changes after evaluating a Sturm sequence."""

    signs: list[bool] = []
    for value in sequence:
        sign = value.sign_at(point)
        if sign == 0:
            continue
        signs.append(sign < 0)
    return sum(left != right for left, right in zip(signs, signs[1:]))


def count_real_roots(value: Polynomial, lower: Rational, upper: Rational) -> int:
    """Count distinct real roots in the open interval ``(lower, upper)``."""

    if not isinstance(value, Polynomial):
        raise TypeError("value must be a Polynomial")
    lower = cast2r(lower)
    upper = cast2r(upper)
    if lower >= upper:
        raise ValueError("lower must be less than upper")
    if value.sign_at(lower) == 0 or value.sign_at(upper) == 0:
        raise ValueError("interval endpoints must not be roots")
    sequence = sturm_sequence(value)
    return sign_variations(sequence, lower) - sign_variations(sequence, upper)


def _format_rational(value: Rational) -> str:
    reduced = value.reduction()
    if reduced.q == Z_ONE:
        return str(reduced.p)
    return str(reduced)


def _as_fraction(value: Rational) -> Fraction:
    return Fraction(int(value.p), int(value.q))


P_ZERO = Polynomial(Q_ZERO)
P_ONE = Polynomial(Q_ONE)
