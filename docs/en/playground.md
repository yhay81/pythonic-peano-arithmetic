<span class="lesson-number">Playground</span>

# Test a prediction

Use this page after reading the natural-number chapter. Change one condition at
a time, and write down the definition, representation, method, expected trace,
and expected result before running the cell.

<div class="learning-prompt" data-kind="prediction" data-reveal>
  <strong>Before running</strong>
  <p>
    For <code>2 + 1</code>, how often will the base and recursive branches run?
    Which trace line appears first, and why?
  </p>
</div>

<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>Experiment · Natural-number addition</span>
    <span class="peano-runner__status" data-role="status">Not run</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="Python code for experimenting with natural-number addition" spellcheck="false">from peano import config_log, natural_number

config_log(log_level=4, max_lines=200)

left = natural_number(2)
right = natural_number(1)
answer = left + right

print(answer)</textarea>
  <div class="peano-runner__controls">
    <button class="peano-runner__button peano-runner__button--run" data-action="run">▶ Run</button>
    <button class="peano-runner__button" data-action="reset">Reset runtime</button>
    <span class="peano-runner__shortcut">⌘ / Ctrl + Enter</span>
  </div>
  <div class="peano-runner__output-wrap">
    <span class="peano-runner__output-label">Output</span>
    <pre class="peano-runner__output" data-role="output" aria-live="polite">Compare the rule order with your prediction.</pre>
  </div>
</div>

<details class="self-check" data-reveal>
  <summary>Check the prediction</summary>
  <p>
    The recursive branch calls the base case before it can return. Because
    <code>@log</code> records a message after the wrapped call returns, the base
    line appears first, the recursive line second, and <code>3</code> is printed
    last.
  </p>
</details>

Try changing only `right` from 1 to 2. One more successor on the right adds one
recursive call and one recursive trace line. The base case still runs once.

## Reading failures

An exception is also part of the implementation's contract. Try a negative
argument to `natural_number`, a zero denominator to `rational`, or an interval
that does not isolate one root. Locate the matching validation branch before
interpreting the error.
