"""0 と後者だけから自然数とその演算を構成する。"""

from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering
from typing import Any, Iterator

from .utils import log


@total_ordering
@dataclass(frozen=True, slots=True, eq=False, repr=False)
class NaturalNumber:
    """Peano 公理に基づく自然数。

    ``None`` が 0、``NaturalNumber(n)`` が後者 :math:`S(n)` を表す。
    値は不変であり、加法と乗法は Peano の再帰的定義をそのまま実装する。
    """

    pre: NaturalNumber | None = None

    def __post_init__(self) -> None:
        if self.pre is not None and not isinstance(self.pre, NaturalNumber):
            raise TypeError("pre は NaturalNumber または None でなければなりません")

    def __repr__(self) -> str:
        return f"<N({int(self)})>"

    def __str__(self) -> str:
        return str(int(self))

    def __int__(self) -> int:
        value = 0
        current: NaturalNumber | None = self
        while current is not None and current.pre is not None:
            value += 1
            current = current.pre
        return value

    @log(log_level=1)
    def __eq__(self, other: object) -> tuple[bool | Any, str]:
        if not isinstance(other, NaturalNumber):
            return NotImplemented, f"{self!r} == {other!r} = NotImplemented"
        if self.pre is None or other.pre is None:
            result = self.pre is None and other.pre is None
            return result, f"{self!r} == {other!r} = {result}"
        return (
            self.pre == other.pre,
            f"{self!r} == {other!r} = {self.pre!r} == {other.pre!r}",
        )

    @log(log_level=2)
    def __lt__(self, other: object) -> tuple[bool | Any, str]:
        if not isinstance(other, NaturalNumber):
            return NotImplemented, f"{self!r} < {other!r} = NotImplemented"
        if self.pre is None:
            result = other.pre is not None
            return result, f"{self!r} < {other!r} = {result}"
        if other.pre is None:
            return False, f"{self!r} < {other!r} = False"
        return (
            self.pre < other.pre,
            f"{self!r} < {other!r} = {self.pre!r} < {other.pre!r}",
        )

    @log(log_level=2)
    def __le__(self, other: object) -> tuple[bool | Any, str]:
        if not isinstance(other, NaturalNumber):
            return NotImplemented, f"{self!r} <= {other!r} = NotImplemented"
        if self.pre is None:
            return True, f"{self!r} <= {other!r} = True"
        if other.pre is None:
            return False, f"{self!r} <= {other!r} = False"
        return (
            self.pre <= other.pre,
            f"{self!r} <= {other!r} = {self.pre!r} <= {other.pre!r}",
        )

    @log(log_level=4)
    def __add__(self, other: object) -> tuple[NaturalNumber | Any, str]:
        if not isinstance(other, NaturalNumber):
            return NotImplemented, f"{self!r} + {other!r} = NotImplemented"
        if other.pre is None:
            return self, f"{self!r} + {other!r} = {self!r}"
        return (
            successor(self + other.pre),
            f"{self!r} + S({other.pre!r}) = S({self!r} + {other.pre!r})",
        )

    @log(log_level=4)
    def __sub__(self, other: object) -> tuple[NaturalNumber | Any, str]:
        if not isinstance(other, NaturalNumber):
            return NotImplemented, f"{self!r} - {other!r} = NotImplemented"
        if other.pre is None:
            return self, f"{self!r} - {other!r} = {self!r}"
        if self.pre is None:
            raise ValueError("自然数の減算結果を負にはできません")
        return (
            self.pre - other.pre,
            f"{self!r} - {other!r} = {self.pre!r} - {other.pre!r}",
        )

    @log(log_level=5)
    def __mul__(self, other: object) -> tuple[NaturalNumber | Any, str]:
        if not isinstance(other, NaturalNumber):
            return NotImplemented, f"{self!r} * {other!r} = NotImplemented"
        if other.pre is None:
            return N_ZERO, f"{self!r} * {other!r} = {N_ZERO!r}"
        return (
            self + self * other.pre,
            f"{self!r} * S({other.pre!r}) = {self!r} + ({self!r} * {other.pre!r})",
        )

    @log(log_level=5)
    def __truediv__(self, other: object) -> tuple[Any, str]:
        if not isinstance(other, NaturalNumber):
            return NotImplemented, f"{self!r} / {other!r} = NotImplemented"
        if other.pre is None:
            raise ZeroDivisionError("0 で割ることはできません")
        from .integer import Integer
        from .rational import Rational

        result = Rational(Integer(self, N_ZERO), Integer(other, N_ZERO))
        return result, f"{self!r} / {other!r} = {result!r}"

    @log(log_level=5)
    def __floordiv__(self, other: object) -> tuple[NaturalNumber | Any, str]:
        if not isinstance(other, NaturalNumber):
            return NotImplemented, f"{self!r} // {other!r} = NotImplemented"
        if not other:
            raise ZeroDivisionError("0 で割ることはできません")
        if self < other:
            return N_ZERO, f"{self!r} // {other!r} = {N_ZERO!r}"
        return (
            N_ONE + ((self - other) // other),
            f"{self!r} // {other!r} = "
            f"{N_ONE!r} + (({self!r} - {other!r}) // {other!r})",
        )

    @log(log_level=5)
    def __mod__(self, other: object) -> tuple[NaturalNumber | Any, str]:
        if not isinstance(other, NaturalNumber):
            return NotImplemented, f"{self!r} % {other!r} = NotImplemented"
        if not other:
            raise ZeroDivisionError("0 で割ることはできません")
        if self < other:
            return self, f"{self!r} % {other!r} = {self!r}"
        return (
            (self - other) % other,
            f"{self!r} % {other!r} = ({self!r} - {other!r}) % {other!r}",
        )

    def __divmod__(self, other: object) -> tuple[NaturalNumber, NaturalNumber] | Any:
        if not isinstance(other, NaturalNumber):
            return NotImplemented
        return self // other, self % other

    @log(log_level=6)
    def __pow__(self, exponent: object) -> tuple[NaturalNumber | Any, str]:
        if not isinstance(exponent, NaturalNumber):
            return NotImplemented, f"{self!r} ** {exponent!r} = NotImplemented"
        if exponent.pre is None:
            return N_ONE, f"{self!r} ** {exponent!r} = {N_ONE!r}"
        return (
            (self**exponent.pre) * self,
            f"{self!r} ** S({exponent.pre!r}) = "
            f"({self!r} ** {exponent.pre!r}) * {self!r}",
        )

    def __bool__(self) -> bool:
        return self.pre is not None

    def __hash__(self) -> int:
        return hash(int(self))

    def __pos__(self) -> NaturalNumber:
        return self

    def __neg__(self) -> Any:
        from .integer import Integer

        return Integer(N_ZERO, self)

    def __abs__(self) -> NaturalNumber:
        return self

    def __iter__(self) -> Iterator[NaturalNumber]:
        current = N_ZERO
        while current != self:
            yield current
            current = successor(current)

    def __reversed__(self) -> Iterator[NaturalNumber]:
        current = self
        while current.pre is not None:
            current = current.pre
            yield current

    def set_repr(self) -> frozenset[Any]:
        """フォン・ノイマン順序数としての集合表示を返す。"""

        if self.pre is None:
            return frozenset()
        predecessor = self.pre.set_repr()
        return frozenset((predecessor,)) | predecessor

    def set_str(self) -> str:
        return (
            str(self.set_repr())
            .replace("{", "")
            .replace("}", "")
            .replace("frozenset(", "{")
            .replace(")", "}")
        )


def successor(number: NaturalNumber) -> NaturalNumber:
    """後者 :math:`S(n)` を返す。"""

    if not isinstance(number, NaturalNumber):
        raise TypeError("successor の引数は NaturalNumber でなければなりません")
    return NaturalNumber(number)


def natural_number(value: int) -> NaturalNumber:
    """Python の非負整数を、0 から後者を重ねて構成する。"""

    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("自然数へ変換できるのは int だけです")
    if value < 0:
        raise ValueError("負の値は自然数に変換できません")
    result = N_ZERO
    for _ in range(value):
        result = successor(result)
    return result


def cast2n(value: object) -> NaturalNumber:
    """NaturalNumber であることを検証する。"""

    if not isinstance(value, NaturalNumber):
        raise TypeError(f"{value!r} is not a NaturalNumber")
    return value


N_ZERO = NaturalNumber()
N_ONE = NaturalNumber(N_ZERO)
