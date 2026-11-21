<span class="lesson-number">第3章 · 有理数</span>

# 割り算を使わずに、二つの分数を比べる

整数を作るときは二つの数を「差」と読みました。今度は整数の組 (p, q) を「p を q で割った量」と読みます。すると (1, 2) と (2, 4) は同じ量です。小数にも直さず、約分もせずに、それをプログラムに判定させられるでしょうか。

<div class="lesson-goals"><strong>この章の目標</strong><p>分数の比較と足し算を整数の掛け算で書き、約分が必要になる場面を見分けます。</p></div>

<span class="lesson-layer" data-layer="definition">分母をそろえる</span>

## 斜めに掛ける理由

1/2 と 2/4 の分母を、両方の分母の積である8にそろえます。左は (1×4)/8、右は (2×2)/8。分母が同じなので、比べるのは **1×4 と 2×2** です。どちらも4なので、この二つは同じ量です。

同じように p/q と r/s の分母を q×s にすれば、分子は p×s と q×r になります。だから二つの積が等しいかどうかで判定できます。この積を**交差積**といいます。分母が0だとこの話は始められないので、数を作る時点で除きます。整数どうしの分数で表せる数のことを**有理数**といいます。

<span class="lesson-layer" data-layer="representation">分子と分母を保存する</span>

```python
def rational(numerator: int, denominator: int) -> Rational:
    return Rational(integer(numerator), integer(denominator))
```

<div class="implementation-bridge"><p>小文字の <code>rational(2, 4)</code> は、Pythonの整数2と4を前章の整数に変え、大文字の <code>Rational</code> に渡します。できた数では <code>p</code> が分子、<code>q</code> が分母です。</p></div>

```python
@total_ordering
@dataclass(frozen=True, slots=True, eq=False, repr=False)
class Rational:
    p: Integer
    q: Integer

    def __post_init__(self) -> None:
        if not isinstance(self.p, Integer) or not isinstance(self.q, Integer):
            raise TypeError("Rational.p and Rational.q must be Integer values")
        if self.q == Z_ZERO:
            raise ZeroDivisionError("the denominator cannot be zero")
```

<p data-meta="post-init">最後の <code>if self.q == Z_ZERO</code> は、受け取った分母と整数の0を前章の方法で比べます。分母が0なら <code>raise</code> で作成を止めます。作成に成功した数はすべて「分母が0でない」という条件を守ります。このように常に守る条件を<strong>不変条件</strong>といいます。</p>

<p class="source-reference" data-source-reference="peano/rational.py" data-test-reference="tests/test_rational.py">元のファイルを読む　<a href="/assets/source/peano/rational.py">peano/rational.py</a> ／ <a href="/assets/source/tests/test_rational.py">tests/test_rational.py</a></p>

<span class="lesson-layer" data-layer="implementation">比較と足し算を書く</span>

## 同じ通分から二つのメソッドを作る

```python
@log(log_level=21)
def __eq__(self, other: object) -> tuple[bool, LogMessage]:
    converted = _coerce_rational(other)
    if converted is None:
        return (
            cast(bool, NotImplemented),
            lambda: f"{self!r} == {other!r} = NotImplemented",
        )
    result = self.p * converted.q == self.q * converted.p
    return (
        result,
        lambda: (
            f"{self!r} == {converted!r} ⇔ "
            f"{self.p!r} * {converted.q!r} == "
            f"{self.q!r} * {converted.p!r}"
        ),
    )
```

`self.p * converted.q` に 1×4、`self.q * converted.p` に 2×2 を当てはめれば、紙で書いた交差積と同じです。右側の値を比較できる型に直すこと、扱えない相手に `NotImplemented` を返すこと、説明文を `lambda` に入れることは整数の章と共通です。

```python
@log(log_level=24)
def __add__(self, other: object) -> tuple[Rational, LogMessage]:
    converted = _coerce_rational(other)
    if converted is None:
        return (
            cast(Rational, NotImplemented),
            lambda: f"{self!r} + {other!r} = NotImplemented",
        )
    result = Rational(
        self.p * converted.q + self.q * converted.p,
        self.q * converted.q,
    )
    return (
        result,
        lambda: (
            f"{self!r} + {converted!r} = "
            f"({self.p!r} * {converted.q!r} + "
            f"{self.q!r} * {converted.p!r}) / "
            f"({self.q!r} * {converted.q!r})"
        ),
    )
```

