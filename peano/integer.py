# from typing import Tuple
from .natural_number import NaturalNumber, natural_number, N_ZERO, N_ONE


class Integer:
    def __init__(self, a: NaturalNumber, b: NaturalNumber) -> None:
        (self.a, self.b) = (a, b)

    def __eq__(self, x: 'Integer') -> bool:
        return self.a + x.b == self.b + x.a

    def __add__(self, x: 'Integer') -> 'Integer':
        return Integer(self.a + x.a, self.b + x.b)

    def __mul__(self, x: 'Integer') -> 'Integer':
        return Integer(self.a * x.a + self.b * x.b, self.a * x.b + self.b * x.a)

    def __neg__(self) -> 'Integer':
        return Integer(self.b, self.a)

    def __sub__(self, x: 'Integer') -> 'Integer':
        return self + -x

    def normalize(self) -> 'Integer':
        if self.a <= self.b:
            return Integer(N_ZERO, self.b - self.a)
        else:
            return Integer(self.b - self.a, N_ZERO)

    def __abs__(self) -> NaturalNumber:
        if self.a == N_ZERO:
            return self.b
        elif self.b == N_ZERO:
            return self.a
        else:
            return abs(self.a.predecessor - self.b.predecessor)

    def __le__(self, x: 'Integer') -> bool:
        return self.a + x.b <= self.b + x.a

    def __lt__(self, x: 'Integer') -> bool:
        return self <= x and self != x

    # def __mod__(self, x: 'Integer') -> 'Integer':  # TODO
    #     if x == Z_ZERO:
    #         raise ZeroDivisionError
    #     if self < x:
    #         return self
    #     else:
    #         return (self - x) % x

    # def __floordiv__(self, x: 'Integer') -> 'Integer':  # TODO
    #     if x == Z_ZERO:
    #         raise ZeroDivisionError
    #     if self < x:
    #         return N_ZERO
    #     else:
    #         return Z_ONE + ((self - x) // x)

    def __bool__(self) -> bool:
        return self != Z_ZERO

    def is_positive(self) -> bool:
        return self > Z_ZERO

    def __int__(self) -> int:
        if self >= Z_ZERO:
            return int(abs(self))
        else:
            return -int(abs(self))

    def __hash__(self) -> int:
        return int(self)

    def __str__(self) -> str:
        return str(int(self))

    def __repr__(self) -> str:
        return f"<Integer {str(self)}>"

    # def __divmod__(self, x: 'Integer') -> Tuple['Integer', 'Integer']:  # TODO
    #     return self // x, self % x

    def __pow__(self, x: NaturalNumber) -> 'Integer':
        if x == N_ZERO:
            return Z_ONE
        else:
            return (self ** (x - N_ONE)) * self

    def __pos__(self):
        return self


Z_ZERO = Integer(N_ZERO, N_ZERO)
Z_ONE = Integer(N_ONE, N_ZERO)
Z_MINUS_ONE = Integer(N_ZERO, N_ONE)


def integer(x):
    return Integer(natural_number(x), N_ZERO) if x >= 0 else Integer(N_ZERO, natural_number(abs(x)))
