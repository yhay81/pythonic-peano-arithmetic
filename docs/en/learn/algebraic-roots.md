<span class="lesson-number">05</span>

# Algebraic real roots through rational intervals

<p class="lesson-lead">
  The positive root of <code>x² - 2</code> is not rational. Identify it with a
  polynomial and an interval containing exactly one root, then shrink the
  interval without leaving exact rational arithmetic.
</p>

<div class="lesson-context" data-reveal>
  <strong>What we already know</strong>
  <p>
    Polynomials can be evaluated exactly at rational points, and a Sturm
    sequence counts distinct real roots in an open rational interval.
  </p>
</div>

<div class="lesson-goals" data-reveal>
  <strong>By the end, you can</strong>
  <ul>
    <li>state the invariants of a rational isolating interval;</li>
    <li>connect those invariants to constructor validation;</li>
    <li>follow one bisection branch from endpoint and midpoint signs;</li>
    <li>explain what this object does not implement as a number type.</li>
  </ul>
</div>

<div class="implementation-bridge" data-reveal
     data-source-reference="peano/algebraic_root.py"
     data-test-reference="tests/test_algebraic_root.py">
  <strong>Read beside this chapter</strong>
  <p>
    <a href="/assets/source/peano/algebraic_root.py">Algebraic-root source</a>
    and <a href="/assets/source/tests/test_algebraic_root.py">root tests</a>.
  </p>
</div>

<span class="lesson-layer" data-layer="definition">Definition</span>

An algebraic real number is a real root of a nonzero polynomial with integer
coefficients. This project studies one root through:

- a polynomial;
- rational endpoints `lower < upper`;
- neither endpoint being a root;
- opposite endpoint signs;
- exactly one distinct real root in the open interval.

For `x² - 2`, the interval `[1,2]` satisfies these conditions for the positive
root. The root itself is not replaced by either endpoint.

<span class="lesson-layer" data-layer="representation">Representation</span>

```python
@dataclass(frozen=True, slots=True)
class RationalInterval:
    lower: Rational
    upper: Rational

    def __post_init__(self) -> None:
        if not isinstance(self.lower, Rational) or not isinstance(
            self.upper, Rational
        ):
            raise TypeError("interval endpoints must be Rational values")
        lower_fraction = _as_fraction(self.lower)
        upper_fraction = _as_fraction(self.upper)
        if lower_fraction > upper_fraction:
            raise ValueError("lower must be less than or equal to upper")
```

The interval's `width`, `midpoint`, and `is_point` are properties derived from
the endpoints. They cannot become inconsistent stored fields.

<div class="meta-note" data-meta="property" data-reveal>
  <strong>A property exposes derived state</strong>
  <p>
    <code>interval.width</code> looks like an attribute but computes from
    immutable endpoints. The representation has one source of truth.
  </p>
</div>

<span class="lesson-layer" data-layer="implementation">Implementation</span>

`AlgebraicRoot.__post_init__` checks the full isolating contract:

```python
def __post_init__(self) -> None:
    if not isinstance(self.polynomial, Polynomial):
        raise TypeError("polynomial must be a Polynomial")
    if not isinstance(self.interval, RationalInterval):
        raise TypeError("interval must be a RationalInterval")
    if self.polynomial.degree <= 0:
        raise ValueError("a root-defining polynomial must have positive degree")
    if self.interval.is_point:
        raise ValueError("the initial interval must have positive width")

    lower_sign = self.polynomial.sign_at(self.interval.lower)
    upper_sign = self.polynomial.sign_at(self.interval.upper)
    if lower_sign == 0 or upper_sign == 0:
        raise ValueError("initial interval endpoints cannot be roots")
    if lower_sign == upper_sign:
        raise ValueError("the polynomial must change sign across the endpoints")

    number_of_roots = count_real_roots(
        self.polynomial,
        self.interval.lower,
        self.interval.upper,
    )
    if number_of_roots != 1:
        raise ValueError(
            "the initial interval must contain exactly one distinct real root "
            f"(found {number_of_roots})"
        )
```

Once construction succeeds, bisection preserves the root:

```python
def _bisect(
    polynomial_value: Polynomial,
    interval: RationalInterval,
) -> tuple[RationalInterval, LogMessage]:
    midpoint = interval.midpoint
    midpoint_sign = polynomial_value.sign_at(midpoint)
    if midpoint_sign == 0:
        result = RationalInterval(midpoint, midpoint)
    elif polynomial_value.sign_at(interval.lower) != midpoint_sign:
        result = RationalInterval(interval.lower, midpoint)
    else:
        result = RationalInterval(midpoint, interval.upper)
    return result, lambda: f"{polynomial_value!r}: {interval} -> {result}"
```

If the midpoint is exact, the interval becomes one point. Otherwise the half
whose endpoint signs differ keeps the root guaranteed by continuity. Because
the original interval contains exactly one root, the retained half still
identifies that same root.

<span class="lesson-layer" data-layer="trace">Trace</span>

<div class="learning-prompt" data-kind="prediction" data-reveal>
  <strong>Predict the first interval</strong>
  <p>
    The midpoint of <code>[1,2]</code> is <code>3/2</code>.
    Evaluate <code>x²-2</code> there and decide which half remains.
  </p>
</div>

<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>Experiment 5 · Refine √2</span>
    <span class="peano-runner__status" data-role="status">Not run</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="Python code refining the positive square root of two" spellcheck="false">from peano import Polynomial, Q_ONE, Q_ZERO, algebraic_root
from peano import config_log, rational

config_log(log_level=41, max_lines=200)

polynomial = Polynomial(rational(-2, 1), Q_ZERO, Q_ONE)
root = algebraic_root(polynomial, (1, 1), (2, 1))

for interval in root.trace(5):
    print(interval, "width =", interval.width)</textarea>
  <div class="peano-runner__controls">
    <button class="peano-runner__button peano-runner__button--run" data-action="run">▶ Run</button>
    <button class="peano-runner__button" data-action="reset">Reset runtime</button>
    <span class="peano-runner__shortcut">⌘ / Ctrl + Enter</span>
  </div>
  <div class="peano-runner__output-wrap">
    <span class="peano-runner__output-label">Output</span>
    <pre class="peano-runner__output" data-role="output" aria-live="polite">Check nesting, sign preservation, and halving widths.</pre>
  </div>
</div>

<span class="lesson-layer" data-layer="test">Test</span>

Tests assert that widths halve, endpoints retain opposite signs, later
intervals are nested, exact midpoints become point intervals, and invalid or
multi-root intervals are rejected. They check the code's preservation of the
documented invariant for representative cases.

<span class="lesson-layer" data-layer="boundary">Boundary</span>

`AlgebraicRoot` is an educational root-isolation object, not a complete real or
algebraic number type. It does not define arithmetic between roots or general
mathematical equality. The course stops after exposing why rational endpoints
can approach a non-rational value without ever becoming that value.

<form class="knowledge-check" data-reveal>
  <fieldset>
    <legend>What identifies the same root after each bisection?</legend>
    <label><input type="radio" name="root-check" data-correct data-feedback="The retained half preserves the isolating invariant."> The interval stays nested and retains the unique sign-changing root</label>
    <label><input type="radio" name="root-check" data-feedback="Endpoints remain rational approximations."> One endpoint eventually becomes the irrational root</label>
    <label><input type="radio" name="root-check" data-feedback="Widths shrink but never become negative."> The interval width becomes negative</label>
  </fieldset>
  <button type="submit">Check</button>
  <p data-role="feedback" aria-live="polite"></p>
</form>

[Return to the course overview →](../index.md)
