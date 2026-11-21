<span class="lesson-number">第1章 · 自然数</span>

# 足し算を使わずに、足し算を定義する

2＋2を「2に1を2回足す」と説明すると、その説明の中でもう足し算を使っています。そこで、最初に使えるのは0と「次の数を作る」操作だけと決めてみましょう。これだけで、どの二つの自然数についても答えが決まるでしょうか。

<div class="lesson-goals"><strong>この章の目標</strong><p>2＋2を計算するプログラムを読み、なぜ最初に2＋0の記録が出るのか説明します。</p></div>

<span class="lesson-layer" data-layer="definition">数の規則</span>

## まず、何を出発点にするか

この章では0も自然数に含めます。ある数 n の次の数を **後者** と呼び、`S(n)` と書きます。1は `S(0)`、2は `S(S(0))` の略だと思ってください。

このように0と後者から自然数を考えるのが、ペアノ算術の出発点です。最初に認める規則を**公理**といいます。0は自然数で、どの自然数にも後者があります。0はどの数の後者にもならず、違う数が同じ後者を持つこともありません。こうして0から始めた列が途中で輪になったり、別の数と合流したりすることを防ぎます。すべての自然数について考えるときには、後で使う数学的帰納法の規則もあります。

<span class="lesson-layer" data-layer="representation">数を保存する</span>

## 2の中に、何を入れておく？

<div class="implementation-bridge"><p>2を作るときには1を、1を作るときには0を中に入れます。逆向きにたどれば、どんな手順でできた数かを取り出せます。</p></div>

```python
@total_ordering
@dataclass(frozen=True, slots=True, eq=False, repr=False)
class NaturalNumber:
    pre: NaturalNumber | None = None

    def __post_init__(self) -> None:
        if self.pre is not None and not isinstance(self.pre, NaturalNumber):
            raise TypeError("pre must be a NaturalNumber or None")
```

`pre` は一つ前の数です。0には前の数がないので、そこには `None` を入れます。`NaturalNumber | None` は「ここに来るのは自然数か None」という型の読み方です。最後の `if` は、文字列などが紛れたらその場で止めます。

```python
N_ZERO = NaturalNumber()
N_ONE = NaturalNumber(N_ZERO)


def successor(number: NaturalNumber) -> NaturalNumber:
    if not isinstance(number, NaturalNumber):
        raise TypeError("successor expects a NaturalNumber")
    return NaturalNumber(number)


def natural_number(value: int) -> NaturalNumber:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("only int values can be converted to NaturalNumber")
    if value < 0:
        raise ValueError("a NaturalNumber cannot be negative")
    result = N_ZERO
    for _ in range(value):
        result = successor(result)
    return result
```

`N_ZERO` は最初に作った0です。`successor(result)` は今の数を一つ前の数として持つ、新しい数を作ります。`for _ in range(value)` はこれを `value` 回繰り返す行です。

`natural_number(2)` の `result` を追うと、ループの前は0、1周目は0を中に持つ数、2周目はその数を中に持つ数です。こうしてできた2の `pre` を2回読むと0に戻れます。

```python
def structural_str(self) -> str:
    depth = 0
    current = self
    while current.pre is not None:
        depth += 1
        current = current.pre
    return f"{'S(' * depth}0{')' * depth}"
```

この `while` は戻った回数を `depth` に数えます。2なら2回なので、`S(` を二つ、0を一つ、閉じかっこを二つ並べて `S(S(0))` と表示します。あとで計算の途中に出てくる表記です。

<p class="source-reference" data-source-reference="peano/natural_number.py" data-test-reference="tests/test_natural_number.py">元のファイルを読む　<a href="/assets/source/peano/natural_number.py">peano/natural_number.py</a> ／ <a href="/assets/source/tests/test_natural_number.py">tests/test_natural_number.py</a></p>

<span class="lesson-layer" data-layer="implementation">コードを読む</span>

## 等しさの実装で、二つの公理を読む

2と1を比べます。両方とも後者なので、等しいかを調べるには、それぞれを一つ戻して1と0を比べれば十分です。違う数は同じ後者になれないからです。この性質を**単射性**と呼びます。

```python
@log(log_level=1)
def __eq__(self, other: object) -> tuple[bool, LogMessage]:
    if not isinstance(other, NaturalNumber):
        return (
            cast(bool, NotImplemented),
            lambda: f"{self!r} == {other!r} = NotImplemented",
        )
    left_predecessor = self.pre
    right_predecessor = other.pre
    if left_predecessor is None or right_predecessor is None:
        result = left_predecessor is None and right_predecessor is None
        return (
            result,
            lambda: (
                f"{translate('equality.zero')} "
                f"eq({self.structural_str()}, "
                f"{other.structural_str()}) -> {result}"
            ),
        )
    return (
        left_predecessor == right_predecessor,
        lambda: (
            f"{translate('equality.successor')} "
            f"eq({self.structural_str()}, "
            f"{other.structural_str()}) -> "
            f"eq({left_predecessor.structural_str()}, "
            f"{right_predecessor.structural_str()})"
        ),
    )
```

