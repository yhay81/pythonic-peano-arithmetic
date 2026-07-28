<span class="lesson-number">02</span>

# Integers as differences

<p class="lesson-lead">
  A pair of natural numbers <code>(a, b)</code> represents the difference
  <code>a - b</code>. Equality must compare represented differences, not fields.
</p>

<div class="lesson-context" data-reveal>
  <strong>What we already know</strong>
  <p>
    Natural numbers are immutable predecessor chains, and their equality and
    addition follow explicit zero/successor cases.
  </p>
</div>

<div class="lesson-goals" data-reveal>
  <strong>By the end, you can</strong>
  <ul>
    <li>explain why multiple pairs represent the same integer;</li>
    <li>derive the cross-sum equality rule;</li>
    <li>explain why <code>eq=False</code> is necessary;</li>
    <li>separate a representative from its normalized form.</li>
  </ul>
</div>

<div class="implementation-bridge" data-reveal
     data-source-reference="peano/integer.py"
     data-test-reference="tests/test_integer.py">
  <strong>Read beside this chapter</strong>
  <p>
    <a href="/assets/source/peano/integer.py">Integer source</a> and
    <a href="/assets/source/tests/test_integer.py">integer tests</a>.
  </p>
</div>

<span class="lesson-layer" data-layer="definition">Definition</span>

## Equal differences form an equivalence class

If `(a, b)` means `a - b`, then `(3, 1)` and `(4, 2)` both mean 2. Avoiding
subtraction gives a rule stated entirely with the natural-number addition we
already constructed:

<div class="peano-equation" data-reveal>
(a, b) ~ (c, d) exactly when a + d = b + c
</div>

This relation is reflexive, symmetric, and transitive, so each integer is an
equivalence class of representatives. The library deliberately stores the
chosen representative so that this construction remains visible.

<span class="lesson-layer" data-layer="representation">Representation</span>

```python
@dataclass(frozen=True, slots=True, eq=False, repr=False)
class Integer:
    a: NaturalNumber
    b: NaturalNumber

    def __post_init__(self) -> None:
        if not isinstance(self.a, NaturalNumber) or not isinstance(
            self.b, NaturalNumber
        ):
            raise TypeError(
                "Integer.a and Integer.b must be NaturalNumber values"
            )
```

Generated field equality would make `(3,1) != (4,2)`. `eq=False` prevents that
incorrect rule and leaves equality to the hand-written method.

<span class="lesson-layer" data-layer="implementation">Implementation</span>

```python
@log(log_level=11)
def __eq__(self, other: object) -> tuple[bool, LogMessage]:
    converted = _coerce_integer(other)
    if converted is None:
        return cast(bool, NotImplemented), lambda: "NotImplemented"
    result = self.a + converted.b == self.b + converted.a
    return result, lambda: (
        f"{self!r} == {converted!r} ⇔ "
        f"{self.a!r} + {converted.b!r} == "
        f"{self.b!r} + {converted.a!r}"
    )
```

The line computing `result` is the defining equation with fields substituted
directly. `_coerce_integer` lets a natural number participate by embedding `n`
as `(n, 0)`. An unrelated type returns `NotImplemented` and remains Python's
dispatch problem.

Addition is componentwise:

```text
(a, b) + (c, d) = (a + c, b + d)
```

Multiplication follows expansion of `(a-b)(c-d)`:

```text
(a, b) × (c, d) = (ac + bd, ad + bc)
```

<div class="meta-note" data-meta="dataclass-equality" data-reveal>
  <strong>Equality belongs to represented values</strong>
  <p>
    Frozen fields make a representative stable. The custom
    <code>__eq__</code> decides whether two stable representatives belong to
    the same equivalence class.
  </p>
</div>

<span class="lesson-layer" data-layer="trace">Trace</span>

<div class="learning-prompt" data-kind="prediction" data-reveal>
  <strong>Predict the two cross-sums</strong>
  <p>
    For <code>(3,1) == (4,2)</code>, write the two natural-number sums that
    <code>Integer.__eq__</code> compares.
  </p>
</div>

<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>Experiment 2 · Equality of representatives</span>
    <span class="peano-runner__status" data-role="status">Not run</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="Python code checking integer representatives" spellcheck="false">from peano import Integer, config_log, natural_number

config_log(log_level=11, max_lines=200)

left = Integer(natural_number(3), natural_number(1))
right = Integer(natural_number(4), natural_number(2))

print(left == right)
print(left.normalize(), right.normalize())</textarea>
  <div class="peano-runner__controls">
    <button class="peano-runner__button peano-runner__button--run" data-action="run">▶ Run</button>
    <button class="peano-runner__button" data-action="reset">Reset runtime</button>
    <span class="peano-runner__shortcut">⌘ / Ctrl + Enter</span>
  </div>
  <div class="peano-runner__output-wrap">
    <span class="peano-runner__output-label">Output</span>
    <pre class="peano-runner__output" data-role="output" aria-live="polite">Compare the logged cross-sums with the definition.</pre>
  </div>
</div>

At level 11 the trace emphasizes integer equality. Lowering the threshold to 4
also exposes the natural-number additions used to build the cross-sums; it does
not change the answer.

<span class="lesson-layer" data-layer="test">Test</span>

Tests compare unequal representatives of the same value and check that
operations respect equality. Those are executable checks of well-definedness
for selected inputs. The general claim still requires showing that changing
representatives cannot change an operation's equivalence class.

<span class="lesson-layer" data-layer="boundary">Boundary</span>

`normalize()` chooses `(n,0)` for nonnegative values or `(0,n)` for negative
values. Construction does not call it automatically. Keeping both `(3,1)` and
`(4,2)` intact is an educational choice, not a mathematical requirement.

<form class="knowledge-check" data-reveal>
  <fieldset>
    <legend>Why is generated dataclass equality unsuitable?</legend>
    <label><input type="radio" name="integer-check" data-correct data-feedback="Representatives can differ while their cross-sums agree."> It compares fields rather than represented differences</label>
    <label><input type="radio" name="integer-check" data-feedback="The fields remain frozen natural numbers."> It would allow fields to be changed</label>
    <label><input type="radio" name="integer-check" data-feedback="Dataclass initialization is still used."> It cannot initialize two fields</label>
  </fieldset>
  <button type="submit">Check</button>
  <p data-role="feedback" aria-live="polite"></p>
</form>

[Next: construct rational numbers from pairs of integers →](rationals.md)
