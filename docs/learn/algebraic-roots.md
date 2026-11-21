<span class="lesson-number">第5章 · 代数的実根</span>

# √2の値を書き切らずに、√2を正確に指定する

「1.41」というメモだけでは、続きを丸めたのか、ぴったり1.41なのかは分かりません。一方、「2乗して2になる数で、1と2の間にあるもの」と書けば、指している数は一つに決まります。この違いを、そのままプログラムに使います。

<div class="lesson-goals"><strong>この章の目標</strong><p>√2を指すデータを作り、その数を取り逃さずに範囲を半分ずつ狭めます。最後に、計算で得た範囲と、その中の数を区別して説明します。</p></div>

<span class="lesson-layer" data-layer="definition">どの根かを決める</span>

## 式と区間は、なぜ両方いる？

方程式 x²−2＝0 には負の根と正の根があります。前章では1から2までの間には根がちょうど一つあると確かめました。そこで、式と区間 [1, 2] をセットで保存します。角かっこは両端を含むという意味です。特定したい根だけを含む範囲を**分離区間**と呼びます。

√2のように、係数がすべて有理数で、少なくとも一つは0でない多項式の根になる実数を**代数的実数**といいます。この章で作るのは、その中でも両端の符号が異なる区間で一つに絞れる根です。たとえば x² は0で横軸に触れて引き返すので、[−1, 1] の両端で符号が変わらず、この作り方では受け付けません。

<span class="lesson-layer" data-layer="representation">データの形を決める</span>

<div class="implementation-bridge"><p><code>AlgebraicRoot</code> は式と区間を持ちます。区間は、下端 <code>lower</code> と上端 <code>upper</code> の二つの有理数を持ちます。</p></div>

```python
@dataclass(frozen=True, slots=True, eq=False)
class AlgebraicRoot:
    polynomial: Polynomial
    interval: RationalInterval
```

```python
@property
def width(self) -> Rational:
    return _from_fraction(_as_fraction(self.upper) - _as_fraction(self.lower))
```

<p data-meta="property">式を持つクラスと区間を持つクラスを読み分けましょう。上の <code>root.interval</code> が区間で、その両端は <code>root.interval.lower</code> と <code>root.interval.upper</code> です。二つ目の抜粋は区間のクラスにある <code>width</code> です。<code>@property</code> が付いているので <code>interval.width</code> と読むと、その場で上端から下端を引きます。<code>_as_fraction</code> は前章の <code>Fraction</code> に直して計算しやすくし、<code>_from_fraction</code> が結果を教材の分数に戻します。√2そのものを小数に直す必要はありません。</p>

<p class="source-reference" data-source-reference="peano/algebraic_root.py" data-test-reference="tests/test_algebraic_root.py">元のファイルを読む　<a href="/assets/source/peano/algebraic_root.py">peano/algebraic_root.py</a> ／ <a href="/assets/source/tests/test_algebraic_root.py">tests/test_algebraic_root.py</a></p>

## 作るときに、どこまで確かめる？

```python
def algebraic_root(
    polynomial_value: Polynomial,
    lower: tuple[int, int],
    upper: tuple[int, int],
) -> AlgebraicRoot:
    return AlgebraicRoot(
        polynomial_value,
        RationalInterval(rational(*lower), rational(*upper)),
    )
```

`algebraic_root(p, (1, 1), (2, 1))` の二つの組は、1/1 と 2/1 を表します。`rational(*lower)` の星印は、組の中身を二つの引数に分ける記号です。この関数が最後に `AlgebraicRoot` を作ると、次の検査が走ります。

```python
def __post_init__(self) -> None:
    if not isinstance(self.polynomial, Polynomial):
        raise TypeError("polynomial must be a Polynomial")
    if not isinstance(self.interval, RationalInterval):
        raise TypeError("interval must be a RationalInterval")
    if self.polynomial.degree <= 0:
        raise ValueError("a root-defining polynomial must have positive degree")
    if self.interval.is_point:
        raise ValueError("the initial interval must have positive width")

    lower_sign = self.polynomial.sign_at(self.interval.lower)
    upper_sign = self.polynomial.sign_at(self.interval.upper)
    if lower_sign == 0 or upper_sign == 0:
        raise ValueError("initial interval endpoints cannot be roots")
    if lower_sign == upper_sign:
        raise ValueError("the polynomial must change sign across the endpoints")

    number_of_roots = count_real_roots(
        self.polynomial,
        self.interval.lower,
        self.interval.upper,
    )
    if number_of_roots != 1:
        raise ValueError(
            "the initial interval must contain exactly one distinct real root "
            f"(found {number_of_roots})"
        )
```

