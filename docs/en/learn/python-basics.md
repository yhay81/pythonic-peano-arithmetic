<span class="lesson-number">00</span>

# How does Python know what + means?

<p class="lesson-lead">Follow one addition from the + sign to a method, and find out why the answer can be used in the next sum.</p>

<div class="lesson-context" data-reveal>
  <strong>Why start here?</strong>
  <p>
    Later chapters ask you to connect a definition to <code>+</code>,
    <code>==</code>, a dataclass option, or a decorator. None of those
    connections requires guessing once Python's dispatch rules are explicit.
  </p>
</div>

<div class="lesson-goals" data-reveal>
  <strong>By the end, you can explain</strong>
  <ul>
    <li>why <code>a + b</code> normally starts at <code>a.__add__(b)</code>;</li>
    <li>how <code>@log</code> replaces a function with a wrapper;</li>
    <li>which dataclass methods are generated and which this project suppresses;</li>
    <li>why a passing test is evidence about code, not a general proof.</li>
  </ul>
</div>

<div class="implementation-bridge" data-reveal
     data-source-reference="peano/utils.py"
     data-test-reference="tests/test_utils.py">
  <strong>Source used in this chapter</strong>
  <p>
    Open the complete <a href="/assets/source/peano/utils.py">logging implementation</a>
    and <a href="/assets/source/tests/test_utils.py">its tests</a> when you need
    the context around an excerpt.
  </p>
</div>

## Create two scores

A class describes a kind of value and the operations it supports. `Score(2)` creates a score. Its `__init__` method stores 2 in `self.points`, where `self` is the score being created.

For two scores, writing `a + b` calls `a.__add__(b)`. Inside the method, `self` is the score on the left and `other` is the score on the right. The new score can take part in another sum.

The experiment adds scores of 2 and 1. If you change b to Score(4), what will (a + b).points display?

<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>Experiment · Add two scores</span>
    <span class="peano-runner__status" data-role="status">Ready</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="Editable Python: Add two scores"
    spellcheck="false">class Score:
    def __init__(self, points):
        self.points = points
    def __add__(self, other):
        return Score(self.points + other.points)

a = Score(2)
b = Score(1)
print((a + b).points)</textarea>
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

self.points remains 2 and other.points becomes 4. The new score contains 6. The dot in .points reads that stored number. Try (a + b) + b. The second + works because the first returned a score. Returning a plain integer or an answer-message pair would break that chain.

## From a plus sign to a method

For a user-defined object, `left + right` asks the left operand to handle the
operation:

```text
left + right
    ↓
left.__add__(right)
    ↓
result, or NotImplemented
```

`NotImplemented` is a special return value, not an exception. It tells Python
that this method does not know the other operand and allows reflected dispatch,
such as `right.__radd__(left)`, to continue. This becomes important when values
from different levels of the numeric tower interact.

<div class="meta-note" data-meta="operator-protocol" data-reveal>
  <strong>Notation does not hide the implementation</strong>
  <p>
    In this course, reading <code>n + m</code> means locating
    <code>type(n).__add__</code>, then following its branches.
  </p>
</div>

## A decorator changes the public callable

This is the central part of `@log`:

```python
def outer(func):
    @wraps(func)
    def inner(*args, **kwargs):
        result, message = func(*args, **kwargs)
        if logger.isEnabledFor(log_level):
            logger.log(
                log_level,
                message if isinstance(message, str) else message(),
            )
        return result
    return inner
```

Read the two names on the left of result, message = func(...). The first gets the answer. The second can hold a function instead of a string. Calling message() only when a log is wanted saves building a description that nobody will read.

Writing `@log(log_level=4)` above `__add__` is equivalent to assigning the
result of the decorator back to the same name:

```text
NaturalNumber.__add__ = log(log_level=4)(original_add)
```

The original method returns `(result, message_factory)`. Callers see `inner`,
which returns only `result`. The factory is a zero-argument function so the
message is not built when tracing is disabled.

<div class="meta-note" data-meta="decorator" data-reveal>
  <strong><code>@wraps</code> preserves identity</strong>
  <p>
    A wrapper would otherwise appear to be named <code>inner</code>.
    <code>@wraps(func)</code> preserves the original name, documentation, and a
    link to the wrapped function. This project additionally rewrites the public
    return annotation from the internal tuple type to the result type.
  </p>
</div>

## Dataclass generation is selective

```python
@dataclass(frozen=True, slots=True, eq=False, repr=False)
class NaturalNumber:
    pre: NaturalNumber | None = None
```

Here the dataclass generates initialization, but:

- `frozen=True` prevents field reassignment after construction;
- `slots=True` prevents undeclared instance fields;
- `eq=False` leaves equality to the hand-written Peano rules;
- `repr=False` leaves structural display to the library.

Other classes use `__post_init__` to validate generated initialization.
`Polynomial` uses `init=False` and writes its own initializer because
normalization must happen before coefficients are stored.

<div class="meta-note" data-meta="dataclass" data-reveal>
  <strong>Generated code is still part of the design</strong>
  <p>
    Each option decides which behavior Python supplies and which behavior must
    remain visible in the mathematical implementation.
  </p>
</div>

## Tests check executable claims

The logging tests inspect both the public signature and the emitted trace:

```python
def test_decorator_preserves_method_metadata(self) -> None:
    self.assertEqual(N_ONE.__add__.__name__, "__add__")
    self.assertTrue(hasattr(N_ONE.__add__, "__wrapped__"))
```

<div class="meta-note" data-meta="test-api" data-reveal>
  <strong>Test and theorem are different claims</strong>
  <p>
    This test can detect a broken wrapper for the specific implementation.
    It does not prove a property of all decorators. Later arithmetic tests have
    the same boundary: they protect representative laws without replacing a
    proof by induction.
  </p>
</div>

<div class="learning-prompt" data-kind="prediction" data-reveal>
  <strong>Predict the call boundary</strong>
  <p>
    If an internal decorated method returns <code>(3, message_factory)</code>,
    what does the caller receive, and when is the factory invoked?
  </p>
</div>

<form class="knowledge-check" data-reveal>
  <fieldset>
    <legend>What is the main job of <code>@log</code> here?</legend>
    <label><input type="radio" name="python-check" data-correct data-feedback="It separates the public value from optional observation."> Return the value while optionally recording an explanation</label>
    <label><input type="radio" name="python-check" data-feedback="The arithmetic still runs in the original method."> Replace recursive arithmetic with faster arithmetic</label>
    <label><input type="radio" name="python-check" data-feedback="Dataclass options control immutability."> Make every numeric class immutable</label>
  </fieldset>
  <button type="submit">Check</button>
  <p data-role="feedback" aria-live="polite"></p>
</form>

You now have the vocabulary needed to read the first construction without
assuming any prior knowledge of its source.

[Next: construct natural numbers from zero and successor →](natural-numbers.md)
