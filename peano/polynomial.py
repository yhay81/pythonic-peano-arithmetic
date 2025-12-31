from itertools import zip_longest

from .integer import Z_ONE, Integer
from .natural_number import N_ONE, N_ZERO, NaturalNumber
from .rational import Q_ONE, Q_ZERO, Rational, n2r, rational, z2r


class Polynomial:
    """有理数係数の多項式を係数列で表すクラス。"""

    def __init__(self, *k: Rational) -> None:
        self._k: tuple[Rational, ...]
        if not k:
            self._k = (Q_ZERO,)
            return
        coeffs = list(k)
        while len(coeffs) > 1 and coeffs[-1] == Q_ZERO:
            coeffs.pop()
        self._k = tuple(coeffs)

    @property
    def k(self) -> tuple[Rational, ...]:
        return self._k

    def __eq__(self, x: object) -> bool:
        x = cast2p(x)
        return self.k == x.k

    def _order_key(self) -> tuple[object, ...]:
        return (len(self.k) - 1, *reversed(self.k))

    def __add__(self, x: object) -> "Polynomial":
        x = cast2p(x)
        coeffs = [a + b for a, b in zip_longest(self.k, x.k, fillvalue=Q_ZERO)]
        return Polynomial(*coeffs)

    def __iter__(self) -> "PolynomialIterator":
        return PolynomialIterator(*self.k)

    def __mul__(self, x: object) -> "Polynomial":
        x = cast2p(x)
        result: list[Rational] = [Q_ZERO] * (len(self.k) + len(x.k) - 1)
        for i, sk in enumerate(self.k):
            for j, xk in enumerate(x.k):
                result[i + j] = result[i + j] + (sk * xk)
        return Polynomial(*result)

    def __neg__(self) -> "Polynomial":
        return Polynomial(*map(lambda x: -x, self))

    def __sub__(self, x: object) -> "Polynomial":
        x = cast2p(x)
        return self + -x

    def __floordiv__(self, x: object) -> "Polynomial":
        x = cast2p(x)
        if not x:
            raise ZeroDivisionError
        if len(self.k) < len(x.k):
            return P_ZERO
        quotient_coeffs = [Q_ZERO] * (len(self.k) - len(x.k) + 1)
        remainder = self
        while remainder and len(remainder.k) >= len(x.k):
            degree_diff = len(remainder.k) - len(x.k)
            lead_coeff = remainder.k[-1] / x.k[-1]
            quotient_coeffs[degree_diff] = lead_coeff
            term_coeffs = [Q_ZERO] * degree_diff + [lead_coeff]
            remainder = remainder - (x * Polynomial(*term_coeffs))
        return Polynomial(*quotient_coeffs)

    def __len__(self) -> int:
        return len(self.k)

    def __le__(self, x: object) -> bool:
        x = cast2p(x)
        return self._order_key() <= x._order_key()

    def __lt__(self, x: object) -> bool:
        x = cast2p(x)
        return self._order_key() < x._order_key()

    def __bool__(self) -> bool:
        return any(k != Q_ZERO for k in self.k)

    def __int__(self) -> int:
        if len(self.k) != 1:
            raise TypeError
        reduced = self.k[0].reduction()
        if reduced.q != Z_ONE:
            raise TypeError
        return int(reduced.p)

    def __hash__(self) -> int:
        return hash(self.k)

    def __str__(self) -> str:
        return "+".join(f"{sk}x^{i}" for i, sk in enumerate(self))

    def __repr__(self) -> str:
        return f"<P({str(self)})>"

    def __pow__(self, x: object) -> "Polynomial":
        if not isinstance(x, NaturalNumber):
            raise TypeError(f"{repr(x)} is not NaturalNumber")
        if x == N_ZERO:
            return Polynomial(Q_ONE)
        else:
            return (self ** (x - N_ONE)) * self  # type: ignore

    def __pos__(self) -> "Polynomial":
        return self

    def reduction(self) -> "Polynomial":
        return Polynomial(*list(map(lambda x: x.reduction(), self)))


class PolynomialIterator(Polynomial):
    """多項式の係数を先頭から順に返すイテレータ。"""

    def __init__(self, *k: Rational) -> None:
        super().__init__(*k)
        self._i = 0
        self.n = len(self.k)

    def __iter__(self) -> "PolynomialIterator":
        return self

    def __next__(self) -> Rational:
        if self._i == self.n:
            raise StopIteration()
        else:
            i = self._i
            self._i += 1
            return self.k[i]


P_ZERO = Polynomial(Q_ZERO)
P_ONE = Polynomial(Q_ONE)


def polynomial(*k: tuple[int, int]) -> Polynomial:
    """(分子, 分母) の組から多項式を構成する。"""

    return Polynomial(*[rational(p, q) for p, q in k])


def n2p(x: NaturalNumber) -> Polynomial:
    """自然数を定数多項式として埋め込む。"""

    return Polynomial(n2r(x))


def z2p(x: Integer) -> Polynomial:
    """整数を定数多項式として埋め込む。"""

    return Polynomial(z2r(x))


def r2p(x: Rational) -> Polynomial:
    """有理数を定数多項式として埋め込む。"""

    return Polynomial(x)


def cast2p(x: object) -> Polynomial:
    """Polynomial への型変換を強制する。"""

    if isinstance(x, NaturalNumber):
        x = n2p(x)
    if isinstance(x, Integer):
        x = z2p(x)
    if isinstance(x, Rational):
        x = r2p(x)
    if not isinstance(x, Polynomial):
        raise TypeError(f"{repr(x)} is not an Polynomial, but {type(x)}")
    return x
