<span class="lesson-number">01</span>

# Natural numbers from zero and successor

<p class="lesson-lead">
  Represent every natural number as either zero or the successor of a natural
  number, then read equality and addition directly from those cases.
</p>

<div class="lesson-context" data-reveal>
  <strong>What we already know</strong>
  <p>
    Python sends <code>+</code> and <code>==</code> to special methods.
    <code>@log</code> wraps a method and records its message after the method
    has returned.
  </p>
</div>

<div class="lesson-goals" data-reveal>
  <strong>By the end, you can</strong>
  <ul>
    <li>distinguish Peano axioms from recursive definitions of operations;</li>
    <li>map zero and successor to the <code>pre</code> field;</li>
    <li>map each equality and addition case to a branch;</li>
    <li>explain why the innermost trace line appears first.</li>
  </ul>
</div>

<div class="implementation-bridge" data-reveal
     data-source-reference="peano/natural_number.py"
     data-test-reference="tests/test_natural_number.py">
  <strong>Read beside this chapter</strong>
  <p>
    <a href="/assets/source/peano/natural_number.py">Natural-number source</a>
    and <a href="/assets/source/tests/test_natural_number.py">behavioral tests</a>.
  </p>
</div>

<span class="lesson-layer" data-layer="definition">Definition</span>

## Axioms and recursive definitions

We use these Peano ideas:

- zero is a natural number;
- every natural number `n` has a successor `S(n)`;
- zero is not a successor;
- `S(n) = S(m)` implies `n = m`;
- induction is the proof principle for properties of all natural numbers.

Addition is then specified separately by recursive equations:

<div class="peano-equation" data-reveal>
n + 0 = n<br>
n + S(m) = S(n + m)
</div>

The first equation stops recursion. The second makes the right operand one
successor smaller. These equations are definitions of addition, not additional
Peano axioms.

<span class="lesson-layer" data-layer="representation">Representation</span>

## One field stores the predecessor chain

```python
@dataclass(frozen=True, slots=True, eq=False, repr=False)
class NaturalNumber:
    pre: NaturalNumber | None = None
```

`NaturalNumber()` has `pre=None` and represents zero.
`NaturalNumber(n)` represents `S(n)`. Thus `natural_number(2)` stores the chain
`S(S(0))`; it does not store the Python integer 2 as its value.

`structural_str()` follows this chain and renders only `0` and `S`:

```python
def structural_str(self) -> str:
    depth = 0
    current = self
    while current.pre is not None:
        depth += 1
        current = current.pre
    return f"{'S(' * depth}0{')' * depth}"
```

<span class="lesson-layer" data-layer="implementation">Implementation</span>

## Equality exposes the zero and successor cases

```python
@log(log_level=1)
def __eq__(self, other: object) -> tuple[bool, LogMessage]:
    if not isinstance(other, NaturalNumber):
        return cast(bool, NotImplemented), lambda: "NotImplemented"
    left_predecessor = self.pre
    right_predecessor = other.pre
    if left_predecessor is None or right_predecessor is None:
        result = left_predecessor is None and right_predecessor is None
        return result, lambda: (
            f"{localized('[equality: zero case]', '[等値・0の場合]')} "
            f"eq({self.structural_str()}, {other.structural_str()}) -> {result}"
        )
    return left_predecessor == right_predecessor, lambda: (
        f"{localized('[equality: successor case]', '[等値・後者の場合]')} "
        f"eq({self.structural_str()}, {other.structural_str()}) -> "
        f"eq({left_predecessor.structural_str()}, "
        f"{right_predecessor.structural_str()})"
    )
```

If exactly one predecessor is `None`, zero is being compared with a successor
and the answer is false. If both values are successors, comparison moves to
their predecessors. This is the code-level correspondence to the two axioms.

## Addition mirrors its two equations

```python
@log(log_level=4)
def __add__(self, other: object) -> tuple[NaturalNumber, LogMessage]:
    if not isinstance(other, NaturalNumber):
        return cast(NaturalNumber, NotImplemented), lambda: "NotImplemented"
    predecessor = other.pre
    if predecessor is None:
        return self, lambda: (
            f"{localized('[addition: base]', '[加法・基底]')} "
            f"add({self.structural_str()}, 0) -> {self.structural_str()}"
        )
    return successor(self + predecessor), lambda: (
        f"{localized('[addition: recursive]', '[加法・再帰]')} "
        f"add({self.structural_str()}, {other.structural_str()}) -> "
        f"S(add({self.structural_str()}, {predecessor.structural_str()}))"
    )
```

`predecessor is None` implements `n + 0 = n`.
`successor(self + predecessor)` implements `n + S(m) = S(n + m)`.

<span class="lesson-layer" data-layer="trace">Trace</span>

<div class="meta-note" data-meta="log-decorator" data-reveal>
  <strong>Messages appear while calls return</strong>
  <p>
    The recursive call must finish before the wrapper receives a result and
    message. Therefore the base case is logged before the outer recursive case.
  </p>
</div>

<div class="learning-prompt" data-kind="prediction" data-reveal>
  <strong>Predict <code>2 + 2</code></strong>
  <p>
    Starting from the two branches above, write the first trace line, the last
    trace line, and the final printed value.
  </p>
</div>

<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>Experiment 1 · Recursive addition</span>
    <span class="peano-runner__status" data-role="status">Not run</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="Python code tracing natural-number addition" spellcheck="false">from peano import config_log, natural_number

config_log(log_level=4, max_lines=200)

left = natural_number(2)
right = natural_number(2)
answer = left + right

print(answer)</textarea>
  <div class="peano-runner__controls">
    <button class="peano-runner__button peano-runner__button--run" data-action="run">▶ Run</button>
    <button class="peano-runner__button" data-action="reset">Reset runtime</button>
    <span class="peano-runner__shortcut">⌘ / Ctrl + Enter</span>
  </div>
  <div class="peano-runner__output-wrap">
    <span class="peano-runner__output-label">Output</span>
    <pre class="peano-runner__output" data-role="output" aria-live="polite">Run after writing your prediction.</pre>
  </div>
</div>

<span class="lesson-layer" data-layer="test">Test</span>

The tests name the intended claims: zero is not a successor, successor is
injective, and the two recursive equations hold for selected values. They
detect implementation regressions. Induction, not enumeration by a test suite,
is what turns compatible base and successor arguments into a theorem for all
natural numbers.

<span class="lesson-layer" data-layer="boundary">Boundary</span>

Unary predecessor chains make the structure visible and arithmetic slow. Large
numbers are intentionally outside the useful range. Python's built-in `int`
appears only at input and display boundaries.

<form class="knowledge-check" data-reveal>
  <fieldset>
    <legend>Why does the base trace appear first for <code>2 + 2</code>?</legend>
    <label><input type="radio" name="natural-check" data-correct data-feedback="The decorator logs only after each wrapped call returns."> The recursive calls reach zero before their wrappers record messages</label>
    <label><input type="radio" name="natural-check" data-feedback="The right operand controls the recursive descent."> Python evaluates the left operand after the right operand</label>
    <label><input type="radio" name="natural-check" data-feedback="The numeric level only filters logs."> Level 4 reverses the output order</label>
  </fieldset>
  <button type="submit">Check</button>
  <p data-role="feedback" aria-live="polite"></p>
</form>

[Next: construct integers from pairs of natural numbers →](integers.md)