第0章で `+` が `__add__` を呼んだのと同じように、二つの自然数を `==` で比べると `__eq__` が呼ばれます。`return result, lambda: ...` は、答えと「あとで説明文を作る関数」の組を返す書き方です。記録係が必要なときにこの関数を呼びます。答えを決めるのはその手前です。片方の `pre` が `None` ならその数は0。もう片方も0のときだけ `True` を返します。両方に前の数があれば、最後の `left_predecessor == right_predecessor` で一段短い比較を始めます。

<div class="learning-prompt"><strong>実行する前に</strong><p>下の <code>config_log</code> は記録の設定です。<code>locale="ja"</code> は日本語表示、<code>max_lines</code> は表示する行数の上限です。入力の数は <code>left</code> と <code>right</code> で決めます。2と1を比べたとき、どちらが先に0になりますか。続いて右側も2に変えたら、最後に比較する二つの数は何でしょう。</p></div>

<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>実験1A · 等値判定と公理を確かめる</span>
    <span class="peano-runner__status" data-role="status">未実行</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="実験1A: 自然数の等値実装とペアノの公理を確かめるPythonコード" spellcheck="false">from peano import config_log, natural_number

config_log(log_level=1, max_lines=20, locale="ja")

left = natural_number(2)
right = natural_number(1)
answer = left == right

print(answer)</textarea>
  <div class="peano-runner__controls">
    <button class="peano-runner__button peano-runner__button--run" data-action="run">▶ 実行</button>
    <button class="peano-runner__button" data-action="reset">環境をリセット</button>
    <span class="peano-runner__shortcut">⌘ / Ctrl + Enter</span>
  </div>
  <div class="peano-runner__output-wrap">
    <span class="peano-runner__output-label">出力</span>
    <pre class="peano-runner__output" data-role="output" aria-live="polite">前者の比較へ戻り、0と後者を区別する順序と照合します。</pre>
  </div>
</div>

<details class="self-check"><summary>比較が止まるところを見る</summary><p>2と1なら、一つ戻したところで1と0になり、答えは False です。2と2なら、1と1、次に0と0へ進むので True になります。</p></details>

## 帰納法と再帰を、同じものにしない

いまの比較が必ず止まるのは、`pre` を読むたびに鎖が短くなるからです。小さい場合の答えを使って次の場合を計算する、この書き方を**再帰**と呼びます。

一方、「どの自然数でも成り立つ」と説明したいときに使うのが**数学的帰納法**です。たとえば「n回『次へ』と進んで作った数は、n回戻ると0に着く」と示してみます。出発点の0なら0回で着きます。ある数でこれが正しいとすると、その後者からはまず1回で元の数へ戻り、あとは既に分かっている道をたどれます。この二つを示すと、どこまで先の数にも説明が届きます。

## `+` は、どのメソッドを呼ぶのか

2＋2の右側の2には「1の次」という情報があります。そこで、先に2＋1を計算し、その答えの次を取ることにします。2＋1でも同じことができます。最後に必要な2＋0の答えは2です。左側を n、右側の一つ前を m と書けば、足し算の**定義**は次の二行になります。

| 右側の形 | 答え |
| --- | --- |
| 0 | n＋0＝n |
| S(m) | n＋S(m)＝S(n＋m) |

この二行を `NaturalNumber.__add__` の中で探しましょう。`self` が左の数、`other` が右の数です。まず、自然数どうしの計算に使う行だけを取り出します。

```python
predecessor = other.pre
if predecessor is None:
    return self
return successor(self + predecessor)
```

最後の行のかっこの内側が、表の n＋m です。右の数から `pre` を一つ取ったので、元の問題より右辺が小さくなりました。その答えを待って外側の `successor` が一つ先へ進めます。実際のメソッドでは、この二つの答えにそれぞれ記録用の関数を添えます。

```python
@log(log_level=4)
def __add__(self, other: object) -> tuple[NaturalNumber, LogMessage]:
    if not isinstance(other, NaturalNumber):
        return (
            cast(NaturalNumber, NotImplemented),
            lambda: f"{self!r} + {other!r} = NotImplemented",
        )
    predecessor = other.pre
    if predecessor is None:
        return (
            self,
            lambda: (
                f"{translate('addition.base')} "
                f"add({self.structural_str()}, 0) "
                f"-> {self.structural_str()}"
            ),
        )
    return (
        successor(self + predecessor),
        lambda: (
            f"{translate('addition.recursive')} "
            f"add({self.structural_str()}, "
            f"{other.structural_str()}) -> "
            f"S(add({self.structural_str()}, {predecessor.structural_str()}))"
        ),
    )
```

