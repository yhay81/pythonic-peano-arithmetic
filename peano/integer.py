from typing import Tuple
from .natural_number import NaturalNumber, natural_number, N_ZERO, N_ONE
from .logger import z_logger

# from .rational import Rational

class Integer:
    def __init__(self, a: NaturalNumber, b: NaturalNumber) -> None:
        (self.a, self.b) = (a, b)
        self._repr = repr(self)

    def __repr__(self) -> str:
        if not hasattr(self, '_repr'):
            self._repr = f"<Z_({repr(self.a)}, {repr(self.b)})>"
        return self._repr

    def __str__(self) -> str:
        return str(int(self))

    def __int__(self) -> int:
        if self >= Z_ZERO:
            return int(abs(self))
        else:
            return -int(abs(self))

    def __abs__(self) -> NaturalNumber:
        if self.a >= self.b:
            return self.a - self.b
        else:
            return self.b - self.a

    def __eq__(self, x: 'Integer') -> bool:
        z_logger.log(11, f'{repr(self)}.a + {repr(x)}.b == {repr(self)}.b + {repr(x)}.a')
        return self.a + x.b == self.b + x.a

    def __le__(self, x: 'Integer') -> bool:
        z_logger.log(12, f'{repr(self)}.a + {repr(x)}.b <= {repr(self)}.b + {repr(x)}.a')
        return self.a + x.b <= self.b + x.a

    def __lt__(self, x: 'Integer') -> bool:
        z_logger.log(12, f'{self} <= {x} and {self} != {x}')
        return self <= x and self != x

    def __add__(self, x: 'Integer') -> 'Integer':
        z_logger.log(13, f'Integer({repr(self)}.a + {repr(x)}.a, {repr(self)}.b + {repr(x)}.b)')
        return Integer(self.a + x.a, self.b + x.b)

    def __neg__(self) -> 'Integer':
        return Integer(self.b, self.a)

    def __sub__(self, x: 'Integer') -> 'Integer':
        z_logger.log(13, f'{repr(self)} + -{repr(x)}')
        return self + -x

    def __mul__(self, x: 'Integer') -> 'Integer':
        z_logger.log(14,
                     f'Integer({repr(self)}.a * {repr(x)}.a + {repr(self)}.b * {repr(x)}.b, '
                     + f'{repr(self)}.a * {repr(x)}.b + {repr(self)}.b * {repr(x)}.a)'
                     )
        return Integer(self.a * x.a + self.b * x.b, self.a * x.b + self.b * x.a)

    # def __truediv__(self, x: 'Integer'):
    #     z_logger.log(13, f'Rational({repr(self)}, {repr(x)})')
    #     return Rational(self, x)

    def __floordiv__(self, x: 'Integer') -> 'Integer':
        z_logger.log(14, f'Z_ONE + (({repr(self)} - {repr(x)} // {repr(x)})')
        if x == Z_ZERO:
            raise ZeroDivisionError
        if self < x:
            return N_ZERO
        else:
            return Z_ONE + ((self - x) // x)

    def __mod__(self, x: 'Integer') -> 'Integer':
        z_logger.log(14, f'({repr(self)} - {repr(x)}) % {repr(x)}')
        if x == Z_ZERO:
            raise ZeroDivisionError
        if self < x:
            return self
        else:
            return (self - x) % x

    def __divmod__(self, x: 'Integer') -> Tuple['Integer', 'Integer']:
        return self // x, self % x

    def __pow__(self, x: NaturalNumber) -> 'Integer':
        if x == N_ZERO:
            return Z_ONE
        else:
            z_logger.log(15, f'({repr(self)} ** ({repr(x)} - N_ONE)) * {repr(self)}')
            return (self ** (x - N_ONE)) * self

    def __bool__(self) -> bool:
        return self != Z_ZERO

    def __hash__(self) -> int:
        return int(self)

    def __pos__(self):
        return self

    def is_positive(self) -> bool:
        return self > Z_ZERO

    def normalize(self) -> 'Integer':
        if self.a <= self.b:
            return Integer(N_ZERO, self.b - self.a)
        else:
            return Integer(self.a - self.b, N_ZERO)


Z_ZERO = Integer(N_ZERO, N_ZERO)
Z_ONE = Integer(N_ONE, N_ZERO)
Z_MINUS_ONE = Integer(N_ZERO, N_ONE)


def integer(x):
    return Integer(natural_number(x), N_ZERO) if x >= 0 else Integer(N_ZERO, natural_number(abs(x)))
