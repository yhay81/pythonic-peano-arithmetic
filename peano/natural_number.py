from typing import Tuple
from .logger import n_logger


# from .integer import Integer
# from .rational import Rational


class NaturalNumber:
    def __init__(self, p=None) -> None:
        self.pre = p
        self._repr = repr(self)

    def __repr__(self) -> str:
        if not hasattr(self, '_repr'):
            self._repr = f"<N_{str(self)}>"
        return self._repr

    def __str__(self) -> str:
        return str(int(self))

    def __int__(self) -> int:
        if self.pre is None:
            return 0
        else:
            return int(self.pre) + 1

    def __eq__(self, x: 'NaturalNumber') -> bool:
        n_logger.log(11, f'{repr(self)}.pre == {repr(x)}.pre')
        if self.pre is None and x.pre is None:
            return True
        elif (self.pre is None and x.pre is not None) \
                or (self.pre is not None and x.pre is None):
            return False
        else:
            return self.pre == x.pre

    def __le__(self, x: 'NaturalNumber') -> bool:
        if self.pre is None:
            return True
        elif x.pre is None:
            return False
        else:
            n_logger.log(12, f'{repr(self.pre)} <= {repr(x.pre)}')
            return self.pre <= x.pre

    def __lt__(self, x: 'NaturalNumber') -> bool:
        n_logger.log(12, f'{repr(self)} <= {repr(x)} and {repr(self)} != {repr(x)}')
        return self <= x and self != x

    def __add__(self, x: 'NaturalNumber') -> 'NaturalNumber':
        if x.pre is None:
            return self
        else:
            n_logger.log(13, f'NaturalNumber({repr(self)} + {repr(x)}.pre)')
            return NaturalNumber(self + x.pre)

    def __sub__(self, x: 'NaturalNumber') -> 'NaturalNumber':
        n_logger.log(13, f'{repr(self)}.pre - {repr(x)}.pre')
        if x.pre is None:
            return self
        elif self.pre is None:
            raise ValueError
        else:
            return self.pre - x.pre

    def __mul__(self, x: 'NaturalNumber') -> 'NaturalNumber':
        if x.pre is None:
            return N_ZERO
        else:
            n_logger.log(14, f'{repr(self)} + {repr(self)} * {repr(x)}.pre')
            return self + self * x.pre

    # def __truediv__(self, x: 'NaturalNumber'):
    #     n_logger.log(14, f'Rational(Integer({repr(self)}, N_ZERO), Integer({repr(x)}, N_ZERO))')
    #     return Rational(Integer(self, N_ZERO), Integer(x, N_ZERO))

    def __floordiv__(self, x: 'NaturalNumber') -> 'NaturalNumber':
        n_logger.log(14, f'(N_ONE + (({repr(self)} - {repr(x)}) // {repr(x)})')
        if x.pre is None:
            raise ZeroDivisionError
        if self < x:
            return N_ZERO
        else:
            return N_ONE + ((self - x) // x)

    def __mod__(self, x: 'NaturalNumber') -> 'NaturalNumber':
        n_logger.log(14, f'({repr(self)} - {repr(x)} % {repr(x)}')
        if x.pre is None:
            raise ZeroDivisionError
        if self < x:
            return self
        else:
            return (self - x) % x

    def __divmod__(self, x: 'NaturalNumber') -> Tuple['NaturalNumber', 'NaturalNumber']:
        n_logger.log(14, f'{repr(self)} // {repr(x)}, {repr(self)} % {repr(x)}')
        return self // x, self % x

    def __pow__(self, x) -> 'NaturalNumber':
        if x.pre is None:
            return N_ONE
        else:
            n_logger.log(15, f'(self ** (x - N_ONE)) * self')
            return (self ** (x - N_ONE)) * self

    def __bool__(self) -> bool:
        return self.pre is not None

    def __hash__(self) -> int:
        return int(self)

    def __pos__(self) -> 'NaturalNumber':
        return self

    # def __neg__(self):
    #     return Integer(N_ZERO, self)

    def __abs__(self) -> 'NaturalNumber':
        return self

    def __iter__(self) -> 'NaturalNumberIterator':
        return NaturalNumberIterator(self)

    def __reversed__(self) -> 'NaturalNumberReversedIterator':
        return NaturalNumberReversedIterator(self)

    def set_repr(self) -> frozenset:
        if self.pre is None:
            return frozenset()
        else:
            preset = self.pre.set_repr()
            return frozenset((preset,)) | preset

    def set_str(self) -> str:
        return str(self.set_repr()).replace('{', '').replace('}', '').replace('frozenset(', '{').replace(')', '}')



class NaturalNumberIterator(NaturalNumber):
    def __init__(self, n: NaturalNumber) -> None:
        super().__init__(n.pre)
        self._i = N_ZERO
        self.n = n

    def __iter__(self) -> 'NaturalNumberIterator':
        return self

    def __next__(self) -> NaturalNumber:
        if self._i == self.n:
            raise StopIteration()
        else:
            i = self._i
            self._i = NaturalNumber(self._i)
            return i


class NaturalNumberReversedIterator(NaturalNumber):
    def __init__(self, n: NaturalNumber) -> None:
        super().__init__(n.pre)
        self._i = n
        self.n = n

    def __iter__(self) -> 'NaturalNumberReversedIterator':
        return self

    def __next__(self) -> NaturalNumber:
        if self._i.pre is None:
            raise StopIteration()
        else:
            self._i = self._i.pre
            return self._i


def successor(n: NaturalNumber) -> NaturalNumber:
    return NaturalNumber(n)


def natural_number(k: int) -> NaturalNumber:
    return N_ZERO if k == 0 else NaturalNumber(natural_number(k - 1))


N_ZERO = NaturalNumber()
N_ONE = NaturalNumber(N_ZERO)