上から順に、まず式と区間の種類を確認します。`degree <= 0` は定数の式、`is_point` は幅が0の区間を除くためです。次に、端そのものが根である場合を除き、両端の符号が異なることを確認します。これで途中に根があると分かります。最後に `count_real_roots` で個数を確かめます。符号が変わっても、途中で3回横軸を横切った可能性が残るからです。

<span class="lesson-layer" data-layer="implementation">半分を選ぶ</span>

## 真ん中で一度計算すると、なぜ半分を消せる？

中点は両端の平均です。コードの `midpoint = interval.midpoint` で、最初は (1＋2)/2＝3/2 が得られます。次の `sign_at(midpoint)` が尋ねるのは、中点が正かではなく、**中点を式に入れた結果**が正かどうかです。たとえば5/4は正でも、(5/4)²−2 は負になります。

x²−2 の値は、左端1では−1、右端2では2。真ん中の 3/2 では 9/4−2＝1/4 で正です。左端と真ん中の間で負から正に変わったので、ここに根が一つはあります。元の区間に根が一つしかないことはもう確かめたので、右半分を捨ててもその根を失いません。これが**二分法**の一歩です。

| 試す前の区間 | 中点 | 中点での x²−2 | 残す区間 |
| --- | --- | --- | --- |
| [1, 2] | 3/2 | 1/4（正） | [1, 3/2] |
| [1, 3/2] | 5/4 | −7/16（負） | [5/4, 3/2] |
| [5/4, 3/2] | 11/8 | −7/64（負） | [11/8, 3/2] |

```python
@log(log_level=41)
def _bisect(
    polynomial_value: Polynomial,
    interval: RationalInterval,
) -> tuple[RationalInterval, LogMessage]:
    midpoint = interval.midpoint
    midpoint_sign = polynomial_value.sign_at(midpoint)

    if midpoint_sign == 0:
        result = RationalInterval(midpoint, midpoint)
        return (
            result,
            lambda: translate(
                "midpoint_root",
                polynomial=repr(polynomial_value),
                midpoint=repr(midpoint),
            ),
        )

    lower_sign = polynomial_value.sign_at(interval.lower)
    if lower_sign != midpoint_sign:
        result = RationalInterval(interval.lower, midpoint)
    else:
        result = RationalInterval(midpoint, interval.upper)
    return (
        result,
        lambda: f"{polynomial_value!r}: {interval} -> {result}",
    )
```

最初の `if` には、表に出てこない場合が書かれています。中点そのものが根なら、両端をその中点にそろえて終われます。そうでなければ `lower_sign != midpoint_sign` で左端と中点の符号を比べます。違えば左半分、同じなら右半分です。元から両端の符号が違うので、後者では中点と右端の符号が違うことも分かります。

<span class="lesson-layer" data-layer="trace">区間の履歴を読む</span>

```python
def trace(
    self,
    steps: int | NaturalNumber,
) -> tuple[RationalInterval, ...]:
    count = _step_count(steps)
    intervals = [self.interval]
    for _ in range(count):
        if intervals[-1].is_point:
            break
        intervals.append(_bisect(self.polynomial, intervals[-1]))
    return tuple(intervals)
```

`intervals = [self.interval]` で最初の区間も履歴に入れます。`intervals[-1]` は一番新しい区間、`append` は次の区間を末尾に加える操作です。一点に決まったら `break` でそこで止まります。`approximate` は最後の区間だけ、`trace` は途中も含むすべての区間を返します。

<div class="learning-prompt"><strong>実行する前に</strong><p>表の最後の区間で、もう一度二分します。中点 23/16 を2乗して2と比べると、左右のどちらを残すでしょう。実行結果の最後の区間と比べてください。</p></div>

<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>実験7 · 二分法で残る区間を確かめる</span>
    <span class="peano-runner__status" data-role="status">未実行</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="実験07: 二分法の分岐と区間ログを検証するPythonコード" spellcheck="false">from peano import algebraic_root, config_log, polynomial

config_log(log_level=41, max_lines=200, locale="ja")

p = polynomial((-2, 1), (0, 1), (1, 1))
sqrt_two = algebraic_root(p, (1, 1), (2, 1))
intervals = sqrt_two.trace(4)

