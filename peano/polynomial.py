from .integer import Integer
from .natural_number import N_ONE, N_ZERO, NaturalNumber
from .rational import Q_ONE, Q_ZERO, Rational, n2r, rational, z2r


class Polynomial:
    def __init__(self, *k: Rational) -> None:
        self.k = k

    def __eq__(self, x: object) -> bool:
        x = cast2p(x)
        return all(map(lambda a, b: a == b, self.k, x.k))

    def __add__(self, x: object) -> "Polynomial":
        x = cast2p(x)
        return Polynomial(*list(map(lambda a, b: a + b, self.k, x.k)))  # type: ignore

    def __iter__(self) -> "PolynomialIterator":
        return PolynomialIterator(*self.k)

    def __mul__(self, x: object) -> "Polynomial":
        x = cast2p(x)
        result: list[Rational] = []
        for i, sk in enumerate(self):
            for j, xk in enumerate(x):
                result[i + j] += sk * xk
        return Polynomial(*result)

    def __neg__(self) -> "Polynomial":
        return Polynomial(*map(lambda x: -x, self))  # type: ignore

    def __sub__(self, x: object) -> "Polynomial":
        x = cast2p(x)
        return self + -x

    # def __floordiv__(self, x):  # TODO

    def __len__(self) -> int:
        return len(self.k)

    # def __le__(self, x):  # TODO

    # def __lt__(self, x):  # TODO

    def __bool__(self) -> bool:
        return any(map(lambda x: x != Q_ZERO, self))

    # def __int__(self): # TODO

    # def __hash__(self): # TODO

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
    def __init__(self, *k: Rational) -> None:
        super().__init__(*k)
        self._i = 0
        self.n = len(k)

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
    return Polynomial(*[rational(p, q) for p, q in k])


def n2p(x: NaturalNumber) -> Polynomial:
    return Polynomial(n2r(x))


def z2p(x: Integer) -> Polynomial:
    return Polynomial(z2r(x))


def r2p(x: Rational) -> Polynomial:
    return Polynomial(x)


def cast2p(x: object) -> Polynomial:
    if isinstance(x, NaturalNumber):
        x = n2p(x)
    if isinstance(x, Integer):
        x = z2p(x)
    if isinstance(x, Rational):
        x = r2p(x)
    if not isinstance(x, Polynomial):
        raise TypeError(f"{repr(x)} is not an Polynomial, but {type(x)}")
    return x
