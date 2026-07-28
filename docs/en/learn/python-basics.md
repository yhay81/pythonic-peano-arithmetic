<span class="lesson-number">00</span>

# Python mechanisms used by the library

<p class="lesson-lead">
  Basic Python syntax is assumed. This preparation chapter explains the data
  model and metaprogramming that make the mathematical notation meaningful.
</p>

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

## Operators are method dispatch

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
