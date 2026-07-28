# Pythonic Peano Arithmetic

An educational Python library that constructs natural numbers, integers,
rational numbers, and polynomials from simple definitions, then uses rational
intervals to study algebraic real roots.

The implementation is intentionally small and explicit. Its purpose is to make
the correspondence between a mathematical definition and executable Python
visible—not to compete with Python's built-in numeric types.

The interactive course runs entirely in the browser with Zensical and Pyodide:

- [English course](https://peano.yusuke-hayashi.com/en/)
- [日本語の教材](https://peano.yusuke-hayashi.com/)

## What you can observe

- natural numbers built from `0` and the successor operation;
- recursive definitions of addition and multiplication;
- integers as equivalence classes of pairs of natural numbers;
- rationals as equivalence classes of integer pairs;
- polynomials as finite coefficient sequences;
- Sturm sequences and bisection over rational isolating intervals;
- Python mechanisms that connect notation to implementation: special methods,
  decorators, frozen dataclasses, coercion, and operator dispatch.

## Install

Python 3.10 or later is required.

```bash
pip install pythonic-peano-arithmetic
```

For repository development, install
[uv](https://docs.astral.sh/uv/) and run:

```bash
git clone https://github.com/yhay81/pythonic-peano-arithmetic.git
cd pythonic-peano-arithmetic
make install
make check
```

## A five-minute tour

### Natural numbers: follow the recursive definition

```python
from peano import natural_number
from peano.utils import config_log

config_log(log_level=4)
two = natural_number(2)
one = natural_number(1)
print(two + one)
```

The trace names the rule used at each step:

```text
[addition: base] add(S(S(0)), 0) -> S(S(0))
[addition: recursive] add(S(S(0)), S(0)) -> S(add(S(S(0)), 0))
3
```

These two lines correspond directly to:

```text
n + 0    = n
n + S(m) = S(n + m)
```

Pass `locale="ja"` to `config_log` to show Japanese rule labels.

### Integers: equality of representatives

An integer is represented by a pair `(a, b)`, read as `a - b`. Different pairs
can represent the same integer:

```python
from peano import integer

print(integer(3, 1) == integer(4, 2))
```

The implementation checks the defining equivalence:

```text
(a, b) ~ (c, d)  exactly when  a + d = b + c
```

### Rationals: equality by cross multiplication

```python
from peano import rational

print(rational(1, 2) == rational(2, 4))
```

This follows the definition `p/q ~ r/s` exactly when `p*s = q*r`.

### Algebraic real roots: approach √2 with rational intervals

```python
from peano import Polynomial, Q_ONE, Q_ZERO, algebraic_root, rational

x_squared_minus_two = Polynomial(rational(-2, 1), Q_ZERO, Q_ONE)
root = algebraic_root(x_squared_minus_two, (1, 1), (2, 1))

for interval in root.trace(5):
    print(interval)
```

Every endpoint remains rational. The intervals are nested, their widths halve,
and each interval still isolates the positive root of `x² - 2`.

## Definition-to-implementation map

| Mathematical idea | Python implementation |
| --- | --- |
| zero and successor `S(n)` | `NaturalNumber`, `successor` |
| `0` differs from every successor | `NaturalNumber.__eq__` |
| successor is injective | `NaturalNumber.__eq__` |
| `n + 0 = n`, `n + S(m) = S(n + m)` | `NaturalNumber.__add__` |
| `n × 0 = 0`, `n × S(m) = n + n × m` | `NaturalNumber.__mul__` |
| `(a,b) ~ (c,d) ↔ a+d=b+c` | `Integer.__eq__` |
| `p/q ~ r/s ↔ ps=qr` | `Rational.__eq__` |
| coefficient sequence `(a₀,a₁,...)` | `Polynomial` |
| distinct roots in an interval | `sturm_sequence`, `count_real_roots` |
| one algebraic root | `AlgebraicRoot`, `RationalInterval` |

Mathematical induction is a proof principle, not a test performed by Python.
The finite tests check representative laws and guard the intended mapping
between the definitions and code.

## Logging

Operations return ordinary values. Internally, selected methods return a value
and a lazily constructed explanation; the `@log` decorator exposes only the
value and emits the explanation when logging is enabled.

```python
from peano.utils import config_log

config_log(
    log_level=4,
    max_lines=200,
    # fmt="Level %(levelno)s: %(message)s",  # expose internal levels if needed
)
```

Lower log levels reveal more detail. The numeric levels are an internal filter,
so the default display emphasizes rule names instead.

## Numeric tower and canonical forms

Mixed operations promote values through:

```text
NaturalNumber → Integer → Rational → Polynomial
```

Canonicalization keeps equivalent representatives predictable:

- `Integer.normalize()` moves a pair toward `(a-b, 0)` or `(0, b-a)`;
- `Rational.reduction()` makes the denominator positive and divides by the GCD;
- `Polynomial` removes trailing zero coefficients.

Equal values have equal hashes even when represented at different levels of the
numeric tower.

## Scope and limits

This project favors definitions that can be read over efficient arithmetic.
Keep examples small:

| Operation | Suggested values |
| --- | --- |
| natural-number comparison/addition | 0–10 |
| natural-number multiplication/division/powers | 0–5 |
| integer, rational, and polynomial components | absolute values up to 5 |
| algebraic-root tracing | roughly 12 bisections |

`AlgebraicRoot` is deliberately not a complete algebraic-number type. It
validates one isolated root and shrinks its rational interval, but provides no
arithmetic between roots and no general mathematical equality.

For interval refinement, sign checks use Python's arbitrary-precision integer
ratios internally. This preserves exactness while avoiding enormous
intermediate Peano representations; returned endpoints are still `Rational`.

## Documentation development

```bash
make docs          # build Japanese at / and English at /en/
make docs-serve    # preview Japanese
make docs-serve-en # preview English
make docs-a11y     # run WCAG checks on both languages
```

The site is deployed from `main` to Cloudflare Workers Static Assets. Deployment
requires `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` repository secrets.

## Release

Releases are built by GitHub Actions and published to PyPI with OpenID Connect.
The `pypi` GitHub environment must be registered as a PyPI Trusted Publisher
for this repository and `.github/workflows/publish.yml`.

## License

[MIT](LICENSE)
