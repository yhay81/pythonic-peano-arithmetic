<span class="lesson-number">第0章 · Pythonの仕組み</span>

# 自分で作った数に、どうやって「＋」を使う？

Pythonは整数の足し算を知っています。これから作る数は、私たちが保存のしかたを決めたデータです。それでも、使う側では普通に `two + one` と書きたい。計算の途中を表示できて、答えは次の計算にも使えるようにするには、どう書けばよいでしょう。

<div class="lesson-goals"><strong>この章の目標</strong><p>最後に、足し算の手順を呼ぶ行、途中経過を書く行、答えを返す行の三つを見つけます。</p></div>

## 記号から、実行する関数を見つける

Pythonでは、同じ種類のデータと、それに使える手順をひとまとめにしたものを**クラス**と呼びます。クラスに書いた関数が**メソッド**です。たとえば、次は点数を一つ持つ小さなクラスです。

```python
class Score:
    def __init__(self, points):
        self.points = points

    def __add__(self, other):
        return Score(self.points + other.points)
```

`a = Score(2)` と書くと、新しく作る点数が `self`、受け取った2が `points` になります。`self.points = points` が、その2を点数の中に保存する行です。

<p data-meta="operator-protocol">次に <code>b = Score(1)</code> として <code>a + b</code> を計算します。ここではPythonが左の点数の <code>__add__</code> を呼ぶので、<code>self</code> は <code>a</code>、<code>other</code> は <code>b</code> です。中身の整数を足し、3を持つ新しい点数を返します。</p>

<div class="implementation-bridge"><p>これから使う自然数のクラスも、同じ名前のメソッドを持っています。記号から手順を見つけるしくみは同じです。中でどんな足し算をするかは、次章で変わります。</p></div>

<p class="source-reference" data-source-reference="peano/utils.py" data-test-reference="tests/test_utils.py">元のファイルを読む　<a href="/assets/source/peano/utils.py">peano/utils.py</a> ／ <a href="/assets/source/tests/test_utils.py">tests/test_utils.py</a></p>

<div class="learning-prompt"><strong>実行する前に</strong><p>下の two と one は、この教材の自然数です。記号で足した答えと、メソッドを直接呼んだ答えを比べると、何が表示されるでしょう。</p></div>

<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>準備実験 · 演算子と特殊メソッド</span>
    <span class="peano-runner__status" data-role="status">未実行</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="演算子と特殊メソッドの対応を確かめるPythonコード" spellcheck="false">from peano import natural_number

two = natural_number(2)
one = natural_number(1)

via_operator = two + one
via_method = two.__add__(one)

print(via_operator)
print(via_operator == via_method)</textarea>
  <div class="peano-runner__controls">
    <button class="peano-runner__button peano-runner__button--run" data-action="run">▶ 実行</button>
    <button class="peano-runner__button" data-action="reset">環境をリセット</button>
    <span class="peano-runner__shortcut">⌘ / Ctrl + Enter</span>
  </div>
  <div class="peano-runner__output-wrap">
    <span class="peano-runner__output-label">出力</span>
    <pre class="peano-runner__output" data-role="output" aria-live="polite">実行すると、ここに答えが表示されます。</pre>
  </div>
</div>

<details class="self-check"><summary>2行の出力を読む</summary><p>最初の print は足し算の答えの3を、次の print は二つの計算結果が等しいかを表示します。等しいときのPythonの答えは True です。</p></details>

## 答えを変えずに、計算の記録を付ける

計算するたびに「今回はどの規則を使ったか」を読みたいとします。けれども、足し算の答えと説明文をセットで受け取ったら、続けて1を足すたびに答えを取り出す手間がかかります。そこで、計算する関数と、説明文を記録する関数に仕事を分けます。

<p data-meta="decorator">関数を受け取り、その前後に仕事を加えた関数を用意するしくみが<strong>デコレータ</strong>です。関数の上に書く <code>@log(...)</code> は、「以後、この名前で呼ぶときは記録係を通してね」という指定です。</p>