for interval in intervals:
    print(interval)</textarea>
  <div class="peano-runner__controls">
    <button class="peano-runner__button peano-runner__button--run" data-action="run">▶ 実行</button>
    <button class="peano-runner__button" data-action="reset">環境をリセット</button>
    <span class="peano-runner__shortcut">⌘ / Ctrl + Enter</span>
  </div>
  <div class="peano-runner__output-wrap">
    <span class="peano-runner__output-label">出力</span>
    <pre class="peano-runner__output" data-role="output" aria-live="polite">4本の区間二分ログと、初期区間を含む5区間を区別します。</pre>
  </div>
</div>

<details class="self-check"><summary>4回目の区間を確かめる</summary><p>23²＝529、2×16²＝512。中点で式の値が正になるので、負だった左端11/8と中点23/16の間を残します。幅は 23/16−22/16＝1/16。初めの区間も含めて、最後の for 文は五つの区間を表示します。</p></details>

<span class="lesson-layer" data-layer="test">何を検査すればよいか</span>

## 幅が正しくても、答えを外すことがある

```python
approximation = root.approximate(3)

self.assertEqual(approximation.width, rational(1, 8))
self.assertLess(
    self.sqrt_two_polynomial.sign_at(approximation.lower),
    0,
)
self.assertGreater(
    self.sqrt_two_polynomial.sign_at(approximation.upper),
    0,
)
self.assertEqual(len(root.trace(3)), 4)
```

毎回間違った側を残しても、幅だけは半分になります。そこでテストでは、3回後の幅が 1/8 かに加えて、左端で式の値が負か、右端で正かも確かめます。`assertLess(..., 0)` は0より小さいことの検査です。最初に根が一つだと確かめた範囲の中でこの符号が保たれれば、同じ根をまだ挟んでいます。

中点が根になる場合も試せます。式を x、区間を [−1, 1] とすれば、中点0が根です。1回の二分で [0, 0] が返り、その先は区間を増やしません。

<span class="lesson-layer" data-layer="boundary">ここまでで何が分かったか</span>

## 指定は正確でも、近似には幅がある

√2の例では、k 回二分すると幅は 1/2ᵏ です。幅を 1/100 より小さくしたければ、2⁶＝64、2⁷＝128 なので7回で足ります。答えを小数で言う前に、「どこからどこまで」と精度を示せます。何回計算しても両端は有理数なので、両端のどちらも √2 にはなりません。

区間の幅が小さいことと、根を含むことは別々に確かめてきました。したがって、たとえば7回後の区間の中点を答えに選べば、√2 とのずれは幅の半分、1/256 以下です。

最初に保存した**式と分離区間**は、初めから正確に一つの根を指しています。一方、二分して得た**区間**は、その根がどこにあるかを知るための有限回の計算結果です。区間を際限なく狭めた先にも実数が存在するという議論には、実数に隙間がないという性質（完備性）を使います。プログラムが無限回の処理を終えるわけではありません。

<form class="knowledge-check" data-reveal>
  <fieldset>
    <legend>確認問題 · √2 の実験で <code>trace(4)</code> を実行して直接得られるものは何ですか。</legend>
    <label>
      <input type="radio" name="root-check" data-feedback="端点は最後まで有理数で、√2そのものにはなりません。">
      √2と厳密に等しい有理数
    </label>
    <label>
      <input type="radio" name="root-check" data-correct data-feedback="初期区間と4回の二分後を含む、根を保った5個の有理区間です。">
      根を含む、初期区間を含めた5個の有理区間
    </label>
    <label>
      <input type="radio" name="root-check" data-feedback="多項式の符号と作成時の根数検査に基づいて区間を選んでいます。">
      根との関係を検査していない5個の近似値
    </label>
    <button type="submit">答え合わせ</button>
    <p class="knowledge-check__feedback" data-role="feedback" aria-live="polite"></p>
  </fieldset>
</form>

## 仕上げの問題　同じコードで √3 を探す

上の実験で、定数の係数を `(-2, 1)` から `(-3, 1)` に変えてください。式は x²−3 になります。最初の区間は [1, 2] のままでよいでしょうか。二分を2回したあとの区間を紙に書いてから、`trace(2)` を実行してみましょう。

<details class="self-check">
  <summary>区間を選んだ理由と、計算結果を確かめる</summary>
  <p>1²−3 は負、2²−3 は正です。正の範囲では2乗は大きくなる一方なので、この間に根は一つだけです。中点 3/2 では 9/4−3＝−3/4。左端を 3/2 に替えます。次の中点 7/4 では 49/16−3＝1/16。今度は右端を替え、[3/2, 7/4] が残ります。変えたのは式の係数と計算回数だけで、区間を選ぶコードはそのまま使えました。</p>
</details>

[実験ページで、入力を一つ変えて予想を確かめる](../playground.md)
