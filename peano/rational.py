"""Construct rational numbers as equivalence classes of integer ratios."""

from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering
from typing import cast

from .integer import Z_ONE, Z_ZERO, Integer, integer, n2z
from .natural_number import N_ONE, N_ZERO, NaturalNumber
from .utils import LogMessage, log


@total_ordering
@dataclass(frozen=True, slots=True, eq=False, repr=False)
class Rational:
    """Represent a rational number as an integer ratio ``p / q``, ``q != 0``.

    ``p/q ~ r/s`` is defined by the cross products ``p*s = q*r``. Input
    representatives are preserved; ``reduction`` normalizes the denominator
    and reduces the ratio only when explicitly requested.
    """

    p: Integer
    q: Integer

    def __post_init__(self) -> None:
        if not isinstance(self.p, Integer) or not isinstance(self.q, Integer):
            raise TypeError("Rational.p and Rational.q must be Integer values")
        if self.q == Z_ZERO:
            raise ZeroDivisionError("the denominator cannot be zero")

    def __repr__(self) -> str:
        return f"<Q({self})>"

    def __str__(self) -> str:
        return f"{self.p}/{self.q}"

    @log(log_level=21)
    def __eq__(self, other: object) -> tuple[bool, LogMessage]:
        converted = _coerce_rational(other)
        if converted is None:
            return (
                cast(bool, NotImplemented),
                lambda: f"{self!r} == {other!r} = NotImplemented",
            )
        result = self.p * converted.q == self.q * converted.p
        return (
            result,
            lambda: (
                f"{self!r} == {converted!r} ⇔ "
                f"{self.p!r} * {converted.q!r} == "
                f"{self.q!r} * {converted.p!r}"
            ),
        )

    @log(log_level=22)
    def __lt__(self, other: object) -> tuple[bool, LogMessage]:
        converted = _coerce_rational(other)
        if converted is None:
            return (
                cast(bool, NotImplemented),
                lambda: f"{self!r} < {other!r} = NotImplemented",
            )
        left = self.p * converted.q
        right = self.q * converted.p
        denominators_have_different_signs = (self.q < Z_ZERO) != (converted.q < Z_ZERO)
        result = left > right if denominators_have_different_signs else left < right
        operator = ">" if denominators_have_different_signs else "<"
        return (
            result,
            lambda: f"{self!r} < {converted!r} ⇔ {left!r} {operator} {right!r}",
        )

    @log(log_level=22)
    def __le__(self, other: object) -> tuple[bool, LogMessage]:
        converted = _coerce_rational(other)
        if converted is None:
            return (
                cast(bool, NotImplemented),
                lambda: f"{self!r} <= {other!r} = NotImplemented",
            )
        left = self.p * converted.q
        right = self.q * converted.p
        denominators_have_different_signs = (self.q < Z_ZERO) != (converted.q < Z_ZERO)
        result = left >= right if denominators_have_different_signs else left <= right
        operator = ">=" if denominators_have_different_signs else "<="
        return (
            result,
            lambda: f"{self!r} <= {converted!r} ⇔ {left!r} {operator} {right!r}",
        )

    @log(log_level=24)
    def __add__(self, other: object) -> tuple[Rational, LogMessage]:
        converted = _coerce_rational(other)
        if converted is None:
            return (
                cast(Rational, NotImplemented),
                lambda: f"{self!r} + {other!r} = NotImplemented",
            )
        result = Rational(
            self.p * converted.q + self.q * converted.p,
            self.q * converted.q,
        )
        return (
            result,
            lambda: (
                f"{self!r} + {converted!r} = "
                f"({self.p!r} * {converted.q!r} + "
                f"{self.q!r} * {converted.p!r}) / "
                f"({self.q!r} * {converted.q!r})"
            ),
        )

    def __radd__(self, other: object) -> Rational:
        return self + other

    @log(log_level=24)
    def __neg__(self) -> tuple[Rational, LogMessage]:
        result = Rational(-self.p, self.q)
        return result, lambda: f"-{self!r} = (-{self.p!r}) / {self.q!r}"

    @log(log_level=24)
    def __sub__(self, other: object) -> tuple[Rational, LogMessage]:
        converted = _coerce_rational(other)
        if converted is None:
            return (
                cast(Rational, NotImplemented),
                lambda: f"{self!r} - {other!r} = NotImplemented",
            )
        return (
            self + -converted,
            lambda: f"{self!r} - {converted!r} = {self!r} + (-{converted!r})",
        )

    def __rsub__(self, other: object) -> Rational:
        converted = _coerce_rational(other)
        if converted is None:
            return cast(Rational, NotImplemented)
        return converted - self

    @log(log_level=25)
    def __mul__(self, other: object) -> tuple[Rational, LogMessage]:
        converted = _coerce_rational(other)
        if converted is None:
            return (
                cast(Rational, NotImplemented),
                lambda: f"{self!r} * {other!r} = NotImplemented",
            )
        result = Rational(self.p * converted.p, self.q * converted.q)
        return (
            result,
            lambda: (
                f"{self!r} * {converted!r} = "
                f"({self.p!r} * {converted.p!r}) / "
                f"({self.q!r} * {converted.q!r})"
            ),
        )

    def __rmul__(self, other: object) -> Rational:
        return self * other

    @log(log_level=25)
    def __truediv__(self, other: object) -> tuple[Rational, LogMessage]:
        converted = _coerce_rational(other)
        if converted is None:
            return (
                cast(Rational, NotImplemented),
                lambda: f"{self!r} / {other!r} = NotImplemented",
            )
        if not converted:
            raise ZeroDivisionError("division by zero")
        result = Rational(self.p * converted.q, self.q * converted.p)
        return (
            result,
            lambda: (
                f"{self!r} / {converted!r} = "
                f"({self.p!r} * {converted.q!r}) / "
                f"({self.q!r} * {converted.p!r})"
            ),
        )

    def __rtruediv__(self, other: object) -> Rational:
        converted = _coerce_rational(other)
        if converted is None:
            return cast(Rational, NotImplemented)
        return converted / self

    @log(log_level=26)
    def __pow__(self, exponent: object) -> tuple[Rational, LogMessage]:
        if not isinstance(exponent, NaturalNumber):
            return (
                cast(Rational, NotImplemented),
                lambda: f"{self!r} ** {exponent!r} = NotImplemented",
            )
        if exponent == N_ZERO:
            return Q_ONE, lambda: f"{self!r} ** {exponent!r} = {Q_ONE!r}"
        return (
            (self ** (exponent - N_ONE)) * self,
            lambda: (
                f"{self!r} ** {exponent!r} = "
                f"({self!r} ** ({exponent!r} - {N_ONE!r})) * {self!r}"
            ),
        )

    def __bool__(self) -> bool:
        return self.p != Z_ZERO

    def __hash__(self) -> int:
        reduced = self.reduction()
        if reduced.q == Z_ONE:
            # Equal NaturalNumber and Integer values must share the same hash.
            return hash(reduced.p)
        return hash(("Rational", int(reduced.p), int(reduced.q)))

    def __pos__(self) -> Rational:
        return self

    def __abs__(self) -> Rational:
        return Rational(Integer(abs(self.p), N_ZERO), Integer(abs(self.q), N_ZERO))

    def as_integer_ratio(self) -> tuple[int, int]:
        """Return a reduced Python integer ratio with a positive denominator.

        This boundary API avoids constructing equivalent but enormous Peano
        intermediates when displaying or validating large rational values.
        """

        from math import gcd

        numerator, denominator = int(self.p), int(self.q)
        if denominator < 0:
            numerator, denominator = -numerator, -denominator
        divisor = gcd(abs(numerator), denominator)
        return numerator // divisor, denominator // divisor

    def reduction(self) -> Rational:
        """Return a reduced representative with a positive denominator."""

        numerator = self.p.normalize()
        denominator = self.q.normalize()
        if denominator < Z_ZERO:
            numerator, denominator = -numerator, -denominator

        a, b = abs(numerator), abs(denominator)
        while b:
            a, b = b, a % b
        divisor = Integer(a, N_ZERO)
        return Rational(numerator // divisor, denominator // divisor)


def rational(numerator: int, denominator: int) -> Rational:
    """Construct a rational number from two Python integers."""

    return Rational(integer(numerator), integer(denominator))


def n2r(value: NaturalNumber) -> Rational:
    """Embed a natural number into the rationals."""

    if not isinstance(value, NaturalNumber):
        raise TypeError("n2r expects a NaturalNumber")
    return Rational(n2z(value), Z_ONE)


def z2r(value: Integer) -> Rational:
    """Embed an integer into the rationals."""

    if not isinstance(value, Integer):
        raise TypeError("z2r expects an Integer")
    return Rational(value, Z_ONE)


def _coerce_rational(value: object) -> Rational | None:
    if isinstance(value, NaturalNumber):
        return n2r(value)
    if isinstance(value, Integer):
        return z2r(value)
    if isinstance(value, Rational):
        return value
    return None


def cast2r(value: object) -> Rational:
    """Coerce a supported numeric value to ``Rational``."""

    converted = _coerce_rational(value)
    if converted is None:
        raise TypeError(f"{value!r} is not a Rational")
    return converted


Q_ZERO = Rational(Z_ZERO, Z_ONE)
Q_ONE = Rational(Z_ONE, Z_ONE)
Q_MINUS_ONE = Rational(-Z_ONE, Z_ONE)
