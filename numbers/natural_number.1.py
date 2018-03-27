class NaturalNumber:
    def __init__(self, p=None):
        self.predecessor = p

    def __eq__(self, x):
        if self.predecessor is None and x.predecessor is None:
            return True
        elif (self.predecessor is None and x.predecessor is not None) \
                or (self.predecessor is not None and x.predecessor is None):
            return False
        else:
            return self.predecessor == x.predecessor

    def __add__(self, x):
        if x == N_ZERO:
            return self
        else:
            return NaturalNumber(self + x.predecessor)

    def __mul__(self, x):
        if x == N_ZERO:
            return N_ZERO
        else:
            return self + self * x.predecessor

    def __le__(self, x):
        if self == N_ZERO:
            return True
        elif x == N_ZERO:
            return False
        else:
            return self.predecessor <= x.predecessor

    def __lt__(self, x):
        return self <= x and self != x

    def __sub__(self, x):
        if x == N_ZERO:
            return self
        elif self == N_ZERO:
            raise ValueError
        else:
            return self.predecessor - x.predecessor

    def __mod__(self, x):
        if x == N_ZERO:
            raise ZeroDivisionError
        if self < x:
            return self
        else:
            return (self - x) % x

    def __floordiv__(self, x):
        if x == N_ZERO:
            raise ZeroDivisionError
        if self < x:
            return N_ZERO
        else:
            return N_ONE + ((self - x) // x)

    def __bool__(self):
        return self != N_ZERO

    def __int__(self):
        if self == N_ZERO:
            return 0
        else:
            return int(self.predecessor) + 1

    def __hash__(self):
        return int(self)

    def __str__(self):
        return str(int(self))

    def __repr__(self):
        return f"<NaturalNumber {str(self)}>"

    def set_repr(self):
        if self == N_ZERO:
            return frozenset()
        else:
            preset = self.predecessor.set_repr()
            return frozenset((preset,)) | preset

    def set_str(self):
        return str(self.set_repr()).replace(
            '{', '').replace('}', '').replace(
                'frozenset(', '{').replace(')', '}')

    def __iter__(self):
        return NaturalNumberIterator(self)

    def __reversed__(self):
        return NaturalNumberReversedIterator(self)

    # def __truediv__(self, x):
    #     return Rational(Integer(self, N_ZERO), Integer(x, N_ZERO))

    def __divmod__(self, x):
        return (self // x, self % x)

    def __pow__(self, x):
        if x == N_ZERO:
            return N_ONE
        else:
            return (self ** (x - N_ONE)) * self

    # def __neg__(self):
    #     return Integer(N_ZERO, self)

    def __pos__(self):
        return self

    def __abs__(self):
        return self


class NaturalNumberIterator(NaturalNumber):
    def __init__(self, n):
        super().__init__(n.predecessor)
        self._i = N_ZERO
        self.n = n

    def __iter__(self):
        return self

    def __next__(self):
        if self._i == self.n:
            raise StopIteration()
        else:
            i = self._i
            self._i = NaturalNumber(self._i)
            return i


class NaturalNumberReversedIterator(NaturalNumber):
    def __init__(self, n):
        super().__init__(n.predecessor)
        self._i = n
        self.n = n

    def __iter__(self):
        return self

    def __next__(self):
        if self._i == N_ZERO:
            raise StopIteration()
        else:
            self._i = self._i.predecessor
            return self._i


def successor(n):
    return NaturalNumber(n)


def N(k):
    return N_ZERO if k == 0 else NaturalNumber(N(k - 1))


N_ZERO = NaturalNumber()
N_ONE = NaturalNumber(N_ZERO)
