<span class="lesson-number">03</span>

# Rational numbers as ratios

<p class="lesson-lead">
  A pair of integers <code>(p, q)</code>, with <code>q ≠ 0</code>, represents
  the ratio <code>p/q</code>. Cross multiplication defines equality.
</p>

<div class="lesson-context" data-reveal>
  <strong>What we already know</strong>
  <p>
    Integers are equivalence classes of natural-number pairs. Their operations
    are available before we use them as numerators and denominators.
  </p>
</div>

<div class="lesson-goals" data-reveal>
  <strong>By the end, you can</strong>
  <ul>
    <li>derive rational equality and addition from integer operations;</li>
    <li>identify the invariant enforced by <code>__post_init__</code>;</li>
    <li>explain why reduction is explicit rather than automatic;</li>
    <li>explain equality and hashing across equivalent representatives.</li>
  </ul>
</div>

<div class="implementation-bridge" data-reveal
     data-source-reference="peano/rational.py"
     data-test-reference="tests/test_rational.py">
  <strong>Read beside this chapter</strong>
  <p>
    <a href="/assets/source/peano/rational.py">Rational source</a> and
    <a href="/assets/source/tests/test_rational.py">rational tests</a>.
  </p>
</div>

<span class="lesson-layer" data-layer="definition">Definition</span>

For nonzero denominators:

<div class="peano-equation" data-reveal>
p/q ~ r/s exactly when p·s = q·r
</div>

Addition and multiplication are:

```text
p/q + r/s = (p·s + q·r)/(q·s)
(p/q)·(r/s) = (p·r)/(q·s)
```

These formulas use only operations already constructed for integers.

<span class="lesson-layer" data-layer="representation">Representation</span>

```python
@dataclass(frozen=True, slots=True, eq=False, repr=False)
class Rational:
    p: Integer
    q: Integer

    def __post_init__(self) -> None:
        if not isinstance(self.p, Integer) or not isinstance(self.q, Integer):
            raise TypeError("Rational.p and Rational.q must be Integer values")
        if self.q == Z_ZERO:
            raise ZeroDivisionError("the denominator cannot be zero")
```

The generated initializer stores the fields, then `__post_init__` rejects
values outside the representation. It does not reduce `2/4` to `1/2`; both
representatives remain available for study.

<div class="meta-note" data-meta="post-init" data-reveal>
  <strong>Validation follows generated initialization</strong>
  <p>
    The caller never invokes <code>__post_init__</code> directly. This hook
    connects dataclass-generated code to a mathematical invariant.
  </p>
</div>

<span class="lesson-layer" data-layer="implementation">Implementation</span>

```python
@log(log_level=21)
def __eq__(self, other: object) -> tuple[bool, LogMessage]:
    converted = _coerce_rational(other)
    if converted is None:
        return cast(bool, NotImplemented), lambda: "NotImplemented"
    result = self.p * converted.q == self.q * converted.p
    return result, lambda: (
        f"{self!r} == {converted!r} ⇔ "
        f"{self.p!r} * {converted.q!r} == "
        f"{self.q!r} * {converted.p!r}"
    )
```

Again, one line is the mathematical definition with fields substituted. The
addition method applies the formula above and calls `reduction()` on the
result. `reduction()` makes the denominator positive and divides numerator and
denominator by their greatest common divisor.

Hashing also uses a reduced canonical pair. Therefore `1/2` and `2/4` compare
equal and have equal hashes, as Python requires for dictionary keys and sets.

<span class="lesson-layer" data-layer="trace">Trace</span>

<div class="learning-prompt" data-kind="prediction" data-reveal>
  <strong>Predict equality without reducing</strong>
  <p>
    What two integer products does <code>1/2 == 2/4</code> compare? Why can the
    result be true even though the stored fields differ?
  </p>
</div>

<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>Experiment 3 · Cross-product equality</span>
    <span class="peano-runner__status" data-role="status">Not run</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="Python code tracing rational equality" spellcheck="false">from peano import config_log, rational

config_log(log_level=21, max_lines=200)

half = rational(1, 2)
two_quarters = rational(2, 4)

print(half == two_quarters)
print(half.reduction(), two_quarters.reduction())
print(hash(half) == hash(two_quarters))</textarea>
  <div class="peano-runner__controls">
    <button class="peano-runner__button peano-runner__button--run" data-action="run">▶ Run</button>
    <button class="peano-runner__button" data-action="reset">Reset runtime</button>
    <span class="peano-runner__shortcut">⌘ / Ctrl + Enter</span>
  </div>
  <div class="peano-runner__output-wrap">
    <span class="peano-runner__output-label">Output</span>
    <pre class="peano-runner__output" data-role="output" aria-live="polite">Read the cross-product trace before the printed booleans.</pre>
  </div>
</div>

<span class="lesson-layer" data-layer="test">Test</span>

Tests check zero-denominator rejection, equivalent representatives, arithmetic,
ordering with negative denominators, reduction, and the equality/hash contract.
They protect implementation behavior for concrete cases, while the formulas
provide the general mathematical reasoning.

<span class="lesson-layer" data-layer="boundary">Boundary</span>

Rationals contain every integer but still have gaps: there is no rational whose
square is 2. The next chapters keep rational arithmetic and use a polynomial
plus an interval to identify such a real number.

<form class="knowledge-check" data-reveal>
  <fieldset>
    <legend>Why can <code>1/2</code> equal <code>2/4</code> before reduction?</legend>
    <label><input type="radio" name="rational-check" data-correct data-feedback="Both cross products are 4."> Equality compares cross products, not stored fields</label>
    <label><input type="radio" name="rational-check" data-feedback="Construction deliberately preserves representatives."> The constructor silently reduces both values</label>
    <label><input type="radio" name="rational-check" data-feedback="Hashes follow equality; they do not define it."> Python compares only their hashes</label>
  </fieldset>
  <button type="submit">Check</button>
  <p data-role="feedback" aria-live="polite"></p>
</form>

[Next: represent polynomials as coefficient sequences →](polynomials.md)
