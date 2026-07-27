"""自然数の差の同値類として整数を構成する。"""

from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering
from typing import Any

from .natural_number import N_ONE, N_ZERO, NaturalNumber, natural_number
from .utils import log


@total_ordering
@dataclass(frozen=True, slots=True, eq=False, repr=False)
class Integer:
    """自然数の対 ``(a, b)`` で差 ``a - b`` を表す。

    ``(a, b) ~ (c, d)`` は ``a + d = b + c`` で定義する。表現をあえて
    自動正規化しないため、同じ整数に複数の表現があることを観察できる。
    """

    a: NaturalNumber
    b: NaturalNumber

    def __post_init__(self) -> None:
        if not isinstance(self.a, NaturalNumber) or not isinstance(
            self.b, NaturalNumber
        ):
            raise TypeError("Integer の a と b は NaturalNumber でなければなりません")

    def __repr__(self) -> str:
        return f"<Z({int(self.a)},{int(self.b)})>"

    def __str__(self) -> str:
        return str(int(self))

    def __int__(self) -> int:
        return int(self.a) - int(self.b)

    def __abs__(self) -> NaturalNumber:
        if self.a >= self.b:
            return self.a - self.b
        return self.b - self.a

    @log(log_level=11)
    def __eq__(self, other: object) -> tuple[bool | Any, str]:
        converted = _coerce_integer(other)
        if converted is None:
            return NotImplemented, f"{self!r} == {other!r} = NotImplemented"
        result = self.a + converted.b == self.b + converted.a
        return (
            result,
            f"{self!r} == {converted!r} iff "
            f"{self.a!r} + {converted.b!r} == "
            f"{self.b!r} + {converted.a!r}",
        )

    @log(log_level=12)
    def __lt__(self, other: object) -> tuple[bool | Any, str]:
        converted = _coerce_integer(other)
        if converted is None:
            return NotImplemented, f"{self!r} < {other!r} = NotImplemented"
        result = self.a + converted.b < self.b + converted.a
        return (
            result,
            f"{self!r} < {converted!r} iff "
            f"{self.a!r} + {converted.b!r} < "
            f"{self.b!r} + {converted.a!r}",
        )

    @log(log_level=12)
    def __le__(self, other: object) -> tuple[bool | Any, str]:
        converted = _coerce_integer(other)
        if converted is None:
            return NotImplemented, f"{self!r} <= {other!r} = NotImplemented"
        result = self.a + converted.b <= self.b + converted.a
        return (
            result,
            f"{self!r} <= {converted!r} iff "
            f"{self.a!r} + {converted.b!r} <= "
            f"{self.b!r} + {converted.a!r}",
        )

    @log(log_level=14)
    def __add__(self, other: object) -> tuple[Integer | Any, str]:
        converted = _coerce_integer(other)
        if converted is None:
            return NotImplemented, f"{self!r} + {other!r} = NotImplemented"
        result = Integer(self.a + converted.a, self.b + converted.b)
        return (
            result,
            f"{self!r} + {converted!r} = "
            f"({self.a!r} + {converted.a!r}, "
            f"{self.b!r} + {converted.b!r})",
        )

    def __radd__(self, other: object) -> Integer | Any:
        return self + other

    @log(log_level=14)
    def __neg__(self) -> tuple[Integer, str]:
        return Integer(self.b, self.a), f"-{self!r} = ({self.b!r}, {self.a!r})"

    @log(log_level=14)
    def __sub__(self, other: object) -> tuple[Integer | Any, str]:
        converted = _coerce_integer(other)
        if converted is None:
            return NotImplemented, f"{self!r} - {other!r} = NotImplemented"
        return (
            self + -converted,
            f"{self!r} - {converted!r} = {self!r} + (-{converted!r})",
        )

    def __rsub__(self, other: object) -> Integer | Any:
        converted = _coerce_integer(other)
        if converted is None:
            return NotImplemented
        return converted - self

    @log(log_level=15)
    def __mul__(self, other: object) -> tuple[Integer | Any, str]:
        converted = _coerce_integer(other)
        if converted is None:
            return NotImplemented, f"{self!r} * {other!r} = NotImplemented"
        result = Integer(
            self.a * converted.a + self.b * converted.b,
            self.a * converted.b + self.b * converted.a,
        )
        return (
            result,
            f"{self!r} * {converted!r} = "
            f"({self.a!r}{converted.a!r} + {self.b!r}{converted.b!r}, "
            f"{self.a!r}{converted.b!r} + {self.b!r}{converted.a!r})",
        )

    def __rmul__(self, other: object) -> Integer | Any:
        return self * other

    @log(log_level=15)
    def __truediv__(self, other: object) -> tuple[Any, str]:
        converted = _coerce_integer(other)
        if converted is None:
            return NotImplemented, f"{self!r} / {other!r} = NotImplemented"
        from .rational import Rational

        result = Rational(self, converted)
        return result, f"{self!r} / {converted!r} = {result!r}"

    def __rtruediv__(self, other: object) -> Any:
        converted = _coerce_integer(other)
        if converted is None:
            return NotImplemented
        return converted / self

    def _divmod(self, divisor: Integer) -> tuple[Integer, Integer]:
        if not divisor:
            raise ZeroDivisionError("0 で割ることはできません")

        quotient_magnitude, remainder_magnitude = divmod(abs(self), abs(divisor))
        same_sign = (self < Z_ZERO) == (divisor < Z_ZERO)

        if same_sign:
            quotient = Integer(quotient_magnitude, N_ZERO)
            remainder = Integer(remainder_magnitude, N_ZERO)
        elif not remainder_magnitude:
            quotient = Integer(N_ZERO, quotient_magnitude)
            remainder = Z_ZERO
        else:
            quotient = Integer(N_ZERO, quotient_magnitude + N_ONE)
            remainder = Integer(abs(divisor) - remainder_magnitude, N_ZERO)

        if divisor < Z_ZERO:
            remainder = -remainder
        return quotient, remainder

    @log(log_level=15)
    def __floordiv__(self, other: object) -> tuple[Integer | Any, str]:
        converted = _coerce_integer(other)
        if converted is None:
            return NotImplemented, f"{self!r} // {other!r} = NotImplemented"
        quotient, _ = self._divmod(converted)
        return (
            quotient,
            f"{self!r} = ({quotient!r}) * {converted!r} + ({self!r} % {converted!r})",
        )

    def __rfloordiv__(self, other: object) -> Integer | Any:
        converted = _coerce_integer(other)
        if converted is None:
            return NotImplemented
        return converted // self

    @log(log_level=15)
    def __mod__(self, other: object) -> tuple[Integer | Any, str]:
        converted = _coerce_integer(other)
        if converted is None:
            return NotImplemented, f"{self!r} % {other!r} = NotImplemented"
        _, remainder = self._divmod(converted)
        return (
            remainder,
            f"{self!r} % {converted!r} = {remainder!r}, "
            f"sign(remainder) = sign({converted!r})",
        )

    def __rmod__(self, other: object) -> Integer | Any:
        converted = _coerce_integer(other)
        if converted is None:
            return NotImplemented
        return converted % self

    def __divmod__(self, other: object) -> tuple[Integer, Integer] | Any:
        converted = _coerce_integer(other)
        if converted is None:
            return NotImplemented
        return self._divmod(converted)

    def __rdivmod__(self, other: object) -> tuple[Integer, Integer] | Any:
        converted = _coerce_integer(other)
        if converted is None:
            return NotImplemented
        return converted._divmod(self)

    @log(log_level=16)
    def __pow__(self, exponent: object) -> tuple[Integer | Any, str]:
        if not isinstance(exponent, NaturalNumber):
            return NotImplemented, f"{self!r} ** {exponent!r} = NotImplemented"
        if exponent == N_ZERO:
            return Z_ONE, f"{self!r} ** {exponent!r} = {Z_ONE!r}"
        return (
            (self ** (exponent - N_ONE)) * self,
            f"{self!r} ** {exponent!r} = "
            f"({self!r} ** ({exponent!r} - {N_ONE!r})) * {self!r}",
        )

    def __bool__(self) -> bool:
        return self.a != self.b

    def __hash__(self) -> int:
        return hash(int(self))

    def __pos__(self) -> Integer:
        return self

    def normalize(self) -> Integer:
        """同値類の代表を ``(n, 0)`` または ``(0, n)`` にする。"""

        if self.a >= self.b:
            return Integer(self.a - self.b, N_ZERO)
        return Integer(N_ZERO, self.b - self.a)


def integer(value: int) -> Integer:
    """Python の整数から標準的な差の表現を構成する。"""

    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("整数へ変換できるのは int だけです")
    if value >= 0:
        return Integer(natural_number(value), N_ZERO)
    return Integer(N_ZERO, natural_number(-value))


def n2z(value: NaturalNumber) -> Integer:
    """自然数を整数へ埋め込む。"""

    if not isinstance(value, NaturalNumber):
        raise TypeError("n2z の引数は NaturalNumber でなければなりません")
    return Integer(value, N_ZERO)


def _coerce_integer(value: object) -> Integer | None:
    if isinstance(value, NaturalNumber):
        return n2z(value)
    if isinstance(value, Integer):
        return value
    return None


def cast2z(value: object) -> Integer:
    """NaturalNumber または Integer を Integer に変換する。"""

    converted = _coerce_integer(value)
    if converted is None:
        raise TypeError(f"{value!r} is not an Integer")
    return converted


Z_ZERO = Integer(N_ZERO, N_ZERO)
Z_ONE = Integer(N_ONE, N_ZERO)
Z_MINUS_ONE = Integer(N_ZERO, N_ONE)
