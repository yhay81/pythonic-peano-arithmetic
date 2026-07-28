# Implementation reference

These are source snapshots from the same working tree used to build the wheel
installed by the browser runner.

| Topic | Implementation | Tests |
| --- | --- | --- |
| logging decorator | [`peano/utils.py`](/assets/source/peano/utils.py) | [`tests/test_utils.py`](/assets/source/tests/test_utils.py) |
| natural numbers | [`peano/natural_number.py`](/assets/source/peano/natural_number.py) | [`tests/test_natural_number.py`](/assets/source/tests/test_natural_number.py) |
| integers | [`peano/integer.py`](/assets/source/peano/integer.py) | [`tests/test_integer.py`](/assets/source/tests/test_integer.py) |
| rationals | [`peano/rational.py`](/assets/source/peano/rational.py) | [`tests/test_rational.py`](/assets/source/tests/test_rational.py) |
| polynomials | [`peano/polynomial.py`](/assets/source/peano/polynomial.py) | [`tests/test_polynomial.py`](/assets/source/tests/test_polynomial.py) |
| algebraic roots | [`peano/algebraic_root.py`](/assets/source/peano/algebraic_root.py) | [`tests/test_algebraic_root.py`](/assets/source/tests/test_algebraic_root.py) |
| cross-type contracts | — | [`tests/test_numeric_tower.py`](/assets/source/tests/test_numeric_tower.py) |

## How to read the decorator

```text
original operation returns (result, message_factory)
    ↓
@log replaces the public callable with inner
    ↓
inner records message_factory() only when enabled
    ↓
the caller receives result
```

The log level is an internal filter, not a recursion depth or proof step.
Default output therefore shows a rule name and expression without the numeric
level. For debugging the logging system itself, opt in:

```python
config_log(
    log_level=4,
    fmt="Level %(levelno)s: %(message)s",
)
```

Read a chapter's local excerpt first. Use these complete files when you need
surrounding methods, coercion helpers, or the full test context.
