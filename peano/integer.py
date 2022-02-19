from .natural_number import N_ONE, N_ZERO, NaturalNumber, natural_number
from .utils import log


class Integer:
    def __init__(self, a: NaturalNumber, b: NaturalNumber) -> None:
        (self.a, self.b) = (a, b)
        self._repr = repr(self)

    def __repr__(self) -> str:
        if not hasattr(self, "_repr"):
            self._repr = f"<Z({int(self.a)},{int(self.b)})>"
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
            return self.a - self.b  # type: ignore
        else:
            return self.b - self.a  # type: ignore

    @log(log_level=11)
    def __eq__(self, x: object) -> tuple[bool, str]:
        x = cast2z(x)
        formula = f"{repr(self)} == {repr(x)}"
        return (
            self.a + x.b == self.b + x.a,
            f"{formula} = {repr(self.a)} + {repr(x.b)} == {repr(self.b)} + {repr(x.a)}",
        )

    @log(log_level=12)
    def __le__(self, x: object) -> tuple[bool, str]:
        x = cast2z(x)
        formula = f"{repr(self)} <= {repr(x)}"
        return (
            self.a + x.b <= self.b + x.a,
            f"{formula} = {repr(self.a)} + {repr(x.b)} <= {repr(self.b)} + {repr(x.a)}",
        )

    @log(log_level=13)
    def __lt__(self, x: object) -> tuple[bool, str]:
        x = cast2z(x)
        formula = f"{repr(self)} < {repr(x)}"
        return self <= x and self != x, f"{formula} = {self} <= {x} and {self} != {x}"

    @log(log_level=14)
    def __add__(self, x: object) -> tuple["Integer", str]:
        x = cast2z(x)
        formula = f"{repr(self)} + {repr(x)}"
        return (
            Integer(self.a + x.a, self.b + x.b),
            f"{formula} = Integer({repr(self.a)} + {repr(x.a)}, {repr(self.b)} + {repr(x.b)})",
        )

    @log(log_level=14)
    def __neg__(self) -> tuple["Integer", str]:
        return (
            Integer(self.b, self.a),
            f"-{repr(self)} = Integer({repr(self.b)}, {repr(self.a)})",
        )

    @log(log_level=14)
    def __sub__(self, x: object) -> tuple["Integer", str]:
        x = cast2z(x)
        formula = f"{repr(self)} - {repr(x)}"
        return self + -x, f"{formula} = {repr(self)} + {repr(-x)}"

    @log(log_level=15)
    def __mul__(self, x: object) -> tuple["Integer", str]:
        x = cast2z(x)
        formula = f"{repr(self)} * {repr(x)}"
        return (
            Integer(self.a * x.a + self.b * x.b, self.a * x.b + self.b * x.a),
            f"{formula} = "
            f"Integer({repr(self.a)} * {repr(x.a)} + {repr(self.b)} * {repr(x.b)}, "
            f"{repr(self.a)} * {repr(x.b)} + {repr(self.b)} * {repr(x.a)})",
        )

    @log(log_level=15)
    def __truediv__(self, x: object):  # type: ignore
        x = cast2z(x)
        formula = f"{repr(self)} / {repr(x)}"
        from .rational import Rational

        return Rational(self, x), f"{formula} = Rational({repr(self)}, {repr(x)})"

    @log(log_level=15)
    def __floordiv__(self, x: object) -> tuple["Integer", str]:
        x = cast2z(x)
        if x == Z_ZERO:
            raise ZeroDivisionError
        formula = f"{repr(self)} // {repr(x)}"
        if (self > Z_ZERO and x > Z_ZERO and self >= x) or (
            self < Z_ZERO and x < Z_ZERO and self <= x
        ):
            return (
                Z_ONE + ((self - x) // x),
                f"{formula} = {repr(Z_ONE)} + (({repr(self)} - {repr(x)}) // {repr(x)})",
            )
        elif (self > Z_ZERO and x < Z_ZERO and self >= Z_ZERO) or (
            self < Z_ZERO and x > Z_ZERO and self <= Z_ZERO
        ):
            return (
                Z_MINUS_ONE + ((self + x) // x),
                f"{formula} = {repr(Z_MINUS_ONE)} + (({repr(self)} + {repr(x)}) // {repr(x)})",
            )
        else:
            return Z_ZERO, f"{formula} = {repr(Z_ZERO)}"

    @log(log_level=15)
    def __mod__(self, x: object) -> tuple["Integer", str]:
        x = cast2z(x)
        if x == Z_ZERO:
            raise ZeroDivisionError
        formula = f"{repr(self)} % {repr(x)}"
        if (self > Z_ZERO and x > Z_ZERO and self >= x) or (
            self < Z_ZERO and x < Z_ZERO and self <= x
        ):
            return (self - x) % x, f"{formula} = ({repr(self)} - {repr(x)}) % {repr(x)}"
        elif (self > Z_ZERO and x < Z_ZERO and self >= Z_ZERO) or (
            self < Z_ZERO and x > Z_ZERO and self <= Z_ZERO
        ):
            return (self + x) % x, f"{formula} = ({repr(self)} + {repr(x)}) % {repr(x)}"
        else:
            return self, f"{formula} = {repr(self)}"

    @log(log_level=15)
    def __divmod__(self, x: object) -> tuple[tuple["Integer", "Integer"], str]:
        x = cast2z(x)
        formula = f"divmod({repr(self)}, {repr(x)})"
        return (
            (self // x, self % x),
            f"{formula} = {repr(self)} // {repr(x)}, {repr(self)} % {repr(x)}",
        )

    @log(log_level=16)
    def __pow__(self, x: object) -> tuple["Integer", str]:
        if not isinstance(x, NaturalNumber):
            raise TypeError
        formula = f"{repr(self)} ** {repr(x)}"
        if x == N_ZERO:
            return Z_ONE, f"{formula} = {repr(Z_ONE)}"
        else:
            return (
                (self ** (x - N_ONE)) * self,
                f"{formula} = ({repr(self)} ** ({repr(x)} - N_ONE)) * {repr(self)}",
            )

    def __bool__(self) -> bool:
        return self != Z_ZERO

    def __hash__(self) -> int:
        return int(self)

    def __pos__(self) -> "Integer":
        return self

    def normalize(self) -> "Integer":
        if self.a <= self.b:
            return Integer(N_ZERO, self.b - self.a)
        else:
            return Integer(self.a - self.b, N_ZERO)


Z_ZERO = Integer(N_ZERO, N_ZERO)
Z_ONE = Integer(N_ONE, N_ZERO)
Z_MINUS_ONE = Integer(N_ZERO, N_ONE)


def integer(x: int) -> Integer:
    return (
        Integer(natural_number(x), N_ZERO)
        if x >= 0
        else Integer(N_ZERO, natural_number(abs(x)))
    )


def n2z(x: NaturalNumber) -> Integer:
    return Integer(x, N_ZERO)


def cast2z(x: object) -> Integer:
    if isinstance(x, NaturalNumber):
        x = n2z(x)
    if not isinstance(x, Integer):
        raise TypeError(f"{repr(x)} is not an Integer, but {type(x)}")
    return x
