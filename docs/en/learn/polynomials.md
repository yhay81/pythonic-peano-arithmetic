<span class="lesson-number">04</span>

# How many numbers make x²−2 zero?

<p class="lesson-lead">Evaluate a polynomial using fractions, then count its roots. A root is an input that makes the result zero.</p>

<div class="lesson-context" data-reveal>
  <strong>What we already know</strong>
  <p>
    Rational values have exact equality and arithmetic. They can therefore act
    as coefficients without introducing floating-point approximation.
  </p>
</div>

<div class="lesson-goals" data-reveal>
  <strong>By the end, you can</strong>
  <ul>
    <li>map a coefficient sequence to a polynomial;</li>
    <li>explain why a custom initializer removes trailing zeroes;</li>
    <li>follow Horner evaluation and the construction of a Sturm sequence;</li>
    <li>state what Sturm's theorem contributes to the next chapter.</li>
  </ul>
</div>

<div class="implementation-bridge" data-reveal
     data-source-reference="peano/polynomial.py"
     data-test-reference="tests/test_polynomial.py">
  <strong>Read beside this chapter</strong>
  <p>
    <a href="/assets/source/peano/polynomial.py">Polynomial source</a> and
    <a href="/assets/source/tests/test_polynomial.py">polynomial tests</a>.
  </p>
</div>

<span class="lesson-layer" data-layer="definition">Definition</span>

At 1, x²−2 is −1; at 2 it is 2. The graph is continuous, so it crosses zero somewhere in between. A sign change alone does not tell us how many crossings there are.

The sequence `(a₀, a₁, a₂)` means `a₀ + a₁x + a₂x²`. Coefficients start at the
constant term. Addition combines matching positions; multiplication performs
coefficient convolution. Substitution uses Horner's identity:

```text
a₀ + a₁x + a₂x² = (a₂x + a₁)x + a₀
```

<span class="lesson-layer" data-layer="representation">Representation</span>

Store coefficients from lowest to highest power: (−2,0,1) means −2+0x+1x². Dropping the middle zero would change the expression to x−2. Each pair in polynomial(...) writes one coefficient as a fraction.

```python
@dataclass(frozen=True, slots=True, init=False, eq=False, repr=False)
class Polynomial:
    _coefficients: tuple[Rational, ...]

    def __init__(self, *coefficients: Rational) -> None:
        if not coefficients:
            coefficients = (Q_ZERO,)
        if any(not isinstance(value, Rational) for value in coefficients):
            raise TypeError("Polynomial coefficients must be Rational")

        normalized = [value.reduction() for value in coefficients]
        while len(normalized) > 1 and normalized[-1] == Q_ZERO:
            normalized.pop()
        object.__setattr__(self, "_coefficients", tuple(normalized))
```

`init=False` suppresses dataclass initialization. The custom method reduces
coefficients and removes trailing zeroes, so `(1,2)` and `(1,2,0)` cannot remain
two stored forms of the same polynomial. Because the dataclass is frozen,
`object.__setattr__` is used only during controlled construction.

<div class="meta-note" data-meta="custom-init" data-reveal>
  <strong>Why normalize here but not earlier number systems?</strong>
  <p>
    Multiple integer and rational representatives teach equivalence classes.
    A trailing zero teaches no new construction, so canonical storage makes
    polynomial algorithms and equality clearer.
  </p>
</div>

<span class="lesson-layer" data-layer="implementation">Implementation</span>

```python
@log(log_level=31)
def evaluate(self, value: object) -> tuple[Rational, LogMessage]:
    point = cast2r(value)
    result = Q_ZERO
    for coefficient in reversed(self.coefficients):
        result = (result * point + coefficient).reduction()
    return result, lambda: f"{self!r}: x={point!r} -> {result!r}"
```

For `x² - 2`, coefficients are `(-2, 0, 1)`. At `x=1`, Horner's loop moves
from 1 to 1 to -1, so the polynomial is negative. At `x=2`, it is positive.

## Counting roots, not merely detecting a sign change

A sign change guarantees at least one root for a continuous polynomial, but
not exactly one. The implementation uses a Sturm sequence:

```python
def sturm_sequence(value: Polynomial) -> tuple[Polynomial, ...]:
    if not isinstance(value, Polynomial):
        raise TypeError("sturm_sequence expects a Polynomial")
    if value.degree <= 0:
        raise ValueError("a constant polynomial has no Sturm sequence")

    square_free = value.square_free()
    sequence = [square_free, square_free.derivative()]
    while sequence[-1]:
        remainder = sequence[-2] % sequence[-1]
        if not remainder:
            break
        sequence.append(-remainder)
    return tuple(sequence)
```

Sturm's theorem says that, when endpoints are not roots, the difference in sign
variation counts at the endpoints equals the number of distinct real roots in
the open interval. The course uses the theorem; it does not prove it.

<span class="lesson-layer" data-layer="trace">Trace</span>

