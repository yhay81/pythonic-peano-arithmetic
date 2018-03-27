import types
from .numbers.natural_number import N, N_ZERO, N_ONE


class ResidueRingModulo:
    modulo = N_ONE

    def __init__(self, n):
        self.number = n % self.modulo

    def __init_subclass__(cls, modulo):
        super().__init_subclass__()
        cls.modulo = modulo
        cls.__add__ = lambda s, x: cls(s.number + x.number)
        cls.__mul__ = lambda s, x: cls(s.number * x.number)
        cls.__pow__ = lambda s, x: cls(s.number ** x)

        def invert(s):
            for i in modulo:
                if s * cls(i) == cls(1):
                    return cls(i)
            else:
                raise ValueError

        cls.__invert__ = invert

        def truediv(s, x):
            for i in modulo:
                if x * cls(i) == s:
                    return cls(i)
            else:
                raise ValueError

        cls.__truediv__ = truediv

    def __eq__(self, x):
        return self.number == x.number

    def __add__(self, x):
        return ResidueRingModulo(self.number + x.number)

    def __mul__(self, x):
        return ResidueRingModulo(self.number + x.number)

    def __int__(self):
        return int(self.number)

    def __str__(self):
        return str(int(self))

    def __repr__(self):
        return "<{} mod {}>".format(str(self), str(self.modulo))


def modulo(m):
    return types.new_class("Z_" + str(m), (ResidueRingModulo,), {'modulo': m})


def print_add_table(values):
    result = "+ | " + " ".join(map(str, values)) + "\n"
    result += "--|-" + "--" * len(values) + "\n"
    for i in values:
        result += str(i) + " | " + \
            " ".join(map(lambda x: str(i + x), values)) + "\n"
    print(result)


def print_mul_table(values):
    result = "* | " + " ".join(map(str, values)) + "\n"
    result += "--|-" + "--" * len(values) + "\n"
    for i in values:
        result += str(i) + " | " + \
            " ".join(map(lambda x: str(i * x), values)) + "\n"
    print(result)


def print_pow_table(values):
    n = N(len(values))
    result = "^ | " + " ".join(map(str, n)) + "\n"
    result += "--|-" + "--" * len(values) + "\n"
    for i in values:
        result += str(i) + " | " + \
            " ".join(map(lambda x: str(i ** x), n)) + "\n"
    print(result)
