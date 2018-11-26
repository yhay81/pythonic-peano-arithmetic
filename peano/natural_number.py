from typing import Tuple


# from .integer import Integer
# from .rational import Rational


class NaturalNumber:
    def __init__(self, p=None) -> None:
        self.predecessor = p

    def __eq__(self, x: 'NaturalNumber') -> bool:
        if self.predecessor is None and x.predecessor is None:
            return True
        elif (self.predecessor is None and x.predecessor is not None) \
                or (self.predecessor is not None and x.predecessor is None):
            return False
        else:
            return self.predecessor == x.predecessor

    def __add__(self, x: 'NaturalNumber') -> 'NaturalNumber':
        if x == N_ZERO:
            return self
        else:
            return NaturalNumber(self + x.predecessor)

    def __mul__(self, x: 'NaturalNumber') -> 'NaturalNumber':
        if x == N_ZERO:
            return N_ZERO
        else:
            return self + self * x.predecessor

    def __le__(self, x: 'NaturalNumber') -> bool:
        if self == N_ZERO:
            return True
        elif x == N_ZERO:
            return False
        else:
            return self.predecessor <= x.predecessor

    def __lt__(self, x: 'NaturalNumber') -> bool:
        return self <= x and self != x

    def __sub__(self, x: 'NaturalNumber') -> 'NaturalNumber':
        if x == N_ZERO:
            return self
        elif self == N_ZERO:
            raise ValueError
        else:
            return self.predecessor - x.predecessor

    def __mod__(self, x: 'NaturalNumber') -> 'NaturalNumber':
        if x == N_ZERO:
            raise ZeroDivisionError
        if self < x:
            return self
        else:
            return (self - x) % x

    def __floordiv__(self, x: 'NaturalNumber') -> 'NaturalNumber':
        if x == N_ZERO:
            raise ZeroDivisionError
        if self < x:
            return N_ZERO
        else:
            return N_ONE + ((self - x) // x)

    def __bool__(self) -> bool:
        return self != N_ZERO

    def __int__(self) -> int:
        if self == N_ZERO:
            return 0
        else:
            return int(self.predecessor) + 1

    def __hash__(self) -> int:
        return int(self)

    def __str__(self) -> str:
        return str(int(self))

    def __repr__(self) -> str:
        return f"<NaturalNumber {str(self)}>"

    def set_repr(self) -> frozenset:
        if self == N_ZERO:
            return frozenset()
        else:
            preset = self.predecessor.set_repr()
            return frozenset((preset,)) | preset

    def set_str(self) -> str:
        return str(self.set_repr()).replace('{', '').replace('}', '').replace('frozenset(', '{').replace(')', '}')

    def __iter__(self) -> 'NaturalNumberIterator':
        return NaturalNumberIterator(self)

    def __reversed__(self) -> 'NaturalNumberReversedIterator':
        return NaturalNumberReversedIterator(self)

    # def __truediv__(self, x: 'NaturalNumberReversedIterator'):
    #     return Rational(Integer(self, N_ZERO), Integer(x, N_ZERO))

    def __divmod__(self, x: 'NaturalNumber') -> Tuple['NaturalNumber', 'NaturalNumber']:
        return self // x, self % x

    def __pow__(self, x) -> 'NaturalNumber':
        if x == N_ZERO:
            return N_ONE
        else:
            return (self ** (x - N_ONE)) * self

    # def __neg__(self):
    #     return Integer(N_ZERO, self)

    def __pos__(self) -> 'NaturalNumber':
        return self

    def __abs__(self) -> 'NaturalNumber':
        return self


class NaturalNumberIterator(NaturalNumber):
    def __init__(self, n: NaturalNumber) -> None:
        super().__init__(n.predecessor)
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
        super().__init__(n.predecessor)
        self._i = n
        self.n = n

    def __iter__(self) -> 'NaturalNumberReversedIterator':
        return self

    def __next__(self) -> NaturalNumber:
        if self._i == N_ZERO:
            raise StopIteration()
        else:
            self._i = self._i.predecessor
            return self._i


def successor(n: NaturalNumber) -> NaturalNumber:
    return NaturalNumber(n)


def natural_number(k: int) -> NaturalNumber:
    return N_ZERO if k == 0 else NaturalNumber(natural_number(k - 1))


N_ZERO = NaturalNumber()
N_ONE = NaturalNumber(N_ZERO)
