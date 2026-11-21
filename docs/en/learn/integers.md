<span class="lesson-number">02</span>

# How can a pair of natural numbers represent a negative number?

<p class="lesson-lead">Build integers from differences and use the multiplication you have already defined.</p>

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

Read (a,b) as a steps right and b steps left. Both (3,1) and (4,2) end at 2. Add 1 and 2 to both sides of 3−1 = 4−2 and you get 3+2 = 4+1, a test using only natural numbers.

## Equal differences form an equivalence class

The same rearrangement works for any two pairs:

<div class="peano-equation" data-reveal>
(a, b) ~ (c, d) exactly when a + d = b + c
</div>

This relation is reflexive, symmetric, and transitive, so each integer is an
equivalence class of representatives. The library deliberately stores the
chosen representative so that this construction remains visible.

<span class="lesson-layer" data-layer="representation">Representation</span>

`Integer` stores the two counts. Its `__eq__` compares a+d with b+c. To add journeys, add the rightward counts together and the leftward counts together.

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

## Multiply the pairs

To multiply (a−b)(c−d), expand and regroup: (ac+bd)−(ad+bc). The two arguments to Integer in the code below are those two groups. Every product inside is a natural-number product.

Use (0,2) for −2 and (3,0) for 3. What integer will their product display?

<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>Experiment · Multiply the pairs</span>
    <span class="peano-runner__status" data-role="status">Ready</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="Editable Python: Multiply the pairs"
    spellcheck="false">from peano import Integer, natural_number

left = Integer(natural_number(0), natural_number(2))
right = Integer(natural_number(3), natural_number(0))
print(left * right)</textarea>
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

<details class="self-check"><summary>Check your reasoning</summary><p>The first count is 0×3+2×0 = 0; the second is 0×0+2×3 = 6. The pair (0,6) represents −6.</p></details>

Replace (0,2) with (1,3). The product is now (3,9), which still means −6. This is why choosing another pair does not change what multiplication means.

normalize() cancels matching steps and returns a pair with a zero on one side. Comparing pairs by cross-addition already works before that cancellation.

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
