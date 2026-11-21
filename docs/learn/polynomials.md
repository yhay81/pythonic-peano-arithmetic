<span class="lesson-number">第4章 · 多項式</span>

# 式の値を計算し、答えがいくつあるかを調べる

前章で、2乗して2になる正の数 √2 は分数で書き切れないと分かりました。けれども、その数を見分ける条件「x²−2＝0」は短く書けます。そこで今度は、数の代わりに式をコンピューターに持たせます。

<div class="lesson-goals"><strong>この章の目標</strong><p>x²−2 に値を代入する手順を作り、1と2の間に答えがちょうど一つあることを確かめます。</p></div>

<span class="lesson-layer" data-layer="definition">式と、その根</span>

## 「一つはある」と「一つだけある」

式に入れると値が0になる数を、その式の**根**と呼びます。x²−2 に1を入れると−1、2を入れると2です。この式のグラフは途中で途切れないので、負の高さから正の高さへ行く途中、どこかで高さ0を通ります。これは**中間値の定理**を使った考え方です。

今回は正の数が大きくなるほど2乗も大きくなるので、1から2の間で0を通るのは一度だけです。でも、一般の式ではグラフが何度も上下するかもしれません。そこで「少なくとも一つ」と「ちょうど一つ」を別々に調べます。

<span class="lesson-layer" data-layer="representation">式の保存方法</span>

## x の項がないのに、なぜ0を入れる？

<div class="implementation-bridge"><p>x²−2 を次数の低い順に書くと −2＋0x＋1x² です。各項に掛かっている数を<strong>係数</strong>と呼びます。係数を (−2, 0, 1) と並べれば、位置が定数、x、x² のどれかを表します。</p></div>

```python
@total_ordering
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

<p data-meta="custom-init"><code>init=False</code> なのは、係数を保存する前に並びを整えたいからです。<code>normalized[-1]</code> は最後の係数。そこが0なら <code>pop()</code> で削ります。たとえば (−2, 0, 1, 0) の最後の0は 0x³ なので削れます。一方、途中の0を削ると (−2, 1) となり、式は x−2 に変わります。</p>

`len(normalized) > 1` は、全部0でも最後の一つは残す条件です。`tuple(normalized)` が、整えた係数を順番の決まった組にします。このように整数や分数の係数と x の0乗、1乗、2乗、…を組み合わせて足した式が**多項式**です。ここでは有理数を係数に使います。

<p class="source-reference" data-source-reference="peano/polynomial.py" data-test-reference="tests/test_polynomial.py">元のファイルを読む　<a href="/assets/source/peano/polynomial.py">peano/polynomial.py</a> ／ <a href="/assets/source/tests/test_polynomial.py">tests/test_polynomial.py</a></p>

<span class="lesson-layer" data-layer="implementation">係数から計算する</span>

## 2乗を先に計算せず、後ろから一項ずつ読む

```python
@log(log_level=31)
def evaluate(self, value: object) -> tuple[Rational, LogMessage]:
    point = cast2r(value)
    result = Q_ZERO
    for coefficient in reversed(self.coefficients):
        result = (result * point + coefficient).reduction()
    return result, lambda: f"{self!r}: x={point!r} -> {result!r}"
