"""有理数係数多項式と、実根を調べるための最小限の道具。"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import total_ordering
from itertools import zip_longest
from typing import Any, Iterator

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
from .utils import log


@total_ordering
@dataclass(frozen=True, slots=True, init=False, eq=False, repr=False)
class Polynomial:
    """有理数係数の有限列 ``(a0, ..., an)`` を多項式とみなす。

    係数は定数項から昇順に並ぶ。末尾の 0 は取り除き、係数を既約化するため、
    0 多項式を含めて表現は一意になる。
    """

    _coefficients: tuple[Rational, ...]

    def __init__(self, *coefficients: Rational) -> None:
        if not coefficients:
            coefficients = (Q_ZERO,)
        if any(not isinstance(value, Rational) for value in coefficients):
            raise TypeError("Polynomial の係数は Rational でなければなりません")

        normalized = [value.reduction() for value in coefficients]
        while len(normalized) > 1 and normalized[-1] == Q_ZERO:
            normalized.pop()
        object.__setattr__(self, "_coefficients", tuple(normalized))

    @property
    def k(self) -> tuple[Rational, ...]:
        """従来APIと同じ係数列。"""

        return self._coefficients

    @property
    def coefficients(self) -> tuple[Rational, ...]:
        return self._coefficients

    @property
    def degree(self) -> int:
        """次数を返す。0 多項式の次数は便宜上 -1 とする。"""

        return -1 if not self else len(self.coefficients) - 1

    @property
    def leading_coefficient(self) -> Rational:
        if not self:
            raise ValueError("0 多項式には最高次係数がありません")
        return self.coefficients[-1]

    def __eq__(self, other: object) -> bool | Any:
        converted = _coerce_polynomial(other)
        if converted is None:
            return NotImplemented
        return self.coefficients == converted.coefficients

    def _order_key(self) -> tuple[Any, ...]:
        return (self.degree, *reversed(self.coefficients))

    def __lt__(self, other: object) -> bool | Any:
        converted = _coerce_polynomial(other)
        if converted is None:
            return NotImplemented
        return self._order_key() < converted._order_key()

    def __le__(self, other: object) -> bool | Any:
        converted = _coerce_polynomial(other)
        if converted is None:
            return NotImplemented
        return self._order_key() <= converted._order_key()

    def __add__(self, other: object) -> Polynomial | Any:
        converted = _coerce_polynomial(other)
        if converted is None:
            return NotImplemented
        coefficients = [
            a + b
            for a, b in zip_longest(
                self.coefficients,
                converted.coefficients,
                fillvalue=Q_ZERO,
            )
        ]
        return Polynomial(*coefficients)

    def __radd__(self, other: object) -> Polynomial | Any:
        return self + other

    def __neg__(self) -> Polynomial:
        return Polynomial(*(-coefficient for coefficient in self))

    def __sub__(self, other: object) -> Polynomial | Any:
        converted = _coerce_polynomial(other)
        if converted is None:
            return NotImplemented
        return self + -converted

    def __rsub__(self, other: object) -> Polynomial | Any:
        converted = _coerce_polynomial(other)
        if converted is None:
            return NotImplemented
        return converted - self

    def __mul__(self, other: object) -> Polynomial | Any:
        converted = _coerce_polynomial(other)
        if converted is None:
            return NotImplemented
        if not self or not converted:
            return P_ZERO
        result = [Q_ZERO] * (len(self.coefficients) + len(converted.coefficients) - 1)
        for i, left in enumerate(self.coefficients):
            for j, right in enumerate(converted.coefficients):
                product = (left * right).reduction()
                result[i + j] = (result[i + j] + product).reduction()
        return Polynomial(*result)

    def __rmul__(self, other: object) -> Polynomial | Any:
        return self * other

    def __divmod__(self, other: object) -> tuple[Polynomial, Polynomial] | Any:
        divisor = _coerce_polynomial(other)
        if divisor is None:
            return NotImplemented
        if not divisor:
            raise ZeroDivisionError("0 多項式で割ることはできません")
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

    def __rdivmod__(self, other: object) -> tuple[Polynomial, Polynomial] | Any:
        dividend = _coerce_polynomial(other)
        if dividend is None:
            return NotImplemented
        return divmod(dividend, self)

    def __floordiv__(self, other: object) -> Polynomial | Any:
        divisor = _coerce_polynomial(other)
        if divisor is None:
            return NotImplemented
        result = self.__divmod__(divisor)
        quotient, _ = result
        return quotient

    def __rfloordiv__(self, other: object) -> Polynomial | Any:
        dividend = _coerce_polynomial(other)
        if dividend is None:
            return NotImplemented
        return dividend // self

    def __mod__(self, other: object) -> Polynomial | Any:
        divisor = _coerce_polynomial(other)
        if divisor is None:
            return NotImplemented
        result = self.__divmod__(divisor)
        _, remainder = result
        return remainder

    def __rmod__(self, other: object) -> Polynomial | Any:
        dividend = _coerce_polynomial(other)
        if dividend is None:
            return NotImplemented
        return dividend % self

    def __pow__(self, exponent: object) -> Polynomial | Any:
        if not isinstance(exponent, NaturalNumber):
            return NotImplemented
        if exponent == N_ZERO:
            return P_ONE
        return (self ** (exponent - N_ONE)) * self

    @log(log_level=31)
    def evaluate(self, value: object) -> tuple[Rational, str]:
        """Horner 法で ``x=value`` における値を計算する。"""

        point = cast2r(value)
        result = Q_ZERO
        for coefficient in reversed(self.coefficients):
            result = (result * point + coefficient).reduction()
        return result, f"{self!r} at x={point!r} = {result!r}"

    def sign_at(self, value: object) -> int:
        """点での値の符号を ``-1, 0, 1`` で厳密に返す。

        根の反復近似では分母が指数的に大きくなる。符号だけを知るために
        Peano 表現の巨大な中間分母を構成する必要はないため、同じ整数比を
        Python の任意精度整数へ写し、Horner 法で厳密に判定する。
        """

        point = _as_fraction(cast2r(value))
        result = Fraction(0)
        for coefficient in reversed(self.coefficients):
            result = result * point + _as_fraction(coefficient)
        return (result > 0) - (result < 0)

    def derivative(self) -> Polynomial:
        """形式微分を返す。"""

        if self.degree <= 0:
            return P_ZERO
        return Polynomial(
            *(
                coefficient * rational(power, 1)
                for power, coefficient in enumerate(self.coefficients[1:], start=1)
            )
        )

    def monic(self) -> Polynomial:
        """最高次係数を 1 にした多項式を返す。"""

        if not self:
            return P_ZERO
        leading = self.leading_coefficient
        return Polynomial(*(coefficient / leading for coefficient in self.coefficients))

    def gcd(self, other: Polynomial) -> Polynomial:
        """Euclid の互除法でモニック最大公約数を返す。"""

        if not isinstance(other, Polynomial):
            raise TypeError("gcd の引数は Polynomial でなければなりません")
        left, right = self, other
        while right:
            left, right = right, left % right
        return left.monic()

    def square_free(self) -> Polynomial:
        """重根を除いた平方因子なし部分を返す。"""

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
        if self.degree != 0:
            raise TypeError("定数多項式だけを int に変換できます")
        coefficient = self.coefficients[0]
        if coefficient.q != Z_ONE:
            raise TypeError("整数でない定数多項式は int に変換できません")
        return int(coefficient.p)

    def __hash__(self) -> int:
        if self.degree == 0:
            # 下位の数体系と等しい定数多項式は同じ hash を持つ。
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
    """互換性のための単純な係数イテレータ。"""

    def __init__(self, *coefficients: Rational) -> None:
        self._iterator = iter(Polynomial(*coefficients).coefficients)

    def __iter__(self) -> PolynomialIterator:
        return self

    def __next__(self) -> Rational:
        return next(self._iterator)


def polynomial(*coefficients: tuple[int, int]) -> Polynomial:
    """``(分子, 分母)`` の列から多項式を構成する。"""

    return Polynomial(*(rational(p, q) for p, q in coefficients))


def n2p(value: NaturalNumber) -> Polynomial:
    return Polynomial(n2r(value))


def z2p(value: Integer) -> Polynomial:
    return Polynomial(z2r(value))


def r2p(value: Rational) -> Polynomial:
    if not isinstance(value, Rational):
        raise TypeError("r2p の引数は Rational でなければなりません")
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
    """実根を数えるための Sturm 列を返す。"""

    if not isinstance(value, Polynomial):
        raise TypeError("sturm_sequence の引数は Polynomial です")
    if value.degree <= 0:
        raise ValueError("定数多項式から Sturm 列は作れません")

    square_free = value.square_free()
    sequence = [square_free, square_free.derivative()]
    while sequence[-1]:
        remainder = sequence[-2] % sequence[-1]
        if not remainder:
            break
        sequence.append(-remainder)
    return tuple(sequence)


def sign_variations(sequence: tuple[Polynomial, ...], point: Rational) -> int:
    """Sturm 列を点で評価し、0 を除いた符号変化の回数を返す。"""

    signs: list[bool] = []
    for value in sequence:
        sign = value.sign_at(point)
        if sign == 0:
            continue
        signs.append(sign < 0)
    return sum(left != right for left, right in zip(signs, signs[1:]))


def count_real_roots(value: Polynomial, lower: Rational, upper: Rational) -> int:
    """開区間 ``(lower, upper)`` にある相異なる実根の個数を返す。"""

    if not isinstance(value, Polynomial):
        raise TypeError("value は Polynomial でなければなりません")
    lower = cast2r(lower)
    upper = cast2r(upper)
    if lower >= upper:
        raise ValueError("lower は upper より小さくなければなりません")
    if value.sign_at(lower) == 0 or value.sign_at(upper) == 0:
        raise ValueError("区間の端点を多項式の根にはできません")
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
