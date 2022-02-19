from .integer import Z_MINUS_ONE, Z_ONE, Z_ZERO, Integer, integer, n2z
from .natural_number import N_ONE, N_ZERO, NaturalNumber
from .utils import log


class Rational:
    def __init__(self, p: Integer, q: Integer) -> None:
        self.p = p
        self.q = q
        self._repr = repr(self)

    def __repr__(self) -> str:
        if not hasattr(self, "_repr"):
            self._repr = f"<Q({str(self)})>"
        return self._repr

    def __str__(self) -> str:
        return f"{self.p}/{self.q}"

    @log(log_level=21)
    def __eq__(self, x: object) -> tuple[bool, str]:
        x = cast2z(x)
        formula = f"{repr(self)} == {repr(x)}"
        return (
            self.p * x.q == self.q * x.p,
            f"{formula} = {repr(self)}.p * {repr(x)}.q == {repr(self)}.q * {repr(x)}.p",
        )

    @log(log_level=22)
    def __le__(self, x: object) -> tuple[bool, str]:
        x = cast2z(x)
        formula = f"{repr(self)} <= {repr(x)}"
        return (
            self.p * x.q <= self.q * x.p,
            f"{formula} = {repr(self)}.p * {repr(x)}.q <= {repr(self)}.q * {repr(x)}.p",
        )

    @log(log_level=23)
    def __lt__(self, x: object) -> tuple[bool, str]:
        x = cast2z(x)
        formula = f"{repr(self)} < {repr(x)}"
        return (
            self <= x and self != x,
            f"{formula} = {repr(self)} <= {repr(x)} and {repr(self)} != {repr(x)}",
        )

    @log(log_level=24)
    def __add__(self, x: object) -> tuple["Rational", str]:
        x = cast2z(x)
        formula = f"{repr(self)} + {repr(x)}"
        return (
            Rational(self.p * x.q + self.q * x.p, self.q * x.q),
            f"{formula} = "
            f"Rational({repr(self)}.p * {repr(x)}.q + {repr(self)}.q * {repr(x)}.p, "
            f"{repr(self)}.q * {repr(x)}.q)",
        )

    @log(log_level=24)
    def __neg__(self) -> tuple["Rational", str]:
        formula = f"-{repr(self)}"
        return (
            Rational(-self.p, self.q),
            f"{formula} = Rational(-{repr(self.p)}, {repr(self.q)})",
        )

    @log(log_level=24)
    def __sub__(self, x: object) -> tuple["Rational", str]:
        x = cast2z(x)
        formula = f"{repr(self)} - {repr(x)}"
        return self + -x, f"{formula} = {repr(self)} + -{repr(x)}"

    @log(log_level=25)
    def __mul__(self, x: object) -> tuple["Rational", str]:
        x = cast2z(x)
        formula = f"{repr(self)} * {repr(x)}"
        return (
            Rational(self.p * x.p, self.q * x.q),
            f"{formula} = Rational({repr(self)}.p * {repr(x)}.p, {repr(self)}.q * {repr(x)}.q)",
        )

    @log(log_level=25)
    def __truediv__(self, x: object) -> tuple["Rational", str]:
        x = cast2z(x)
        formula = f"{repr(self)} / {repr(x)}"
        return (
            Rational(self.p * x.q, self.q * x.p),
            f"{formula} = Rational({repr(self)}.p * {repr(x)}.q, {repr(self)}.q * {repr(x)}.p)",
        )

    @log(log_level=26)
    def __pow__(self, x: object) -> tuple["Rational", str]:
        if not isinstance(x, NaturalNumber):
            raise TypeError(f"{repr(x)} is not NaturalNumber")
        formula = f"{repr(self)} ** {repr(x)}"
        if x == N_ZERO:
            return (
                Q_ONE,
                f"{formula} = {repr(Q_ONE)}",
            )
        else:
            return (
                (self ** (x - N_ONE)) * self,
                f"{formula} = ({repr(self)} ** ({repr(x)} - {repr(N_ONE)})) * {repr(self)}",
            )

    def __bool__(self) -> bool:
        return self != Q_ZERO

    def __hash__(self) -> int:
        p, q = int(self.p), int(self.q)
        ap, aq = abs(p), abs(q)
        return (2 * (ap + aq) + int(p < 0)) ** 2 + 2 * aq + int(q < 0)

    def __pos__(self) -> "Rational":
        return self

    def __abs__(self) -> "Rational":
        return Rational(Integer(abs(self.p), N_ZERO), Integer(abs(self.q), N_ZERO))

    def reduction(self) -> "Rational":
        a, b = self.p.normalize(), self.q.normalize()
        while b:
            a, b = b, a % b
        return Rational(self.p.normalize() // a, self.q.normalize() // a)


Q_ZERO = Rational(Z_ZERO, Z_ONE)
Q_ONE = Rational(Z_ONE, Z_ONE)
Q_MINUS_ONE = Rational(Z_MINUS_ONE, Z_ONE)


def rational(p: int, q: int) -> Rational:
    return Rational(integer(p), integer(q))


def n2r(x: NaturalNumber) -> Rational:
    return Rational(n2z(x), Z_ONE)


def z2r(x: Integer) -> Rational:
    return Rational(x, Z_ONE)


def cast2z(x: object) -> Rational:
    if isinstance(x, NaturalNumber):
        x = n2r(x)
    if isinstance(x, Integer):
        x = z2r(x)
    if not isinstance(x, Rational):
        raise TypeError(f"{repr(x)} is not an Rational, but {type(x)}")
    return x
