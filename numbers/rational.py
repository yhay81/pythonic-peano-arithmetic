from .integer import Integer, Z, Z_MINUS_ONE, Z_ONE, Z_ZERO
from .natural_number import N_ZERO, N_ONE


class Rational:
    def __init__(self, p, q):
        self.p = p
        self.q = q

    def __eq__(self, x):
        return self.p * x.q == self.q * x.p

    def __add__(self, x):
        return Rational(self.p * x.q + self.q * x.p, self.q * x.q)

    def __mul__(self, x):
        return Rational(self.p * x.p, self.q * x.q)

    def __neg__(self):
        return Rational(-self.p, self.q)

    def __sub__(self, x):
        return self + -x

    def __truediv__(self, x):
        return Rational(self.p * x.q, self.q * x.p)

    # def __le__(self, x): TODO

    # def __lt__(self, x): TODO
    #   return self <= x  and self != x

    def __bool__(self):
        return self != Q_ZERO

    # def __int__(self): TODO

    def __hash__(self):
        p, q = int(self.p), int(self.q)
        ap, aq = abs(p), abs(q)
        if p >= 0 and q >= 0:
            return (2 * (ap + aq)) ** 2 + 2 * aq
        if p >= 0 and q < 0:
            return (2 * (ap + aq)) ** 2 + 2 * aq + 1
        if p < 0 and q >= 0:
            return (2 * (ap + aq) + 1) ** 2 + 2 * aq
        if p < 0 and q < 0:
            return (2 * (ap + aq) + 1) ** 2 + 2 * aq + 1

    def __str__(self):
        return f"{self.p}/{self.q}"

    def __repr__(self):
        return f"<Rational {str(self)}>"

    def __pow__(self, x):
        if x == N_ZERO:
            return Q_ONE
        else:
            return (self ** (x - N_ONE)) * self

    def __pos__(self):
        return self

    def __abs__(self):
        return Rational(
            Integer(abs(self.p), N_ZERO),
            Integer(abs(self.q), N_ZERO)
        )

    # def reduction(self): TODO


Q_ZERO = Rational(Z_ZERO, Z_ONE)
Q_ONE = Rational(Z_ONE, Z_ONE)
Q_MINUS_ONE = Rational(Z_MINUS_ONE, Z_ONE)


def Q(p, q):
    return Rational(Z(p), Z(q))