<div class="learning-prompt" data-kind="prediction" data-reveal>
  <strong>Predict two exact values</strong>
  <p>
    Evaluate <code>x² - 2</code> at 1 and 2 by Horner's loop. What do their
    signs imply, and what extra claim requires the Sturm count?
  </p>
</div>

<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>Experiment 4 · Evaluation and root count</span>
    <span class="peano-runner__status" data-role="status">Not run</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="Python code evaluating a polynomial and counting roots" spellcheck="false">from peano import Polynomial, Q_ONE, Q_ZERO, config_log
from peano import count_real_roots, rational

config_log(log_level=31, max_lines=200)

polynomial = Polynomial(rational(-2, 1), Q_ZERO, Q_ONE)
lower = rational(1, 1)
upper = rational(2, 1)

print(polynomial.evaluate(lower))
print(polynomial.evaluate(upper))
print(count_real_roots(polynomial, lower, upper))</textarea>
  <div class="peano-runner__controls">
    <button class="peano-runner__button peano-runner__button--run" data-action="run">▶ Run</button>
    <button class="peano-runner__button" data-action="reset">Reset runtime</button>
    <span class="peano-runner__shortcut">⌘ / Ctrl + Enter</span>
  </div>
  <div class="peano-runner__output-wrap">
    <span class="peano-runner__output-label">Output</span>
    <pre class="peano-runner__output" data-role="output" aria-live="polite">Separate endpoint signs from the root-count claim.</pre>
  </div>
</div>

<span class="lesson-layer" data-layer="test">Test</span>

Tests cover coefficient normalization, arithmetic, long division, derivatives,
GCD, square-free parts, Sturm sequences, and root counts. Testing a known
polynomial checks the implementation; Sturm's theorem supplies the general
mathematical bridge from variations to roots.

<span class="lesson-layer" data-layer="boundary">Boundary</span>

`sign_at` maps rational values to Python's exact arbitrary-precision integer
ratios for performance. No floating-point approximation is introduced. The
mapping is a documented implementation boundary that avoids enormous unary
intermediates during interval refinement.

## Count roots on both sides of zero

evaluate reads the list backwards, multiplying the running value by x and then adding the next coefficient. For x = 3/2 the values are 1, 3/2, then 9/4−2 = 1/4. This is Horner's method.

How many distinct roots will the program count between −2 and 2?

<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>Experiment · Count roots on both sides of zero</span>
    <span class="peano-runner__status" data-role="status">Ready</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="Editable Python: Count roots on both sides of zero"
    spellcheck="false">from peano import count_real_roots, polynomial, rational, sign_variations, sturm_sequence

p = polynomial((-2, 1), (0, 1), (1, 1))
x = rational(3, 2)
print(x, p.evaluate(x))

left = rational(-2, 1)
right = rational(2, 1)
sequence = sturm_sequence(p)
for point in (left, right):
    print(point, sign_variations(sequence, point))
print(count_real_roots(p, left, right))</textarea>
  <div class="peano-runner__controls">
    <button class="peano-runner__button peano-runner__button--run"
      data-action="run">▶ Run</button>
    <button class="peano-runner__button"
      data-action="reset">Reset</button>
    <span class="peano-runner__shortcut">⌘ / Ctrl + Enter</span>
  </div>
  <div class="peano-runner__output-wrap">
    <span class="peano-runner__output-label">Output</span>
    <pre class="peano-runner__output" data-role="output"
      aria-live="polite">Run the example to see the result.</pre>
  </div>
</div>

<details class="self-check"><summary>Check your reasoning</summary><p>For x²−2 the Sturm sequence is x²−2, 2x, 2. At −2 its signs are +,−,+ (two changes); at 2 they are +,+,+ (none). The difference is 2. Between 1 and 2 the difference is 1.</p></details>

The second expression, 2x, is the derivative: when x increases by h, the square changes by 2xh+h²; dividing by h gives 2x+h, approaching 2x. Dividing x²−2 by 2x leaves −2. Negating that remainder gives the last expression, 2.

Sturm's theorem justifies subtracting these counts when neither endpoint is a root. Skip zeros when counting adjacent signs. sign_at uses exact fractions, so rounding cannot change a sign near zero.

<form class="knowledge-check" data-reveal>
  <fieldset>
    <legend>Why is a sign change alone insufficient for an isolating interval?</legend>
    <label><input type="radio" name="polynomial-check" data-correct data-feedback="An odd number of roots could produce the same endpoint signs."> It establishes existence, not that exactly one distinct root lies inside</label>
    <label><input type="radio" name="polynomial-check" data-feedback="Rational signs are exact."> Rational evaluation can only approximate a sign</label>
    <label><input type="radio" name="polynomial-check" data-feedback="Polynomials are continuous."> The intermediate value theorem does not apply to polynomials</label>
  </fieldset>
  <button type="submit">Check</button>
  <p data-role="feedback" aria-live="polite"></p>
</form>

[Next: isolate and refine one algebraic real root →](algebraic-roots.md)