今度は 1/2＋1/3 で `result = Rational(...)` の二つの引数を読みます。最初の引数は **1×3＋2×1＝5**。二つ目は **2×3＝6**。つまり、同じ大きさに切りそろえた3切れと2切れを足す計算です。比較では交差積を比べ、足し算ではその二つを足します。

<span class="lesson-layer" data-layer="trace">自分の予想と比べる</span>

<div class="learning-prompt"><strong>実行する前に</strong><p>1/2 と 2/4 を比べたあと、左だけを 2/3 に変えてみましょう。右の分数をそのままにすると、比べる二つの積はどう変わりますか。</p></div>

<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>実験3 · 有理数の等値判定を確かめる</span>
    <span class="peano-runner__status" data-role="status">未実行</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="実験03: 有理数の交差積と等号ログを検証するPythonコード" spellcheck="false">from peano import config_log, rational

config_log(log_level=21, max_lines=200, locale="ja")

half = rational(1, 2)
two_quarters = rational(2, 4)

print(half == two_quarters)</textarea>
  <div class="peano-runner__controls">
    <button class="peano-runner__button peano-runner__button--run" data-action="run">▶ 実行</button>
    <button class="peano-runner__button" data-action="reset">環境をリセット</button>
    <span class="peano-runner__shortcut">⌘ / Ctrl + Enter</span>
  </div>
  <div class="peano-runner__output-wrap">
    <span class="peano-runner__output-label">出力</span>
    <pre class="peano-runner__output" data-role="output" aria-live="polite">交差積の定義と有理数の等号ログを照合します。</pre>
  </div>
</div>

<details class="self-check"><summary>答えと途中の計算</summary><p>元の比較は True。変更後は 2×4＝8 と 3×2＝6 が違うので False です。表示される一行の比較の内側では、前章で作った整数の演算が働いています。</p></details>

<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>実験4 · 有理数の加法を確かめる</span>
    <span class="peano-runner__status" data-role="status">未実行</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="実験04: 有理数加法ログを検証するPythonコード" spellcheck="false">from peano import config_log, rational

config_log(log_level=24, max_lines=200, locale="ja")

answer = rational(1, 2) + rational(1, 3)

print(answer)</textarea>
  <div class="peano-runner__controls">
    <button class="peano-runner__button peano-runner__button--run" data-action="run">▶ 実行</button>
    <button class="peano-runner__button" data-action="reset">環境をリセット</button>
    <span class="peano-runner__shortcut">⌘ / Ctrl + Enter</span>
  </div>
  <div class="peano-runner__output-wrap">
    <span class="peano-runner__output-label">出力</span>
    <pre class="peano-runner__output" data-role="output" aria-live="polite">分子・分母の構築式と、表示された5/6を照合します。</pre>
  </div>
</div>

2つ目の実験で両方を 1/2 にすると、計算結果の分子は 1×2＋2×1＝4、分母は 2×2＝4 です。表示が 4/4 でも値は1です。分子・分母を簡単な形に直す手順は、次のメソッドに分けてあります。

## 約分で割る数は、どうやって見つける？

```python
def reduction(self) -> Rational:
    numerator = self.p.normalize()
    denominator = self.q.normalize()
    if denominator < Z_ZERO:
        numerator, denominator = -numerator, -denominator

    a, b = abs(numerator), abs(denominator)
    while b:
        a, b = b, a % b
    divisor = Integer(a, N_ZERO)
    return Rational(numerator // divisor, denominator // divisor)
```

6/−8 で追います。まず分母が負なので、分子と分母の符号を両方変えて −6/8 にします。この符号変更では、整数 (a, b) の二つの欄を交換します。右へ進む歩数と左へ進む歩数を入れ替えると符号が反対になるからです。次に絶対値の6と8から、両方を割り切る最大の数（最大公約数）を探します。

