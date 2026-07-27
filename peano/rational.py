"""整数の比の同値類として有理数を構成する。"""

from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering
from typing import Any

from .integer import Z_ONE, Z_ZERO, Integer, integer, n2z
from .natural_number import N_ONE, N_ZERO, NaturalNumber
from .utils import log


@total_ordering
@dataclass(frozen=True, slots=True, eq=False, repr=False)
class Rational:
    """整数の対 ``p / q``（``q != 0``）で有理数を表す。

    ``p/q ~ r/s`` は交差積 ``p*s = q*r`` で定義する。入力表現は保存し、
    ``reduction`` を呼んだときだけ分母を正にして既約化する。
    """

    p: Integer
    q: Integer

    def __post_init__(self) -> None:
        if not isinstance(self.p, Integer) or not isinstance(self.q, Integer):
            raise TypeError("Rational の p と q は Integer でなければなりません")
        if self.q == Z_ZERO:
            raise ZeroDivisionError("分母は 0 にできません")

    def __repr__(self) -> str:
        return f"<Q({self})>"

    def __str__(self) -> str:
        return f"{self.p}/{self.q}"

    @log(log_level=21)
    def __eq__(self, other: object) -> tuple[bool | Any, str]:
        converted = _coerce_rational(other)
        if converted is None:
            return NotImplemented, f"{self!r} == {other!r} = NotImplemented"
        result = self.p * converted.q == self.q * converted.p
        return (
            result,
            f"{self!r} == {converted!r} iff "
            f"{self.p!r} * {converted.q!r} == "
            f"{self.q!r} * {converted.p!r}",
        )

    @log(log_level=22)
    def __lt__(self, other: object) -> tuple[bool | Any, str]:
        converted = _coerce_rational(other)
        if converted is None:
            return NotImplemented, f"{self!r} < {other!r} = NotImplemented"
        left = self.p * converted.q
        right = self.q * converted.p
        denominators_have_different_signs = (self.q < Z_ZERO) != (converted.q < Z_ZERO)
        result = left > right if denominators_have_different_signs else left < right
        operator = ">" if denominators_have_different_signs else "<"
        return (
            result,
            f"{self!r} < {converted!r} iff {left!r} {operator} {right!r}",
        )

    @log(log_level=22)
    def __le__(self, other: object) -> tuple[bool | Any, str]:
        converted = _coerce_rational(other)
        if converted is None:
            return NotImplemented, f"{self!r} <= {other!r} = NotImplemented"
        left = self.p * converted.q
        right = self.q * converted.p
        denominators_have_different_signs = (self.q < Z_ZERO) != (converted.q < Z_ZERO)
        result = left >= right if denominators_have_different_signs else left <= right
        operator = ">=" if denominators_have_different_signs else "<="
        return (
            result,
            f"{self!r} <= {converted!r} iff {left!r} {operator} {right!r}",
        )

    @log(log_level=24)
    def __add__(self, other: object) -> tuple[Rational | Any, str]:
        converted = _coerce_rational(other)
        if converted is None:
            return NotImplemented, f"{self!r} + {other!r} = NotImplemented"
        result = Rational(
            self.p * converted.q + self.q * converted.p,
            self.q * converted.q,
        )
        return (
            result,
            f"{self!r} + {converted!r} = "
            f"({self.p!r}{converted.q!r} + "
            f"{self.q!r}{converted.p!r}) / "
            f"({self.q!r}{converted.q!r})",
        )

    def __radd__(self, other: object) -> Rational | Any:
        return self + other

    @log(log_level=24)
    def __neg__(self) -> tuple[Rational, str]:
        result = Rational(-self.p, self.q)
        return result, f"-{self!r} = (-{self.p!r}) / {self.q!r}"

    @log(log_level=24)
    def __sub__(self, other: object) -> tuple[Rational | Any, str]:
        converted = _coerce_rational(other)
        if converted is None:
            return NotImplemented, f"{self!r} - {other!r} = NotImplemented"
        return (
            self + -converted,
            f"{self!r} - {converted!r} = {self!r} + (-{converted!r})",
        )

    def __rsub__(self, other: object) -> Rational | Any:
        converted = _coerce_rational(other)
        if converted is None:
            return NotImplemented
        return converted - self

    @log(log_level=25)
    def __mul__(self, other: object) -> tuple[Rational | Any, str]:
        converted = _coerce_rational(other)
        if converted is None:
            return NotImplemented, f"{self!r} * {other!r} = NotImplemented"
        result = Rational(self.p * converted.p, self.q * converted.q)
        return (
            result,
            f"{self!r} * {converted!r} = "
            f"({self.p!r}{converted.p!r}) / "
            f"({self.q!r}{converted.q!r})",
        )

    def __rmul__(self, other: object) -> Rational | Any:
        return self * other

    @log(log_level=25)
    def __truediv__(self, other: object) -> tuple[Rational | Any, str]:
        converted = _coerce_rational(other)
        if converted is None:
            return NotImplemented, f"{self!r} / {other!r} = NotImplemented"
        if not converted:
            raise ZeroDivisionError("0 で割ることはできません")
        result = Rational(self.p * converted.q, self.q * converted.p)
        return (
            result,
            f"{self!r} / {converted!r} = "
            f"({self.p!r}{converted.q!r}) / "
            f"({self.q!r}{converted.p!r})",
        )

    def __rtruediv__(self, other: object) -> Rational | Any:
        converted = _coerce_rational(other)
        if converted is None:
            return NotImplemented
        return converted / self

    @log(log_level=26)
    def __pow__(self, exponent: object) -> tuple[Rational | Any, str]:
        if not isinstance(exponent, NaturalNumber):
            return NotImplemented, f"{self!r} ** {exponent!r} = NotImplemented"
        if exponent == N_ZERO:
            return Q_ONE, f"{self!r} ** {exponent!r} = {Q_ONE!r}"
        return (
            (self ** (exponent - N_ONE)) * self,
            f"{self!r} ** {exponent!r} = "
            f"({self!r} ** ({exponent!r} - {N_ONE!r})) * {self!r}",
        )

    def __bool__(self) -> bool:
        return self.p != Z_ZERO

    def __hash__(self) -> int:
        reduced = self.reduction()
        if reduced.q == Z_ONE:
            # NaturalNumber / Integer と等しい値は同じ hash を持つ。
            return hash(reduced.p)
        return hash(("Rational", int(reduced.p), int(reduced.q)))

    def __pos__(self) -> Rational:
        return self

    def __abs__(self) -> Rational:
        return Rational(Integer(abs(self.p), N_ZERO), Integer(abs(self.q), N_ZERO))

    def as_integer_ratio(self) -> tuple[int, int]:
        """既約で分母が正の Python 整数比を返す。

        大きな有理数を表示・検査するとき、同値な巨大 Peano 中間値を
        作らずに正規形を取得するための境界APIでもある。
        """

        from math import gcd

        numerator, denominator = int(self.p), int(self.q)
        if denominator < 0:
            numerator, denominator = -numerator, -denominator
        divisor = gcd(abs(numerator), denominator)
        return numerator // divisor, denominator // divisor

    def reduction(self) -> Rational:
        """分母を正にし、最大公約数で割った代表元を返す。"""

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
    """2つの Python 整数から有理数を構成する。"""

    return Rational(integer(numerator), integer(denominator))


def n2r(value: NaturalNumber) -> Rational:
    """自然数を有理数へ埋め込む。"""

    if not isinstance(value, NaturalNumber):
        raise TypeError("n2r の引数は NaturalNumber でなければなりません")
    return Rational(n2z(value), Z_ONE)


def z2r(value: Integer) -> Rational:
    """整数を有理数へ埋め込む。"""

    if not isinstance(value, Integer):
        raise TypeError("z2r の引数は Integer でなければなりません")
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
    """NaturalNumber / Integer / Rational を Rational に変換する。"""

    converted = _coerce_rational(value)
    if converted is None:
        raise TypeError(f"{value!r} is not a Rational")
    return converted


Q_ZERO = Rational(Z_ZERO, Z_ONE)
Q_ONE = Rational(Z_ONE, Z_ONE)
Q_MINUS_ONE = Rational(-Z_ONE, Z_ONE)
