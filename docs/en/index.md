---
title: Build numbers, one rule at a time
hide:
  - toc
---

<section class="course-hero">
  <div class="course-hero__content">
    <span class="course-kicker">Arithmetic construction through Python's data model</span>
    <h1>Build numbers, one rule at a time.</h1>
    <p>
      Start with zero and successor. Follow each mathematical definition into
      a class, method, branch, trace, and test.
    </p>
    <div class="course-actions">
      <a class="course-action course-action--primary" href="learn/python-basics/">Start with the Python mechanisms</a>
      <a class="course-action" href="#route">See the route</a>
    </div>
  </div>
  <figure class="course-hero__diagram">
    <figcaption>The construction</figcaption>
    <ol>
      <li><strong>Zero and successor</strong><span>construct natural numbers and addition</span></li>
      <li><strong>Pairs of naturals</strong><span>identify pairs with the same difference</span></li>
      <li><strong>Pairs of integers</strong><span>identify pairs with the same ratio</span></li>
      <li><strong>Expressions and intervals</strong><span>identify a real root that is not rational</span></li>
    </ol>
  </figure>
</section>

## What this course assumes

You should be comfortable with ordinary Python syntax: functions, classes,
conditionals, loops, collections, exceptions, and type annotations. You do not
need prior knowledge of Peano arithmetic, constructed number systems,
polynomials, or this repository.

The course teaches the Python mechanisms that matter to this implementation:

- operator dispatch such as `a + b` calling `a.__add__(b)`;
- decorators that change a public call without changing its mathematical core;
- generated and suppressed dataclass methods;
- `__post_init__`, properties, `total_ordering`, and frozen values;
- coercion, `NotImplemented`, equality, and hashing across a numeric tower.

Nothing is installed on your computer. Experiments run in the browser.

## How understanding accumulates

<div class="learning-cycle" data-reveal aria-label="Learning cycle used in each chapter">
  <span><strong>1 · Definition</strong>state the object and its rules</span>
  <span><strong>2 · Representation</strong>see which fields store it</span>
  <span><strong>3 · Implementation</strong>map each rule to a method and branch</span>
  <span><strong>4 · Trace</strong>predict the execution before running it</span>
  <span><strong>5 · Test</strong>read what concrete behavior is checked</span>
  <span><strong>6 · Boundary</strong>separate proof, design choice, and optimization</span>
</div>

A trace is not a self-explanatory derivation. First read the relevant
implementation; then use the trace to check which rule and branch actually ran.
Every chapter includes the source excerpt needed for its questions and links to
the complete source and tests.

## Learning route { #route }

<nav class="learning-path" aria-label="Learning route" data-reveal>
  <a href="learn/python-basics/" data-step="00"><span><strong>Python mechanisms</strong>operators, decorators, and dataclasses</span></a>
  <a href="learn/natural-numbers/" data-step="01"><span><strong>Natural numbers</strong>zero, successor, equality, and recursive addition</span></a>
  <a href="learn/integers/" data-step="02"><span><strong>Integers</strong>construct signed values from pairs of naturals</span></a>
  <a href="learn/rationals/" data-step="03"><span><strong>Rational numbers</strong>construct fractions from pairs of integers</span></a>
  <a href="learn/polynomials/" data-step="04"><span><strong>Polynomials</strong>turn expressions into data and count roots</span></a>
  <a href="learn/algebraic-roots/" data-step="05"><span><strong>Algebraic real roots</strong>identify one root by nested rational intervals</span></a>
</nav>

The finish line is not merely obtaining the right answer. You should be able to
say which definition was executed, how the value was represented, which branch
produced a trace line, and what the test does—and does not—establish.

[Begin with Python's data model and metaprogramming →](learn/python-basics.md)
