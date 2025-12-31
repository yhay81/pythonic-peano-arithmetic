from typing import Any, Optional

from .utils import log


class NaturalNumber:
    """Peano 公理に基づく自然数。

    数学定義: 0 と後者 S(n) で生成される集合。
    停止条件: 再帰は `pre is None` (0) に到達したときに止まる。
    `pre` は前者を表し、`None` が 0 に対応する。
    """

    def __init__(self, pre: Optional["NaturalNumber"] = None) -> None:
        self._pre = pre
        self._repr = repr(self)  # for chaching

    @property
    def pre(self) -> Optional["NaturalNumber"]:
        return self._pre

    def __repr__(self) -> str:
        if not hasattr(self, "_repr"):
            self._repr = f"<N({str(self)})>"
        return self._repr

    def __str__(self) -> str:
        return str(int(self))

    def __int__(self) -> int:
        if self.pre is None:
            return 0
        else:
            return int(self.pre) + 1

    @log(log_level=1)
    def __eq__(self, x: object) -> tuple[bool, str]:
        if not isinstance(x, NaturalNumber):
            return NotImplemented, f"{repr(self)} == {repr(x)} = NotImplemented"
        x = cast2n(x)
        formula = f"{repr(self)} == {repr(x)} = {repr(self)}.pre == {repr(x)}.pre = {repr(self.pre)} == {repr(x.pre)}"
        if self.pre is None and x.pre is None:
            return (
                True,
                f"{formula} = True",
            )
        elif (self.pre is None and x.pre is not None) or (
            self.pre is not None and x.pre is None
        ):
            return (
                False,
                f"{formula} = False",
            )
        else:
            return self.pre == x.pre, formula

    @log(log_level=2)
    def __le__(self, x: object) -> tuple[bool, str]:
        if not isinstance(x, NaturalNumber):
            return NotImplemented, f"{repr(self)} <= {repr(x)} = NotImplemented"
        x = cast2n(x)
        formula = f"{repr(self)} <= {repr(x)} = {repr(self)}.pre <= {repr(x)}.pre = {repr(self.pre)} <= {repr(x.pre)}"
        if self.pre is None:
            return True, f"{formula} = True"
        elif x.pre is None:
            return False, f"{formula} = False"
        else:
            return self.pre <= x.pre, formula

    @log(log_level=3)
    def __lt__(self, x: object) -> tuple[bool, str]:
        if not isinstance(x, NaturalNumber):
            return NotImplemented, f"{repr(self)} < {repr(x)} = NotImplemented"
        x = cast2n(x)
        return (
            self <= x and self != x,
            f"{repr(self)} <= {repr(x)} and {repr(self)} != {repr(x)}",
        )

    @log(log_level=4)
    def __add__(self, x: object) -> tuple["NaturalNumber", str]:
        x = cast2n(x)
        formula = f"{repr(self)} + {repr(x)}"
        if x.pre is None:
            return self, f"{formula} = {repr(self)}"
        else:
            return (
                NaturalNumber(self + x.pre),
                f"{formula} = NaturalNumber(pre={repr(self)} + {repr(x.pre)})",
            )

    @log(log_level=4)
    def __sub__(self, x: object) -> tuple["NaturalNumber", str]:
        x = cast2n(x)
        formula = f"{repr(self)} - {repr(x)}"
        if x.pre is None:
            return self, f"{formula} = {repr(self)}"
        elif self.pre is None:
            raise ValueError
        else:
            return self.pre - x.pre, f"{formula} = {repr(self.pre)} - {repr(x.pre)}"

    @log(log_level=5)
    def __mul__(self, x: object) -> tuple["NaturalNumber", str]:
        x = cast2n(x)
        formula = f"{repr(self)} * {repr(x)}"
        if x.pre is None:
            return N_ZERO, f"{formula} = {repr(N_ZERO)}"
        else:
            return (
                self + self * x.pre,
                f"{formula} = {repr(self)} + {repr(self)} * {repr(x)}.pre"
                f" = {repr(self)} + {repr(self)} * {repr(x.pre)}",
            )

    @log(log_level=5)
    def __truediv__(self, x: object) -> tuple[Any, str]:
        x = cast2n(x)
        if x.pre is None:
            raise ZeroDivisionError
        formula = f"{repr(self)} / {repr(x)}"
        from .integer import Integer
        from .rational import Rational

        return (
            Rational(Integer(self, N_ZERO), Integer(x, N_ZERO)),
            f"{formula} = Rational(Integer({repr(self)}, {repr(N_ZERO)}), Integer({repr(x)}, {repr(N_ZERO)}))",
        )

    @log(log_level=5)
    def __floordiv__(self, x: object) -> tuple["NaturalNumber", str]:
        x = cast2n(x)
        formula = f"{repr(self)} // {repr(x)}"
        if x.pre is None:
            raise ZeroDivisionError
        if self < x:
            return (
                N_ZERO,
                f"{formula} = {repr(N_ZERO)}",
            )
        else:
            return (
                N_ONE + ((self - x) // x),
                f"{formula} = {repr(N_ONE)} + (({repr(self)} - {repr(x)}) // {repr(x)})",
            )

    @log(log_level=5)
    def __mod__(self, x: object) -> tuple["NaturalNumber", str]:
        x = cast2n(x)
        formula = f"{repr(self)} % {repr(x)}"
        if x.pre is None:
            raise ZeroDivisionError
        if self < x:
            return self, f"{formula} = {repr(self)}"
        else:
            return (self - x) % x, f"{formula} = ({repr(self)} - {repr(x)}) % {repr(x)}"

    @log(log_level=5)
    def __divmod__(
        self, x: object
    ) -> tuple[tuple["NaturalNumber", "NaturalNumber"], str]:
        x = cast2n(x)
        return (
            self // x,
            self % x,
        ), f"{repr(self)} // {repr(x)}, {repr(self)} % {repr(x)}"

    @log(log_level=6)
    def __pow__(self, x: object) -> tuple["NaturalNumber", str]:
        x = cast2n(x)
        formula = f"{repr(self)} ** {repr(x)}"
        if x.pre is None:
            return (
                N_ONE,
                f"{formula} = {repr(N_ONE)}",
            )
        else:
            return (
                (self ** (x.pre)) * self,
                f"{formula} = {repr(self)} * {repr(self)} ** {repr(x.pre)}",
            )

    def __bool__(self) -> bool:
        return self.pre is not None

    def __hash__(self) -> int:
        return int(self)

    def __pos__(self) -> "NaturalNumber":
        return self

    def __neg__(self) -> Any:
        from .integer import Integer

        return Integer(N_ZERO, self)

    def __abs__(self) -> "NaturalNumber":
        return self

    def __iter__(self) -> "NaturalNumberIterator":
        return NaturalNumberIterator(self)

    def __reversed__(self) -> "NaturalNumberReversedIterator":
        return NaturalNumberReversedIterator(self)

    def set_repr(self) -> frozenset[Any]:
        if self.pre is None:
            return frozenset()
        else:
            preset = self.pre.set_repr()
            return frozenset((preset,)) | preset

    def set_str(self) -> str:
        return (
            str(self.set_repr())
            .replace("{", "")
            .replace("}", "")
            .replace("frozenset(", "{")
            .replace(")", "}")
        )


class NaturalNumberIterator:
    """0 から n-1 までを順に返すイテレータ。"""

    def __init__(self, n: NaturalNumber) -> None:
        self._i = N_ZERO
        self.n = n

    def __iter__(self) -> "NaturalNumberIterator":
        return self

    def __next__(self) -> NaturalNumber:
        if self._i == self.n:
            raise StopIteration()
        else:
            i = self._i
            self._i = NaturalNumber(self._i)
            return i


class NaturalNumberReversedIterator:
    """n-1 から 0 までを逆順に返すイテレータ。"""

    def __init__(self, n: NaturalNumber) -> None:
        self._i = n
        self.n = n

    def __iter__(self) -> "NaturalNumberReversedIterator":
        return self

    def __next__(self) -> NaturalNumber:
        if self._i.pre is None:
            raise StopIteration()
        else:
            self._i = self._i.pre
            return self._i


def successor(n: NaturalNumber) -> NaturalNumber:
    """後者関数 S(n) を返す。"""

    return NaturalNumber(n)


def natural_number(k: int) -> NaturalNumber:
    """Python の int から自然数を構成する。"""

    if k < 0:
        raise ValueError("負の値は自然数に変換できません")
    return N_ZERO if k == 0 else NaturalNumber(natural_number(k - 1))


def cast2n(x: object) -> NaturalNumber:
    """NaturalNumber への型変換を強制する。"""

    if not isinstance(x, NaturalNumber):
        raise TypeError(f"{repr(x)} is not an NaturalNumber, but {type(x)}")
    return x


N_ZERO = NaturalNumber()
N_ONE = NaturalNumber(N_ZERO)
