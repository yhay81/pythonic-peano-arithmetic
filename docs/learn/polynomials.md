<span class="lesson-number">第4章 · 多項式</span>

# 式をデータにして、根の個数を調べる

<p class="lesson-lead">
  <code>√2</code> は有理数として作れませんが、
  <code>x²−2=0</code> を満たす数として指定できます。
  この章では式を係数列として保存し、代入とスツルム列（Sturm列）の実装から、
  根が1と2の間に一つだけあることを確かめます。
</p>

<div class="lesson-context" data-reveal>
  <div>
    <strong>前章から使うもの</strong>
    <p>有理数の表現と演算、約分、作成時の不変条件、ログの表示範囲。</p>
  </div>
  <div>
    <strong>この章で学ぶこと</strong>
    <p>変数、係数列、ホーナー法（Horner法）、根、符号変化、スツルム列、高速化のための選択。</p>
  </div>
</div>

<div class="lesson-goals" data-reveal>
  <strong>この章を終えると</strong>
  <ul>
    <li><code>x²−2</code> と係数列 <code>(−2,0,1)</code> を対応付けられる</li>
    <li><code>Polynomial.__init__</code> と <code>evaluate</code> の処理を追える</li>
    <li>根の存在と一意性を、別の根拠で説明できる</li>
  </ul>
</div>

<div class="implementation-bridge" data-reveal aria-label="多項式の数学・表現・実装">
  <div>
    <strong>数学</strong>
    <p>有限個の有理数係数を持つ式へ値を代入し、0になる根を調べます。</p>
  </div>
  <div>
    <strong>データ表現</strong>
    <p><code>Polynomial.coefficients</code> が、定数項から順に係数を保存します。</p>
  </div>
  <div>
    <strong>実装</strong>
    <p>コンストラクタが表現を正規化し、ホーナー法とスツルム列が根を調べます。</p>
  </div>
</div>

<div class="source-reference"
     data-source-reference="peano/polynomial.py"
     data-test-reference="tests/test_polynomial.py">
  <strong>この章で横に置く実装</strong>
  <p>
    完全なクラスと根数え関数:
    <a href="/assets/source/peano/polynomial.py"><code>peano/polynomial.py</code></a>。
    本文では <code>__init__</code>、<code>evaluate</code>、
    <code>sturm_sequence</code>、<code>count_real_roots</code> を抜粋します。
  </p>
  <p>
    正規化・代入・根数の検査:
    <a href="/assets/source/tests/test_polynomial.py"><code>tests/test_polynomial.py</code></a>。
    ファイル索引は<a href="/reference/implementation/">実装リファレンス</a>にあります。
  </p>
</div>

<span class="lesson-layer" data-layer="definition">数学上の定義</span>

## `x²−2` の根として√2を指定する

`x` は、あとから数を代入する場所です。`x²` は `x×x` の短い表記です。
数と `x` のべき乗を足して作る式を**多項式**と呼びます。

<div class="peano-equation" data-reveal>
x²−2 = −2 + 0x + 1x²
</div>

`−2`、`0`、`1` は各項の**係数**です。`x²−2` へ `x=1` を代入すると
`−1`、`x=2` なら `2` です。代入した結果が0になる `x` を**根**と呼びます。
したがって、探している正の `√2` は `x²−2` の根です。

多項式の値は、入力を少し動かしたとき突然飛びません。この**連続性**と
中間値の定理により、1で負、2で正なら、**開区間** `(1,2)` に根が
少なくとも一つあります。ただし、端点の符号だけでは根が一つとは限りません。
開区間 `(1,2)` は、1と2そのものを含まず、その間にある実数全体です。
ここでは中間値の定理を証明せず、連続な関数が負から正へ変わる途中では
0を通る、という保証として使います。

<span class="lesson-layer" data-layer="representation">データの表し方</span>

## 式を、定数項から始まる係数列として保存する

ライブラリは多項式の見た目の文字列を保存しません。係数を
`x⁰, x¹, x², …` の順に並べた、変更できない列として保存します。

| 数学の式 | 保存する係数列 |
| --- | --- |
| `x²−2` | `(−2,0,1)` |
| `1+x` | `(1,1)` |
| `3` | `(3)` |

`polynomial((-2,1),(0,1),(1,1))` の各組は、係数を
`(分子,分母)` で書いたものです。内部では三つの `Rational` を作り、
`Polynomial` へ渡します。

