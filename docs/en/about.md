# Course and implementation

This course reads a public Python library as an executable construction of
number systems. Its sequence is:

1. natural numbers from zero and successor;
2. integers from pairs of natural numbers;
3. rationals from pairs of integers;
4. polynomials from rational coefficient sequences;
5. one algebraic real root from a polynomial and a rational interval.

Each chapter follows definition, representation, implementation, trace, test,
and boundary. Concrete tests protect the intended implementation, but a finite
test suite is not a mathematical proof.

## Where Python carries mathematical meaning

| Python mechanism | Use in this library | Meaning |
| --- | --- | --- |
| `__add__`, `__eq__` | operator dispatch | connect notation to a defining operation |
| `@dataclass` | fields and generated initialization | declare the data that represents a value |
| `frozen=True` | prohibit reassignment | values do not change after construction |
| `eq=False`, `repr=False` | suppress generated behavior | implement mathematical equality and structural display explicitly |
| `init=False` | custom polynomial initialization | normalize coefficients before storage |
| `__post_init__` | validate a newly created value | enforce representation invariants |
| `@property` | interval width and midpoint | derive state instead of storing duplicates |
| `@total_ordering` | synthesize comparison methods | keep one ordering definition authoritative |
| `NotImplemented` | decline unsupported operands | allow Python's reflected dispatch to continue |
| `@log` and `@wraps` | wrap operations | expose a value while optionally recording the rule used |

The logging decorator is intentionally metaprogramming, not incidental
plumbing. An internal operation returns `(result, message_factory)`. The
decorated public operation returns only `result`, preserves metadata, and
evaluates the explanation only when logging is enabled.

## The browser runtime

Zensical builds the course. Pyodide runs Python as WebAssembly inside a Web
Worker. A wheel built from the same source tree is installed into that runtime.
Source links in each lesson are snapshots from that tree, so the prose,
interactive code, and linked implementation are checked together.

Code entered in a runner stays in the browser. Runners stop after five seconds
and traces are normally limited to 200 lines because this implementation favors
readable definitions over performance.

## Deliberate design choices

- Integer and rational representatives are not normalized on construction, so
  equivalent but structurally different representatives remain observable.
- Polynomial trailing zero coefficients are removed because they do not add a
  useful equivalence-class lesson here.
- Root refinement uses exact Python integer ratios for sign checks to avoid
  constructing enormous Peano intermediates.
- `AlgebraicRoot` isolates and refines one root; it is not a complete
  algebraic-number field.

Continue with the [implementation reference](reference/implementation.md) or
the [first lesson](learn/python-basics.md).