```python
def outer(func: Callable[P, tuple[T, LogMessage]]) -> Callable[P, T]:
    @wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        result, message = func(*args, **kwargs)
        if logger.isEnabledFor(log_level):
            logger.log(log_level, message if isinstance(message, str) else message())
        return result

    # このあと、公開する戻り型とシグネチャも更新する。
    ...
    return inner
```

`def` の行にある `Callable` は「呼び出せるもの」、`tuple[T, LogMessage]` は「答えと説明の組」という型のメモです。矢印 `-> T` の先には、記録係から受け取れる答えの型が書かれています。

内側の `inner` が記録係です。`*args, **kwargs` は、渡された引数をまとめて次の関数に渡す書き方です。次の3行に絞ると役割が見えます。

1. `result, message = func(...)` で元の計算を呼び、答えと説明を受け取ります。
2. 記録する設定なら `logger.log(...)` が説明を書きます。`message()` は、この時点で初めて説明文を作ります。
3. `return result` が答えだけを返します。だから足した結果を、また足し算に使えます。

外側の `return inner` は、クラスを用意するときに「これを記録係として使う」と関数を渡す行です。内側の `return result` は、実際に足し算したときに動きます。`@wraps(func)` は、記録係を通しても元の関数の名前などを調べられるようにします。抜粋中の `...` では、外から戻り値の型を調べたときにも、答えの型が見えるよう設定しています。

## 数のどの部分を保存するか

```python
@total_ordering
@dataclass(frozen=True, slots=True, eq=False, repr=False)
class Integer:
    a: NaturalNumber
    b: NaturalNumber
```

<p data-meta="dataclass">ここで <code>a</code> と <code>b</code> は整数の材料になる二つの自然数です。<code>@dataclass</code> は、この二つを受け取って保存する <code>__init__</code> を用意します。先ほどの Score で手書きした仕事です。</p>

`frozen=True` は作った数の中身をあとから書き換えないための指定、`slots=True` は使う属性名をあらかじめ定める指定です。`eq=False` と `repr=False` は等しさの判定と表示を自分で書くために付けます。たとえば分数は分子と分母が違っても同じ値になるので、二つの欄をそのまま比べるだけでは困ります。

`@total_ordering` は、等しいか、小さいかの判定から残りの大小比較を補います。作った直後に分母の確認などが必要なクラスは、`__post_init__` にその手順を書きます。

## 値を読むときに計算する

```python
@property
def coefficients(self) -> tuple[Rational, ...]:
    return self._coefficients
```

`@property` を付けると、利用者は `p.coefficients` と書くだけで上の関数を呼べます。この例では、保存済みの係数（式の各項に掛かる数）を返します。最終章の `interval.width` も同じ書き方ですが、その場で「右端−左端」を計算します。

## テストの一行を日本語で読む

<p data-meta="test-api"><code>self.assertEqual(two + one, three)</code> は、「二つの値を計算し、等しいかを確認する」と読みます。この行の <code>self</code> は検査を行う側です。足し算の中の <code>self</code> がどの数を指すかは、左辺の <code>two</code> で決まります。</p>

もし記録係が `return result, message` と書いてあったら、利用者に届くのは二つの値の組です。途中経過が正しく表示されても、上のテストは通りません。最後の問いでは、画面に出る説明と、計算の答えがどこへ行くかを追ってみてください。

<form class="knowledge-check" data-reveal>
  <fieldset>
    <legend>確認問題 · <code>@log</code> で包まれた演算から、利用者へ返るものはどれですか。</legend>
    <label>
      <input type="radio" name="python-check" data-feedback="説明文はログへ送られ、戻り値には含まれません。">
      計算結果と説明文のタプル
    </label>
    <label>
      <input type="radio" name="python-check" data-correct data-feedback="ラッパーが説明文をログへ送り、計算結果だけを返します。">
      計算結果
    </label>
    <label>
      <input type="radio" name="python-check" data-feedback="ログは副作用として記録されますが、戻り値ではありません。">
      説明文だけ
    </label>
    <button type="submit">答え合わせ</button>
    <p class="knowledge-check__feedback" data-role="feedback" aria-live="polite"></p>
  </fieldset>
</form>

[第1章で、自然数の足し算そのものを作る](natural-numbers.md)