このクラスは、これまでの数のクラスと違って `init=False` です。

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

<div class="meta-note" data-meta="custom-init" data-reveal>
  <strong>dataclassの生成を止め、正規化するコンストラクタを書く</strong>
  <p>
    係数を受け取ったまま保存すると、末尾の0や未約分の係数が残ります。
    そこで <code>init=False</code> で自動生成を止め、
    正規化してから一つのタプルへ保存する <code>__init__</code> を手書きします。
    <code>dataclass</code>は<code>frozen</code>と<code>slots</code>の制約には引き続き使われます。
  </p>
</div>

`Q_ZERO` は前章で構成した有理数0を一度作って名前を付けた定数です。

1. すべての有理数係数を約分する
2. 最高次側に続く0を取り除く
3. 変更できない `tuple` として保存する

`1+0x` と `1` は同じ多項式なので、どちらも係数列 `(1)` へ正規化されます。
整数と有理数では入力した代表元を残しましたが、多項式では表現を一意に寄せます。
これは型ごとの設計上の違いです。

`frozen=True` では通常の `self._coefficients = ...` も拒否されるため、
初期化中だけ基底の `object.__setattr__` を明示的に呼びます。
これは不変オブジェクトを手書きで初期化するためのPythonデータモデル上の処理で、
数学的な操作ではありません。

<span class="lesson-layer" data-layer="implementation">Pythonでの実装</span>

## ホーナー法で係数列から値を計算する

係数が `(a₀,a₁,a₂)` の多項式は `a₀+a₁x+a₂x²` です。
同じ式を次のように括ると、`x` の掛け算を一段ずつ進められます。

<div class="peano-equation" data-reveal>
a₀ + x(a₁ + xa₂)
</div>

これを**ホーナー法**と呼びます。`Polynomial.evaluate` は係数列を逆向きに読み、
有理数の乗法と加法を繰り返します。

```python
@log(log_level=31)
def evaluate(self, value: object) -> tuple[Rational, LogMessage]:
    point = cast2r(value)
    result = Q_ZERO
    for coefficient in reversed(self.coefficients):
        result = (result * point + coefficient).reduction()
    return result, lambda: f"{self!r}: x={point!r} -> {result!r}"
```

- `cast2r` は、自然数・整数・有理数の入力を有理数へ揃える
- `reversed` によって、最高次の係数から読む
- 毎回 `reduction()` して、途中の分数表現が膨らみすぎないようにする

`x²−2` へ1を代入すると、内部状態は次のように変わります。

| 読んだ係数 | 更新式 | `result` |
| ---: | --- | ---: |
| 1 | `0×1+1` | 1 |
| 0 | `1×1+0` | 1 |
| −2 | `1×1−2` | −1 |

この表は実装のループを手で実行したものです。

スツルム列の実装は、根を数えるために別の計算を組み立てます。
次は入力検査と戻り値を含む完全な関数です。

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

`square_free()` は、同じ場所に重なっている根を一つとして数えられる形へ直します。
`x²−2` には重なった根がないため、ここでは元の式のままです。
次の `derivative()` は**導関数**を作ります。係数と指数を掛けて次数を一つ下げるので、
各項 `aₖxᵏ` は `k×aₖxᵏ⁻¹` へ変わり、`x²−2` の導関数は `2x` です。

その後は前二つを多項式として割り、余りの符号を反転して追加します。
`x²−2` なら、実装のループを次のように手で追えます。

| 段階 | 割る計算 | 余り | 列へ追加するもの |
| ---: | --- | ---: | ---: |
| 初期化 | — | — | `x²−2`, `2x` |
| 1 | `(x²−2) ÷ 2x` | `−2` | 符号を反転した `2` |
| 2 | `2x ÷ 2` | `0` | 追加せず終了 |

最初の余りは、`x²−2 = (x/2)(2x)−2` と書けば `−2` だと確認できます。
したがってスツルム列は次の三つです。

<div class="peano-equation" data-reveal>
x²−2,　2x,　2
</div>

<span class="lesson-layer" data-layer="trace">実行して確かめる</span>

## 代入ログと符号変化を、別の証拠として読む

`evaluate` には `@log(log_level=31)` が付いています。ログはループの各周ではなく、
すべての係数を処理して戻り値ができたあとに一行だけ出ます。

