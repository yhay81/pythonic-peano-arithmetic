"""有理数では表せない根を、有理区間の縮小として観察する。"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .natural_number import NaturalNumber
from .polynomial import Polynomial, count_real_roots
from .rational import Rational, rational
from .utils import log


@dataclass(frozen=True, slots=True)
class RationalInterval:
    """2つの有理数からなる閉区間。

    同じ端点を許し、その場合は厳密な有理数一点を表す。
    """

    lower: Rational
    upper: Rational

    def __post_init__(self) -> None:
        if not isinstance(self.lower, Rational) or not isinstance(self.upper, Rational):
            raise TypeError("区間の端点は Rational でなければなりません")
        lower_fraction = _as_fraction(self.lower)
        upper_fraction = _as_fraction(self.upper)
        if lower_fraction > upper_fraction:
            raise ValueError("lower は upper 以下でなければなりません")
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
    """多項式の1つの実根を分離区間で指定する教材用オブジェクト。

    これは実数の完全な数値型ではない。四則演算や厳密な等号は提供せず、
    有理数だけを使って区間が縮む過程を観察することに責務を絞る。
    """

    polynomial: Polynomial
    interval: RationalInterval

    def __post_init__(self) -> None:
        if not isinstance(self.polynomial, Polynomial):
            raise TypeError("polynomial は Polynomial でなければなりません")
        if not isinstance(self.interval, RationalInterval):
            raise TypeError("interval は RationalInterval でなければなりません")
        if self.polynomial.degree <= 0:
            raise ValueError("根を指定する多項式は1次以上でなければなりません")
        if self.interval.is_point:
            raise ValueError("初期区間には正の幅が必要です")

        lower_sign = self.polynomial.sign_at(self.interval.lower)
        upper_sign = self.polynomial.sign_at(self.interval.upper)
        if lower_sign == 0 or upper_sign == 0:
            raise ValueError("初期区間の端点を根にはできません")
        if lower_sign == upper_sign:
            raise ValueError("端点で多項式の符号が変わる区間を指定してください")

        number_of_roots = count_real_roots(
            self.polynomial,
            self.interval.lower,
            self.interval.upper,
        )
        if number_of_roots != 1:
            raise ValueError(
                "初期区間には相異なる実根がちょうど1つ必要です"
                f"（検出数: {number_of_roots}）"
            )

    def approximate(self, steps: int | NaturalNumber) -> RationalInterval:
        """二分法を ``steps`` 回行い、根を含む閉区間を返す。"""

        count = _step_count(steps)
        interval = self.interval
        for _ in range(count):
            if interval.is_point:
                break
            interval = _bisect(self.polynomial, interval)
        return interval

    def trace(self, steps: int | NaturalNumber) -> tuple[RationalInterval, ...]:
        """初期区間を含む、二分法の全区間を返す。"""

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
) -> tuple[RationalInterval, str]:
    midpoint = interval.midpoint
    midpoint_sign = polynomial_value.sign_at(midpoint)

    if midpoint_sign == 0:
        result = RationalInterval(midpoint, midpoint)
        return (
            result,
            f"{polynomial_value!r}: midpoint {midpoint!r} is an exact root",
        )

    lower_sign = polynomial_value.sign_at(interval.lower)
    if lower_sign != midpoint_sign:
        result = RationalInterval(interval.lower, midpoint)
    else:
        result = RationalInterval(midpoint, interval.upper)
    return (
        result,
        f"{polynomial_value!r}: {interval} -> {result}",
    )


def algebraic_root(
    polynomial_value: Polynomial,
    lower: tuple[int, int],
    upper: tuple[int, int],
) -> AlgebraicRoot:
    """Python 整数の組で端点を指定する簡便な生成関数。"""

    return AlgebraicRoot(
        polynomial_value,
        RationalInterval(rational(*lower), rational(*upper)),
    )


def _step_count(value: int | NaturalNumber) -> int:
    if isinstance(value, NaturalNumber):
        return int(value)
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("steps は int または NaturalNumber で指定してください")
    if value < 0:
        raise ValueError("steps は 0 以上でなければなりません")
    return value


def _as_fraction(value: Rational) -> Fraction:
    return Fraction(int(value.p), int(value.q))


def _from_fraction(value: Fraction) -> Rational:
    return rational(value.numerator, value.denominator)
