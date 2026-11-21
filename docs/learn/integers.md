<span class="lesson-number">第2章 · 整数</span>

# 引き算がまだなくても、負の数を作れるか

前章では自然数を足せるようになりました。けれども1から3を引こうとすると、0の先で行き止まります。そこで「1から3を引いた答え」の代わりに、まず材料の1と3をそのまま記録します。ここで問題になるのは、1−3と2−4のように、記録が違っても同じ場所に着く場合です。

<div class="lesson-goals"><strong>この章の目標</strong><p>自然数の足し算だけで二組が同じ整数を表すか判定し、組を取り替えても足し算の答えが変わらない理由を説明します。</p></div>

<span class="lesson-layer" data-layer="definition">等しさを決める</span>

## 引き算を、両辺の足し算に書き換える

組 (a, b) を「右へ a 歩、左へ b 歩」と読みます。(3, 1) と (4, 2) はどちらも0から右へ2歩の位置に着きます。引き算が使える人には 3−1＝4−2 でおしまいです。前章のプログラムにも分かる形にしてみましょう。

両辺に1と2を足すと、左では −1 と ＋1 が、右では −2 と ＋2 が消えます。残るのは **3＋2＝4＋1**。これなら計算できます。一般に (a, b) と (c, d) が同じ整数を表す条件は **a＋d＝b＋c** です。この規則で同じ値をまとめることを**同値関係**、値を表す個々の組を**代表元**と呼びます。

<span class="lesson-layer" data-layer="representation">組を保存する</span>

<div class="implementation-bridge"><p>数学で (a, b) と書いた二つの欄を、Pythonでは <code>self.a</code> と <code>self.b</code> に保存します。負の数でも、欄の中身はどちらも自然数です。</p></div>

```python
@total_ordering
@dataclass(frozen=True, slots=True, eq=False, repr=False)
class Integer:
    a: NaturalNumber
    b: NaturalNumber

    def __post_init__(self) -> None:
        if not isinstance(self.a, NaturalNumber) or not isinstance(
            self.b, NaturalNumber
        ):
            raise TypeError(
                "Integer.a and Integer.b must be NaturalNumber values"
            )
```

<p data-meta="dataclass-equality"><code>__post_init__</code> は二つの欄が自然数かを確認します。<code>eq=False</code> と指定したのは、欄を一つずつ比べる自動判定を使うと、(3, 1) と (4, 2) が違う答えになってしまうからです。</p>

<p class="source-reference" data-source-reference="peano/integer.py" data-test-reference="tests/test_integer.py">元のファイルを読む　<a href="/assets/source/peano/integer.py">peano/integer.py</a> ／ <a href="/assets/source/tests/test_integer.py">tests/test_integer.py</a></p>

<span class="lesson-layer" data-layer="implementation">自分で比較を書く</span>

## 同じ型にそろえてから、斜めに足す

```python
def _coerce_integer(value: object) -> Integer | None:
    if isinstance(value, NaturalNumber):
        return n2z(value)
    if isinstance(value, Integer):
        return value
    return None
```

`_coerce_integer` は計算相手の種類を調べる関数です。自然数 n が来たら、同じ値を表す整数 (n, 0) に直します。整数ならそのまま通し、それ以外なら `None` で「ここでは扱えない」と伝えます。

```python
@log(log_level=11)
def __eq__(self, other: object) -> tuple[bool, LogMessage]:
    converted = _coerce_integer(other)
    if converted is None:
        return (
            cast(bool, NotImplemented),
            lambda: f"{self!r} == {other!r} = NotImplemented",
        )
    result = self.a + converted.b == self.b + converted.a
    return (
        result,
        lambda: (
            f"{self!r} == {converted!r} ⇔ "
            f"{self.a!r} + {converted.b!r} == "
            f"{self.b!r} + {converted.a!r}"
        ),
    )
```

等しさを決めるのは `result =` の一行です。左の組を `self`、右の組を `converted` と読めば、左の a と右の b を足すのが式の左辺、左の b と右の a を足すのが右辺です。二つの和は自然数なので、最後の `==` には前章の比較が使えます。

## 足し算で、どちらの組を選んでもよい理由

(3, 1) に (1, 4) を足します。動きを続けて行うなら、右へは合計4歩、左へは合計5歩。だから答えを (4, 5) と記録できます。`__add__` は次の一行でこの組を作ります。

