"""Construct natural numbers and their operations from zero and successor."""

from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering
from typing import TYPE_CHECKING, Iterator, cast

from .utils import LogMessage, log, translate

if TYPE_CHECKING:
    from .integer import Integer
    from .rational import Rational


@total_ordering
@dataclass(frozen=True, slots=True, eq=False, repr=False)
class NaturalNumber:
    """A natural number based on the Peano axioms.

    ``None`` represents zero and ``NaturalNumber(n)`` represents the successor
    :math:`S(n)`. Values are immutable. Addition and multiplication follow
    their recursive definitions directly.
    """

    pre: NaturalNumber | None = None

    def __post_init__(self) -> None:
        if self.pre is not None and not isinstance(self.pre, NaturalNumber):
            raise TypeError("pre must be a NaturalNumber or None")

    def __repr__(self) -> str:
        return f"<N({int(self)})>"

    def __str__(self) -> str:
        return str(int(self))

    def __int__(self) -> int:
        value = 0
        current: NaturalNumber | None = self
        while current is not None and current.pre is not None:
            value += 1
            current = current.pre
        return value

    def structural_str(self) -> str:
        """Return the structure using only zero and successor notation."""

        depth = 0
        current = self
        while current.pre is not None:
            depth += 1
            current = current.pre
        return f"{'S(' * depth}0{')' * depth}"

    @log(log_level=1)
    def __eq__(self, other: object) -> tuple[bool, LogMessage]:
        if not isinstance(other, NaturalNumber):
            return (
                cast(bool, NotImplemented),
                lambda: f"{self!r} == {other!r} = NotImplemented",
            )
        left_predecessor = self.pre
        right_predecessor = other.pre
        if left_predecessor is None or right_predecessor is None:
            result = left_predecessor is None and right_predecessor is None
            return (
                result,
                lambda: (
                    f"{translate('equality.zero')} "
                    f"eq({self.structural_str()}, "
                    f"{other.structural_str()}) -> {result}"
                ),
            )
        return (
            left_predecessor == right_predecessor,
            lambda: (
                f"{translate('equality.successor')} "
                f"eq({self.structural_str()}, "
                f"{other.structural_str()}) -> "
                f"eq({left_predecessor.structural_str()}, "
                f"{right_predecessor.structural_str()})"
            ),
        )

    @log(log_level=2)
    def __lt__(self, other: object) -> tuple[bool, LogMessage]:
        if not isinstance(other, NaturalNumber):
            return (
                cast(bool, NotImplemented),
                lambda: f"{self!r} < {other!r} = NotImplemented",
            )
        if self.pre is None:
            result = other.pre is not None
            return result, lambda: f"{self!r} < {other!r} = {result}"
        if other.pre is None:
            return False, lambda: f"{self!r} < {other!r} = False"
        return (
            self.pre < other.pre,
            lambda: f"{self!r} < {other!r} = {self.pre!r} < {other.pre!r}",
        )

    @log(log_level=2)
    def __le__(self, other: object) -> tuple[bool, LogMessage]:
        if not isinstance(other, NaturalNumber):
            return (
                cast(bool, NotImplemented),
                lambda: f"{self!r} <= {other!r} = NotImplemented",
            )
        if self.pre is None:
            return True, lambda: f"{self!r} <= {other!r} = True"
        if other.pre is None:
            return False, lambda: f"{self!r} <= {other!r} = False"
        return (
            self.pre <= other.pre,
            lambda: f"{self!r} <= {other!r} = {self.pre!r} <= {other.pre!r}",
        )

    @log(log_level=4)
    def __add__(self, other: object) -> tuple[NaturalNumber, LogMessage]:
        if not isinstance(other, NaturalNumber):
            return (
                cast(NaturalNumber, NotImplemented),
                lambda: f"{self!r} + {other!r} = NotImplemented",
            )
        predecessor = other.pre
        if predecessor is None:
            return (
                self,
                lambda: (
                    f"{translate('addition.base')} "
                    f"add({self.structural_str()}, 0) "
                    f"-> {self.structural_str()}"
                ),
            )
        return (
            successor(self + predecessor),
            lambda: (
                f"{translate('addition.recursive')} "
                f"add({self.structural_str()}, "
                f"{other.structural_str()}) -> "
                f"S(add({self.structural_str()}, {predecessor.structural_str()}))"
            ),
        )

    @log(log_level=4)
    def __sub__(self, other: object) -> tuple[NaturalNumber, LogMessage]:
        if not isinstance(other, NaturalNumber):
            return (
                cast(NaturalNumber, NotImplemented),
                lambda: f"{self!r} - {other!r} = NotImplemented",
            )
        if other.pre is None:
            return self, lambda: f"{self!r} - {other!r} = {self!r}"
        if self.pre is None:
            raise ValueError(
                "natural-number subtraction cannot produce a negative value"
            )
        return (
            self.pre - other.pre,
            lambda: f"{self!r} - {other!r} = {self.pre!r} - {other.pre!r}",
        )

    @log(log_level=5)
    def __mul__(self, other: object) -> tuple[NaturalNumber, LogMessage]:
        if not isinstance(other, NaturalNumber):
            return (
                cast(NaturalNumber, NotImplemented),
                lambda: f"{self!r} * {other!r} = NotImplemented",
            )
        predecessor = other.pre
        if predecessor is None:
            return (
                N_ZERO,
                lambda: (
                    f"{translate('multiplication.base')} "
                    f"mul({self.structural_str()}, 0) -> 0"
                ),
            )
        return (
            self + self * predecessor,
            lambda: (
                f"{translate('multiplication.recursive')} "
                f"mul({self.structural_str()}, "
                f"{other.structural_str()}) -> "
                f"add({self.structural_str()}, "
                f"mul({self.structural_str()}, {predecessor.structural_str()}))"
            ),
        )

    @log(log_level=5)
    def __truediv__(self, other: object) -> tuple[Rational, LogMessage]:
        if not isinstance(other, NaturalNumber):
            return (
                cast("Rational", NotImplemented),
                lambda: f"{self!r} / {other!r} = NotImplemented",
            )
        if other.pre is None:
            raise ZeroDivisionError("division by zero")
        from .integer import Integer
        from .rational import Rational

        result = Rational(Integer(self, N_ZERO), Integer(other, N_ZERO))
        return result, lambda: f"{self!r} / {other!r} = {result!r}"

    @log(log_level=5)
    def __floordiv__(self, other: object) -> tuple[NaturalNumber, LogMessage]:
        if not isinstance(other, NaturalNumber):
            return (
                cast(NaturalNumber, NotImplemented),
                lambda: f"{self!r} // {other!r} = NotImplemented",
            )
        if not other:
            raise ZeroDivisionError("division by zero")
        if self < other:
            return N_ZERO, lambda: f"{self!r} // {other!r} = {N_ZERO!r}"
        return (
            N_ONE + ((self - other) // other),
            lambda: (
                f"{self!r} // {other!r} = "
                f"{N_ONE!r} + (({self!r} - {other!r}) // {other!r})"
            ),
        )

    @log(log_level=5)
    def __mod__(self, other: object) -> tuple[NaturalNumber, LogMessage]:
        if not isinstance(other, NaturalNumber):
            return (
                cast(NaturalNumber, NotImplemented),
                lambda: f"{self!r} % {other!r} = NotImplemented",
            )
        if not other:
            raise ZeroDivisionError("division by zero")
        if self < other:
            return self, lambda: f"{self!r} % {other!r} = {self!r}"
        return (
            (self - other) % other,
            lambda: f"{self!r} % {other!r} = ({self!r} - {other!r}) % {other!r}",
        )

    def __divmod__(self, other: object) -> tuple[NaturalNumber, NaturalNumber]:
        if not isinstance(other, NaturalNumber):
            return cast(tuple[NaturalNumber, NaturalNumber], NotImplemented)
        return self // other, self % other

    @log(log_level=6)
    def __pow__(self, exponent: object) -> tuple[NaturalNumber, LogMessage]:
        if not isinstance(exponent, NaturalNumber):
            return (
                cast(NaturalNumber, NotImplemented),
                lambda: f"{self!r} ** {exponent!r} = NotImplemented",
            )
        if exponent.pre is None:
            return N_ONE, lambda: f"{self!r} ** {exponent!r} = {N_ONE!r}"
        return (
            (self**exponent.pre) * self,
            lambda: (
                f"{self!r} ** S({exponent.pre!r}) = "
                f"({self!r} ** {exponent.pre!r}) * {self!r}"
            ),
        )

    def __bool__(self) -> bool:
        return self.pre is not None

    def __hash__(self) -> int:
        return hash(int(self))

    def __pos__(self) -> NaturalNumber:
        return self

    def __neg__(self) -> Integer:
        from .integer import Integer

        return Integer(N_ZERO, self)

    def __abs__(self) -> NaturalNumber:
        return self

    def __iter__(self) -> Iterator[NaturalNumber]:
        current = N_ZERO
        while current != self:
            yield current
            current = successor(current)

    def __reversed__(self) -> Iterator[NaturalNumber]:
        current = self
        while current.pre is not None:
            current = current.pre
            yield current

    def set_repr(self) -> frozenset[object]:
        """Return the von Neumann ordinal representation."""

        if self.pre is None:
            return frozenset()
        predecessor = self.pre.set_repr()
        return frozenset((predecessor,)) | predecessor

    def set_str(self) -> str:
        return (
            str(self.set_repr())
            .replace("{", "")
            .replace("}", "")
            .replace("frozenset(", "{")
            .replace(")", "}")
        )


def successor(number: NaturalNumber) -> NaturalNumber:
    """Return the successor :math:`S(n)`."""

    if not isinstance(number, NaturalNumber):
        raise TypeError("successor expects a NaturalNumber")
    return NaturalNumber(number)


def natural_number(value: int) -> NaturalNumber:
    """Construct a natural number from a non-negative Python integer."""

    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("only int values can be converted to NaturalNumber")
    if value < 0:
        raise ValueError("negative values cannot be converted to NaturalNumber")
    result = N_ZERO
    for _ in range(value):
        result = successor(result)
    return result


def cast2n(value: object) -> NaturalNumber:
    """Validate and return a ``NaturalNumber``."""

    if not isinstance(value, NaturalNumber):
        raise TypeError(f"{value!r} is not a NaturalNumber")
    return value


N_ZERO = NaturalNumber()
N_ONE = NaturalNumber(N_ZERO)
