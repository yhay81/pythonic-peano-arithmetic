from .integer import Integer, integer, Z_MINUS_ONE, Z_ONE, Z_ZERO
from .natural_number import N_ZERO, N_ONE, NaturalNumber
from .logger import q_logger


class Rational:
    def __init__(self, p: Integer, q: Integer) -> None:
        self.p = p
        self.q = q
        self._repr = repr(self)

    def __repr__(self) -> str:
        if not hasattr(self, '_repr'):
            self._repr = f"<Q_{str(self)}>"
        return self._repr

    def __str__(self) -> str:
        return f"{self.p}/{self.q}"

    def __eq__(self, x: 'Rational') -> bool:
        q_logger.log(11, f'{repr(self)}.p * {repr(x)}.q == {repr(self)}.q * {repr(x)}.p')
        return self.p * x.q == self.q * x.p

    def __le__(self, x: 'Rational') -> bool:
        q_logger.log(12, f'self.p * x.q <= self.q * x.p')
        return self.p * x.q <= self.q * x.p

    def __lt__(self, x: 'Rational') -> bool:
        q_logger.log(12, f'self <= x and self != x')
        return self <= x and self != x

    def __add__(self, x: 'Rational') -> 'Rational':
        q_logger.log(13, f'Rational({repr(self)}.p * {repr(x)}.q + {repr(self)}.q * {repr(x)}.p, {repr(self)}.q * {repr(x)}.q)')
        return Rational(self.p * x.q + self.q * x.p, self.q * x.q)

    def __neg__(self) -> 'Rational':
        return Rational(-self.p, self.q)

    def __sub__(self, x: 'Rational') -> 'Rational':
        q_logger.log(13, f'self + -x')
        return self + -x

    def __mul__(self, x: 'Rational') -> 'Rational':
        q_logger.log(14, f'Rational(self.p * x.p, self.q * x.q)')
        return Rational(self.p * x.p, self.q * x.q)

    def __truediv__(self, x: 'Rational') -> 'Rational':
        q_logger.log(14, f'Rational(self.p * x.q, self.q * x.p)')
        return Rational(self.p * x.q, self.q * x.p)

    # def __floordiv__(self, x: 'Integer') -> 'Integer':
    #     pass
    #
    # def __mod__(self, x: 'Integer') -> 'Integer':
    #     pass
    #
    # def __divmod__(self, x: 'Integer') -> Tuple['Integer', 'Integer']:
    #     pass

    def __pow__(self, x: 'NaturalNumber') -> 'Rational':
        q_logger.log(15, f'(self ** (x - N_ONE)) * self')
        if x == N_ZERO:
            return Q_ONE
        else:
            return (self ** (x - N_ONE)) * self

    def __bool__(self) -> bool:
        return self != Q_ZERO

    # def __int__(self) -> int:
    #     if self >= Q_ZERO:
    #         return abs(self) % Q_ONE
    #     else:
    #         return - abs(self) % Q_ONE

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
        return Rational(self.p.normalize() // a, self.q.normalize() // a)


Q_ZERO = Rational(Z_ZERO, Z_ONE)
Q_ONE = Rational(Z_ONE, Z_ONE)
Q_MINUS_ONE = Rational(Z_MINUS_ONE, Z_ONE)


def rational(p, q):
    return Rational(integer(p), integer(q))