`a % b` は a を b で割った余りです。8＝6×1＋2 なので、8と6を両方割り切る数は余りの2も割り切ります。逆に6と2を割り切れば8も割り切れます。このようにペアを「割る数と余り」に替えても最大公約数は同じです。ループの (a, b) は (6, 8)、(8, 6)、(6, 2)、(2, 0) と進みます。コードの `while b` は「b が0になるまで繰り返す」という条件です。最後に残った自然数2を `Integer(a, N_ZERO)` で整数の2に直します。`//` は整数の商を取る記号です。ここでは割り切れる数を選んだので、−6 と8をそれぞれ2で割ると −3/4 が得られます。

<span class="lesson-layer" data-layer="test">等しさが関わる別の場面</span>

## 同じ分数を辞書のキーにしたら？

Pythonの辞書は、目印（キー）と、それに対応する値を組にして覚えます。たとえば `names = {rational(1, 2): "半分"}` と書いたら、`names[rational(2, 4)]` でも同じ「半分」が見つかってほしいところです。辞書は、キーを探す手がかりに**ハッシュ値**という整数を使います。1/2 をキーにして書いた値を 2/4 でも取り出すには、等しい二つのキーが同じハッシュ値を返す必要があります。

```python
def __hash__(self) -> int:
    reduced = self.reduction()
    if reduced.q == Z_ONE:
        return hash(reduced.p)
    return hash(("Rational", int(reduced.p), int(reduced.q)))
```

ここではまず `reduction()` を呼びます。1/2 も 2/4 も同じ組にしてからハッシュ値を作れるからです。分母が1なら整数と同じハッシュ値を返します。次のテストの一行目は、分子と分母を2倍した場合についてこの約束を確かめます。

```python
self.assertEqual(hash(rational(i, j)), hash(rational(i * 2, j * 2)))
self.assertEqual(rational(16, 9).reduction(), rational(16, 9))
```

```python
with self.assertRaises(ZeroDivisionError):
    rational(1, 0)
```

最後のテストは、分母が0の入力で決めた通りのエラーが出れば成功です。正しい結果を出せることと、作ってはいけない数を止められることの両方を試しています。

<span class="lesson-layer" data-layer="boundary">次の数が必要になる理由</span>

## 2乗して2になる分数はあるか

まず、分数の掛け算をコードに結びつけましょう。分子どうし、分母どうしを掛けるので、`Rational.__mul__` の答えは `Rational(self.p * converted.p, self.q * converted.q)` です。たとえば 3/2 の2乗は 9/4。次章でもこの計算を使います。

今度は逆に、2乗してちょうど2になる分数があると仮定します。その分数を約分しきって p/q と書くと、(p/q)²＝p²/q²＝2。両辺に q² を掛ければ p²＝2q² です。右辺が偶数なので p² は偶数。奇数の2乗は奇数だから、p も偶数です。そこで p＝2k と置いて戻すと、4k²＝2q²、つまり q²＝2k²。すると q も偶数です。分子も分母も2で割れるのは、約分しきったという出発点と矛盾します。

この正の数を √2（ルート2）と書きます。そこで次の章では、分数として保存できないこの数を「ある式を0にする数」として指定します。

<form class="knowledge-check" data-reveal>
  <fieldset>
    <legend>確認問題 · <code>rational(2,4)</code> を作った直後について正しい説明はどれですか。</legend>
    <label>
      <input type="radio" name="rational-check" data-feedback="作成時には自動約分せず、入力表現を保存します。">
      内部表現は必ず <code>1/2</code> へ変わる
    </label>
    <label>
      <input type="radio" name="rational-check" data-correct data-feedback="表現は2/4のままでも、交差積による等号で1/2と同じ値だと判定します。">
      表現は <code>2/4</code> のまま、値は <code>1/2</code> と等しい
    </label>
    <label>
      <input type="radio" name="rational-check" data-feedback="分母4は0ではないため、正しい入力です。">
      分子と分母がどちらも2で割れるので、作るときにエラーになる
    </label>
    <button type="submit">答え合わせ</button>
    <p class="knowledge-check__feedback" data-role="feedback" aria-live="polite"></p>
  </fieldset>
</form>

[第4章へ。式を保存し、答えがいくつあるか調べる](polynomials.md)