```

`point` は代入する数、`result` は途中の値です。`reversed` で係数を後ろから読み、毎回「途中の値×代入する数＋次の係数」を計算します。x＝3/2 を代入して一周ずつ追いましょう。

| 読む係数 | 計算 | 新しい result |
| --- | --- | --- |
| 1 | 0×(3/2)＋1 | 1 |
| 0 | 1×(3/2)＋0 | 3/2 |
| −2 | (3/2)×(3/2)−2 | 1/4 |

これは x²−2 を (1×x＋0)×x−2 とかっこでくくっただけです。高い次数にも同じループが使えます。この計算法を**ホーナー法**と呼びます。

<span class="lesson-layer" data-layer="trace">手計算と比べる</span>

<div class="learning-prompt"><strong>実行する前に</strong><p>実験では同じ式に1と2を入れます。手で符号を予想してから実行し、片方の入力を 3/2 に変えて表の最後の値も確かめてください。</p></div>

<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>実験5 · 多項式への代入を確かめる</span>
    <span class="peano-runner__status" data-role="status">未実行</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="実験5: ホーナー法と多項式の代入ログを確かめるPythonコード" spellcheck="false">from peano import config_log, polynomial, rational

config_log(log_level=31, max_lines=200, locale="ja")

p = polynomial((-2, 1), (0, 1), (1, 1))
value_at_1 = p.evaluate(rational(1, 1))
value_at_2 = p.evaluate(rational(2, 1))

print("x = 1:", value_at_1)
print("x = 2:", value_at_2)</textarea>
  <div class="peano-runner__controls">
    <button class="peano-runner__button peano-runner__button--run" data-action="run">▶ 実行</button>
    <button class="peano-runner__button" data-action="reset">環境をリセット</button>
    <span class="peano-runner__shortcut">⌘ / Ctrl + Enter</span>
  </div>
  <div class="peano-runner__output-wrap">
    <span class="peano-runner__output-label">出力</span>
    <pre class="peano-runner__output" data-role="output" aria-live="polite">二つの代入ログと、printの二つの結果を区別します。</pre>
  </div>
</div>

## 根の個数を数えるための、もう一つの表

ここからは少し先の数学です。**スツルムの定理**という道具を使います。根を端に含まない区間なら、決まった作り方で並べた式について、左端と右端で「符号が隣と何回入れ替わるか」を調べると、その差が区間の中の異なる実数の根の個数になります。まずこの定理の使い方を、実際の数で確かめます。

x²−2 の場合、並べる式は **x²−2、2x、2** です。端の数を三つの式すべてに入れ、左から符号を読みます。

| 入れる数 | 三つの値 | 符号の並び | 入れ替わる回数 |
| --- | --- | --- | ---: |
| 1 | −1, 2, 2 | −, ＋, ＋ | 1 |
| 2 | 2, 4, 2 | ＋, ＋, ＋ | 0 |

左の回数から右の回数を引くと1−0＝1。これで1と2の間の根は**ちょうど一つ**と分かります。根が一つだと知ってから区間を半分にするのが、次章の出発点です。

## その三つの式はどこから来たか

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

`square_free()` は、同じ根が重なる因子を一つずつに整理します。今回の x²−2 はそのままです。`derivative()` は、式からその変化のしかたを表す別の式（導関数）を作ります。たとえば x が h だけ増えると、2乗の増え方は (x＋h)²−x²＝2xh＋h²。これを h で割ると 2x＋h で、h を0に近づけると 2x に近づきます。これが x² の導関数が 2x になる理由です。定数 −2 は x が動いても変わらないので導関数は0です。初めの二つの式がこれで決まりました。

次の `%` は式の割り算の余りです。x²−2＝(x/2)×(2x)−2 なので、最初の式を次の式で割った余りは−2。`append(-remainder)` で符号を反転して2を追加します。次に2xを2で割ると余りが0なので終了です。この作り方で得られる並びを**スツルム列**と呼びます。なぜこれであらゆる多項式の根を数えられるかという証明は、この章では定理として使っています。

```python
def sign_variations(
    sequence: tuple[Polynomial, ...],
    point: Rational,
) -> int:
    signs: list[bool] = []
    for value in sequence:
        sign = value.sign_at(point)
        if sign == 0:
            continue
        signs.append(sign < 0)
    return sum(left != right for left, right in zip(signs, signs[1:]))


def count_real_roots(
    value: Polynomial,
    lower: Rational,
    upper: Rational,
) -> int:
    if not isinstance(value, Polynomial):
        raise TypeError("value must be a Polynomial")
    lower = cast2r(lower)
    upper = cast2r(upper)
    if lower >= upper:
        raise ValueError("lower must be less than upper")
    if value.sign_at(lower) == 0 or value.sign_at(upper) == 0:
        raise ValueError("interval endpoints must not be roots")
    sequence = sturm_sequence(value)
    return sign_variations(sequence, lower) - sign_variations(sequence, upper)