`isinstance` は、この足し算で扱える相手かを確かめます。扱えない型のときに返す `NotImplemented` は「この組み合わせはこのメソッドでは計算できない」というPythonへの合図です。自然数どうしなら、`predecessor` が空かどうかで上の表の行が決まります。

<span class="lesson-layer" data-layer="trace">順番を追う</span>

## 先に呼んだ計算が、最後に表示される理由

<p data-meta="log-decorator">第0章の記録係 <code>@log</code> は、元の関数から答えと説明を受け取ってから説明を書きます。そこで、呼び出す順と、答えが決まる順を別々に書いてみます。</p>

| 呼び出す順 | その場で答えが出るか |
| --- | --- |
| 2＋2 | 2＋1の答えを待つ |
| 2＋1 | 2＋0の答えを待つ |
| 2＋0 | 2をすぐ返せる |

ここから表を下から読んでください。2＋0が2を返すと、待っていた2＋1は、返ってきた自然数2を `successor` に渡して3を返せます。それを待っていた2＋2が4を返して計算終了です。

<div class="learning-prompt"><strong>実行する前に</strong><p>最初に答えが決まる行には「加法・基底」、小さい計算から戻る行には「加法・再帰」と出ます。2＋2ではそれぞれ何行出るでしょう。</p></div>

<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>実験1B · 加法の実行順を確かめる</span>
    <span class="peano-runner__status" data-role="status">未実行</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="実験1B: 自然数加法の実装ログを確かめるPythonコード" spellcheck="false">from peano import config_log, natural_number

config_log(log_level=4, max_lines=200, locale="ja")

n = natural_number(2)
m = natural_number(2)
answer = n + m

print(answer)</textarea>
  <div class="peano-runner__controls">
    <button class="peano-runner__button peano-runner__button--run" data-action="run">▶ 実行</button>
    <button class="peano-runner__button" data-action="reset">環境をリセット</button>
    <span class="peano-runner__shortcut">⌘ / Ctrl + Enter</span>
  </div>
  <div class="peano-runner__output-wrap">
    <span class="peano-runner__output-label">出力</span>
    <pre class="peano-runner__output" data-role="output" aria-live="polite">実装から予想した「戻りの順」と照合します。</pre>
  </div>
</div>

<details class="self-check"><summary>画面の4行を読む</summary><p>基底が1行、再帰が2行、最後の print が1行です。途中の S は「次の数」、add は足し算を表す表示です。右辺を3にすると、答えを待つ呼び出しが一つ増えます。</p></details>

<span class="lesson-layer" data-layer="test">規則をテストする</span>

## たまたま4になっただけではないか

```python
self.assertEqual(n + natural_number(0), n)
self.assertEqual(n + successor(m), successor(n + m))
```

最初のテストは「右が0なら左を返す」、次は「右が後者なら、小さい計算の後者を返す」という約束を調べます。たとえば2行目に n＝3、m＝1 を入れると、左は3＋2、右は「3＋1の次」です。違う入力も試せば、4を返すだけの間違った実装を見つけられます。有限個のテストを通ったことと、任意の n、m について示す証明は別です。

<span class="lesson-layer" data-layer="boundary">掛け算へ進む</span>

## 同じ考え方で、3×2を組み立てる

右側が0なら積は0。右側が一つ増えたら、前の積に左の数を一つ足します。3×2なら、3×0＝0、3×1＝3＋0、3×2＝3＋3です。この二行の規則を `__mul__` では、右が0なら `N_ZERO`、それ以外なら `self + self * predecessor` と書いています。今度は、さきほど自分で定義した足し算が道具として使えます。

<form class="knowledge-check" data-reveal>
  <fieldset>
    <legend>確認問題 · <code>2+2</code> のログで <code>加法・基底</code> が最初に記録されるのはなぜですか。</legend>
    <label>
      <input type="radio" name="natural-check" data-feedback="log_levelは表示対象を選ぶ設定であり、順序を反転しません。">
      <code>log_level=4</code> が式を逆順に並べるから
    </label>
    <label>
      <input type="radio" name="natural-check" data-correct data-feedback="内側の再帰呼び出しが完了し、基底ケースから戻るときにログが記録されます。">
      ログは再帰呼び出しが戻ったあとに記録されるから
    </label>
    <label>
      <input type="radio" name="natural-check" data-feedback="Pythonのprintではなく、@logデコレータが各行を記録しています。">
      <code>print(answer)</code> が0から順に表示するから
    </label>
    <button type="submit">答え合わせ</button>
    <p class="knowledge-check__feedback" data-role="feedback" aria-live="polite"></p>
  </fieldset>
</form>

[第2章へ。自然数の足し算だけで、負の数の等しさを決める](integers.md)