<div class="learning-prompt" data-kind="prediction" data-reveal>
  <strong>実行前に、ホーナー法を一度手で追う</strong>
  <p>
    上に抜粋した <code>evaluate</code> のループを参照し、
    <code>x=2</code> の三つの
    <code>result</code> を書いてから実行してください。
  </p>
</div>

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

`<P(-2 + x^2)>` は保存された多項式、`<Q(1/1)>` は代入した有理数、
最後の `<Q(-1/1)>` はホーナー法で得た有理数です。代入ログの一行だけでは
ループ途中は見えないため、実装を根拠に上の表を作ることに意味があります。

次にスツルム列の符号を端点で調べます。0を除いた符号が何回切り替わるかを
`sign_variations` が数えます。

| 点 | `x²−2, 2x, 2` の符号 | 変化回数 |
| ---: | --- | ---: |
| 1 | `−,+,+` | 1 |
| 2 | `+,+,+` | 0 |

スツルムの定理により、左端の変化回数から右端の回数を引いた値が、
開区間の相異なる実根の個数です。

実装も、その差をそのまま返します。次は二つの関数の完全な実装です。

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

表示幅に合わせて関数のシグネチャと最後の式を改行していますが、処理は実ファイルと同じです。

<div class="learning-prompt" data-kind="prediction" data-reveal>
  <strong>存在と個数を分けて予想</strong>
  <p>
    上の <code>count_real_roots</code> のreturnを参照してください。
    中間値の定理が保証することと、符号変化の差
    <code>1−0</code> が保証することを、それぞれ一文で書いてください。
  </p>
</div>

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

<span class="lesson-layer" data-layer="test">テストで確かめる</span>

## テストは表現・計算・根の個数を分離する

係数列の正規化は、末尾の0がある表現とない表現が等しいことで検査します。

```python
self.assertEqual(
    Polynomial(rational(1, 1), rational(0, 1)),
    Polynomial(rational(1, 1)),
)
```

代入は、`x²−2` へ `3/2` を入れた結果が `1/4` になることを確かめます。

```python
self.assertEqual(
    self.sqrt_two_polynomial.evaluate(rational(3, 2)),
    rational(1, 4),
)
```

スツルム列については、`(−2,2)` に二つの実根 `−√2` と `√2` があること、
列の長さが3になることを検査します。

```python
self.assertEqual(
    count_real_roots(self.sqrt_two_polynomial, rational(-2, 1), rational(2, 1)),
    2,
)
self.assertEqual(len(sturm_sequence(self.sqrt_two_polynomial)), 3)
```

一つの大きなテストではなく、表現の不変条件、代入、根の個数という責務ごとに
失敗箇所を切り分けられる形になっています。

<span class="lesson-layer" data-layer="boundary">高速化のための選択</span>

## 構成を見せる経路と、高速に符号だけ調べる経路

`evaluate` は、これまで構成した `Rational` の演算を実際に使うため、
数体系の積み上げを観察できます。一方、二分法やスツルム列では、多項式の
**符号だけ**を何度も調べます。

そこで `sign_at` は、同じ整数比をPythonの任意精度整数を使う `Fraction` へ
一時的に写し、ホーナー法で厳密に符号を判定します。浮動小数点の近似ではありませんが、
ペアノ表現だけを通す経路でもありません。

```python
def sign_at(self, value: object) -> int:
    point = _as_fraction(cast2r(value))
    result = Fraction(0)
    for coefficient in reversed(self.coefficients):
        result = result * point + _as_fraction(coefficient)
    return (result > 0) - (result < 0)
```

ここでは、構成を見せる処理と、繰り返し計算を現実的な時間で行う処理を
意図的に分けています。

| メソッド | 優先するもの |
| --- | --- |
| `evaluate` | 構成した数体系の演算が見えること |
| `sign_at` | 同じ有理数の意味を保ったまま、反復判定を実用的に行うこと |

中間値の定理は根が少なくとも一つあること、スツルムの定理は相異なる根の個数を
保証します。プログラムの出力だけから定理そのものが証明されるわけではありません。

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

## 次へ

多項式と区間 `(1,2)` を結び付け、そこに根が一つだけあると確認できました。
次章では、この条件をオブジェクトの不変条件として保存し、区間を半分ずつ狭めます。

[代数的実根へ進む →](algebraic-roots.md)