```

最初の関数では、0を飛ばし、各値が「負かどうか」を並べます。`zip(signs, signs[1:])` は一つずらして隣同士を組にする書き方です。左と右が違う組だけを数えれば、表の最後の列になります。二つ目の関数の最後の一行が、左端での回数から右端での回数を引いています。

<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>実験6 · スツルム列で根の個数を確かめる</span>
    <span class="peano-runner__status" data-role="status">未実行</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="実験6: スツルム列の符号変化から実根数を確かめるPythonコード" spellcheck="false">from peano import (
    count_real_roots,
    polynomial,
    rational,
    sign_variations,
    sturm_sequence,
)

p = polynomial((-2, 1), (0, 1), (1, 1))
one = rational(1, 1)
two = rational(2, 1)
sequence = sturm_sequence(p)

print("スツルム列:", [str(item) for item in sequence])
print("1 での符号変化:", sign_variations(sequence, one))
print("2 での符号変化:", sign_variations(sequence, two))
print("根の個数:", count_real_roots(p, one, two))</textarea>
  <div class="peano-runner__controls">
    <button class="peano-runner__button peano-runner__button--run" data-action="run">▶ 実行</button>
    <button class="peano-runner__button" data-action="reset">環境をリセット</button>
    <span class="peano-runner__shortcut">⌘ / Ctrl + Enter</span>
  </div>
  <div class="peano-runner__output-wrap">
    <span class="peano-runner__output-label">出力</span>
    <pre class="peano-runner__output" data-role="output" aria-live="polite">列、両端の符号変化、差として得る根の個数を順に読みます。</pre>
  </div>
</div>

<details class="self-check"><summary>左端を−2にしたら？</summary><p>−2を入れると三つの符号は ＋, −, ＋ で、入れ替わりは2回。右端の2では0回。差は2です。両端で元の式の値が正でも、途中に根が二つある例です。</p></details>

<span class="lesson-layer" data-layer="test">別の入力で確かめる</span>

## テストが見分ける二つの間違い

```python
self.assertEqual(
    self.sqrt_two_polynomial.evaluate(rational(3, 2)),
    rational(1, 4),
)
```

このテストは先ほどの手計算の 1/4 と、代入の結果を比べます。たとえば係数を逆向きに保存したら、違う式の値になり、見つけられます。

```python
self.assertEqual(
    count_real_roots(self.sqrt_two_polynomial, rational(-2, 1), rational(2, 1)),
    2,
)
self.assertEqual(len(sturm_sequence(self.sqrt_two_polynomial)), 3)
```

こちらは −2 と 2 の間の根の個数を調べます。式を正しく計算できても、「両端の符号が同じなら根は0個」と決めてしまう実装はこの検査で失敗します。

<span class="lesson-layer" data-layer="boundary">正確さと計算量</span>

## 値の全部が要るときと、符号だけで足りるとき

```python
def sign_at(self, value: object) -> int:
    point = _as_fraction(cast2r(value))
    result = Fraction(0)
    for coefficient in reversed(self.coefficients):
        result = result * point + _as_fraction(coefficient)
    return (result > 0) - (result < 0)
```

`sign_at` も同じホーナー法です。ただし分数をPython標準の `Fraction` に移して計算します。分母が大きくなると、分子や分母を「次の数」の鎖で毎回組み立てるのに時間がかかるからです。分子と分母は整数のまま扱うので、小数への丸めは入りません。最後の行は正なら1、負なら−1、0なら0を返します。次章の二分法で必要なのは、この三通りの答えです。

<form class="knowledge-check" data-reveal>
  <fieldset>
    <legend>確認問題 · <code>x²−2</code> の1と2での符号が異なるだけで、直接言えることはどれですか。</legend>
    <label>
      <input type="radio" name="polynomial-check" data-feedback="根が複数ある可能性は、端点の符号だけでは残ります。">
      根がちょうど一つある
    </label>
    <label>
      <input type="radio" name="polynomial-check" data-correct data-feedback="連続性と中間値の定理から、途中に少なくとも一つの根があります。">
      根が少なくとも一つある
    </label>
    <label>
      <input type="radio" name="polynomial-check" data-feedback="負から正へ連続に変わる途中で0を通ります。">
      根は存在しない
    </label>
    <button type="submit">答え合わせ</button>
    <p class="knowledge-check__feedback" data-role="feedback" aria-live="polite"></p>
  </fieldset>
</form>

[第5章へ。根を一つ含む区間を狭める](algebraic-roots.md)
