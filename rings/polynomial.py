from .rational import Rational, Q_ZERO, Q_ONE
from .numbers.natural_number import N, N_ZERO, N_ONE


class Polynomial:
    def __init__(self, *k):
        self.k = k

    def __eq__(self, x):
        return all(lambda a, b: a == b, zip(self.k, x.k))

    def __add__(self, x):
        return Polynomial(*list(map(lambda a, b: a + b, zip(self.k, x.k))))

    def __iter__(self):
        return PolynomialIterator(self.k)

    def __mul__(self, x):
        result = []
        for i, sk in enumerate(self):
            for j, xk in enumerate(x):
                result[i + j] += sk * xk
        return Polynomial(*result)

    def __neg__(self):
        return Polynomial(*list(map(lambda x: -x, self)))

    def __sub__(self, x):
        return self + -x

    # def __floordiv__(self, x): TODO

    # def __le__(self, x): TODO

    # def __lt__(self, x): TODO
    #   return self <= x  and self != x

    def __bool__(self):
        return any(lambda x: x != Q_ZERO, self)

    # def __int__(self): TODO

    # def __hash__(self): TODO

    def __str__(self):
        return "+".join(f"{sk}x^{i}" for i, sk in self)

    def __repr__(self):
        return f"<Polynomial {str(self)}>"

    def __pow__(self, x):
        if x == N_ZERO:
            return Q_ONE
        else:
            return (self ** (x - N_ONE)) * self

    def __pos__(self):
        return self

    # def reduction(self): TODO


class PolynomialIterator(Polynomial):
    def __init__(self, *k):
        super().__init__(*k)
        self._i = 0
        self.n = len(k)

    def __iter__(self):
        return self

    def __next__(self):
        if self._i == self.n:
            raise StopIteration()
        else:
            i = self._i
            self._i += 1
            return self.k[i]


P_ZERO = Polynomial(Q_ZERO)
P_ONE = Polynomial(Q_ONE)


def P(*k):
    return Polynomial(Q(p, q) for p, q in k)
