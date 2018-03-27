from .natural_number import N, N_ZERO, N_ONE


class Integer:
    def __init__(self, a, b):
        (self.a, self.b) = (a, b)

    def __eq__(self, x):
        return self.a + x.b == self.b + x.a

    def __add__(self, x):
        return Integer(self.a + x.a, self.b + x.b)

    def __mul__(self, x):
        return Integer(self.a * x.a + self.b * x.b, self.a * x.b + self.b * x.a)

    def __neg__(self):
        return Integer(self.b, self.a)

    def __sub__(self, x):
        return self + -x

    def normalize(self):
        if self.a <= self.b:
            return Integer(N_ZERO, self.b - self.a)
        else:
            return Integer(self.b - self.a, N_ZERO)

    # def __floordiv__(self, x): TODO
    #     if x.a == x.b:
    #         raise ZeroDivisionError
    #     if self < x:
    #         return self
    #     else:
    #         return (self - x) // x

    def __abs__(self):
        if self.a == N_ZERO:
            return self.b
        elif self.b == N_ZERO:
            return self.a
        else:
            abs(self.a.predecessor, self.b.predecessor)

    def __le__(self, x):
        return self.a + x.b <= self.b + x.a

    def __lt__(self, x):
        return self <= x and self != x

    # def __mod__(self, x): TODO

    # def __floordiv__(self, x): TODO

    def __bool__(self):
        return self != Z_ZERO

    def is_positive(self):
        return self > Z_ZERO

    def __int__(self):
        if self >= Z_ZERO:
            return int(abs(self))
        else:
            return -int(abs(self))

    def __hash__(self):
        return int(self)

    def __str__(self):
        return str(int(self))

    def __repr__(self):
        return f"<Integer {str(self)}>"

    # def __divmod__(self, x): TODO

    def __pow__(self, x):
        if x == N_ZERO:
            return Z_ONE
        else:
            return (self ** (x - N_ONE)) * self

    def __pos__(self):
        return self


Z_ZERO = Integer(N_ZERO, N_ZERO)
Z_ONE = Integer(N_ONE, N_ZERO)
Z_MINUS_ONE = Integer(N_ZERO, N_ONE)


def Z(x):
    return Integer(N(x), N_ZERO) if x >= 0 else Integer(N_ZERO, N(abs(x)))
