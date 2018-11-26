from .integer import Integer, integer, Z_MINUS_ONE, Z_ONE, Z_ZERO
from .natural_number import N_ZERO, N_ONE, NaturalNumber


class Rational:
    def __init__(self, p: Integer, q: Integer) -> None:
        self.p = p
        self.q = q

    def __eq__(self, x: 'Rational') -> bool:
        return self.p * x.q == self.q * x.p

    def __add__(self, x: 'Rational') -> 'Rational':
        return Rational(self.p * x.q + self.q * x.p, self.q * x.q)

    def __mul__(self, x: 'Rational') -> 'Rational':
        return Rational(self.p * x.p, self.q * x.q)

    def __neg__(self) -> 'Rational':
        return Rational(-self.p, self.q)

    def __sub__(self, x: 'Rational') -> 'Rational':
        return self + -x

    def __truediv__(self, x: 'Rational') -> 'Rational':
        return Rational(self.p * x.q, self.q * x.p)

    def __le__(self, x: 'Rational') -> bool:
        return self.p * x.q <= self.q * x.p

    def __lt__(self, x: 'Rational') -> bool:
        return self <= x and self != x

    def __bool__(self) -> bool:
        return self != Q_ZERO

    # def __int__(self) -> int:
    #     return int(self)

    def __hash__(self) -> int:
        p, q = int(self.p), int(self.q)
        ap, aq = abs(p), abs(q)
        if p >= 0 and q >= 0:
            return (2 * (ap + aq)) ** 2 + 2 * aq
        if p >= 0 > q:
            return (2 * (ap + aq)) ** 2 + 2 * aq + 1
        if p < 0 <= q:
            return (2 * (ap + aq) + 1) ** 2 + 2 * aq
        if p < 0 and q < 0:
            return (2 * (ap + aq) + 1) ** 2 + 2 * aq + 1

    def __str__(self) -> str:
        return f"{self.p}/{self.q}"

    def __repr__(self) -> str:
        return f"<Rational {str(self)}>"

    def __pow__(self, x: 'NaturalNumber') -> 'Rational':
        if x == N_ZERO:
            return Q_ONE
        else:
            return (self ** (x - N_ONE)) * self

    def __pos__(self) -> 'Rational':
        return self

    def __abs__(self) -> 'Rational':
        return Rational(
            Integer(abs(self.p), N_ZERO),
            Integer(abs(self.q), N_ZERO)
        )

    def reduction(self) -> 'Rational':
        a, b = self.p.normalize(), self.q.normalize()
        while b:
            a, b = b, a % b
        Rational(self.p.normalize() / a, self.q.normalize() / a)


Q_ZERO = Rational(Z_ZERO, Z_ONE)
Q_ONE = Rational(Z_ONE, Z_ONE)
Q_MINUS_ONE = Rational(Z_MINUS_ONE, Z_ONE)


def rational(p, q):
    return Rational(integer(p), integer(q))