```python
result = Integer(self.a + converted.a, self.b + converted.b)
```

最初の組を (4, 2) に取り替えると、答えは (5, 6) です。右と左が同じだけ増えたので、着く場所はやはり−1。一般にも、片方の組の両方の欄に同じ数を足せば、答えの二つの欄にも同じ数が加わります。これで、たまたま選んだ代表元に左右されずに足し算ができます。

<span class="lesson-layer" data-layer="trace">比較を実行する</span>

<div class="learning-prompt"><strong>実行する前に</strong><p>下の right の最後の2を3にすると、斜めの和はそれぞれいくつになるでしょう。まず元のまま実行し、次に一か所だけ変えてください。</p></div>

<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>実験2 · 整数の等値判定を確かめる</span>
    <span class="peano-runner__status" data-role="status">未実行</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="実験02: 整数の同値関係と等号ログを検証するPythonコード" spellcheck="false">from peano import Integer, config_log, natural_number

config_log(log_level=11, max_lines=200, locale="ja")

left = Integer(natural_number(3), natural_number(1))
right = Integer(natural_number(4), natural_number(2))

print(left == right)</textarea>
  <div class="peano-runner__controls">
    <button class="peano-runner__button peano-runner__button--run" data-action="run">▶ 実行</button>
    <button class="peano-runner__button" data-action="reset">環境をリセット</button>
    <span class="peano-runner__shortcut">⌘ / Ctrl + Enter</span>
  </div>
  <div class="peano-runner__output-wrap">
    <span class="peano-runner__output-label">出力</span>
    <pre class="peano-runner__output" data-role="output" aria-live="polite">定義 → 実装 → 整数の等号ログを照合します。</pre>
  </div>
</div>

<details class="self-check"><summary>二つの和と答えを確かめる</summary><p>元の組なら 3＋2 と 1＋4 がともに5なので True。変更後は 3＋3＝6 と 1＋4＝5 なので False です。数字が何組表示されても、最後の print が答える問いは「同じ整数か」です。</p></details>

<span class="lesson-layer" data-layer="test">違う組でも試す</span>

## 負の数についても確かめる

```python
for i in range(-10, 10):
    for j in range(abs(i), 10):
        self.assertEqual(
            integer(i),
            Integer(natural_number(i + j), natural_number(j)),
        )
```

`i` は表したい整数、`j` は両方の欄をどれだけずらすかを決める数です。i＝−2、j＝3 なら右側の組は (1, 3)。次の j＝4 なら (2, 4)。どちらも左側の−2と等しいはずです。`j` を `abs(i)` 以上にしているので、i が負でも `i + j` は自然数の範囲に収まります。

<span class="lesson-layer" data-layer="boundary">表し方をそろえる</span>

## 値を比べることと、組を書き直すこと

```python
def normalize(self) -> Integer:
    if self.a >= self.b:
        return Integer(self.a - self.b, N_ZERO)
    return Integer(N_ZERO, self.b - self.a)
```

`normalize()` は右と左で打ち消し合う歩数を取り除きます。(1, 3) なら2行目の条件が偽なので最後の行に進み、(0, 2) を返します。引く向きを場合分けしたおかげで、欄の中で必要になる引き算は常に自然数の範囲に収まります。このように代表の形をそろえる操作が**正規化**です。比較だけなら、先ほどの斜めの足し算で十分です。

<form class="knowledge-check" data-reveal>
  <fieldset>
    <legend>確認問題 · <code>Integer(3,1)</code> と <code>Integer(4,2)</code> が等しいのはなぜですか。</legend>
    <label>
      <input type="radio" name="integer-check" data-feedback="保存されている二つの属性は異なります。">
      二つの代表元が同じ属性を保存しているから
    </label>
    <label>
      <input type="radio" name="integer-check" data-correct data-feedback="3+2と1+4がともに5なので、同じ差を表す代表元だと判定されます。">
      交差和 <code>3+2</code> と <code>1+4</code> が等しいから
    </label>
    <label>
      <input type="radio" name="integer-check" data-feedback="この実装は入力した代表元を自動的には正規化しません。">
      代表元が自動的に正規化されたから
    </label>
    <button type="submit">答え合わせ</button>
    <p class="knowledge-check__feedback" data-role="feedback" aria-live="polite"></p>
  </fieldset>
</form>

[第3章へ。分子と分母の組で、分数を作る](rationals.md)
