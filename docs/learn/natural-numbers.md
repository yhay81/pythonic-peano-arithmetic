<span class="lesson-number">第1章 · 自然数</span>

# 公理から実装を読み、ログを検証する

<p class="lesson-lead">
  <code>0, 1, 2, …</code> を使うだけでなく、何を出発点として認め、
  ライブラリがそれをどう保存し、<code>+</code> をどう実行するかまで読みます。
  ログは、実装を理解したあとに妥当性を確かめる材料です。
</p>

<div class="lesson-context" data-reveal>
  <div>
    <strong>ここまでに分かったこと</strong>
    <p>演算子と特殊メソッド、dataclassのコード生成、デコレータ適用前後の違い。</p>
  </div>
  <div>
    <strong>この章で学ぶこと</strong>
    <p>ペアノの公理、データ表現、メソッド、再帰、呼び出しと戻りの順番です。</p>
  </div>
</div>

<div class="lesson-goals" data-reveal>
  <strong>この章を終えると</strong>
  <ul>
    <li>ペアノの公理と、このライブラリの表現上の選択を区別できる</li>
    <li>0と後者の区別、後者の単射性を <code>__eq__</code> の分岐へ対応付けられる</li>
    <li>加法の再帰的定義と <code>NaturalNumber.__add__</code> を対応付けられる</li>
    <li>なぜ <code>2+0</code> のログが最初に出るのか、実装から説明できる</li>
  </ul>
</div>

<div class="implementation-bridge" data-reveal aria-label="自然数の数学・表現・実装">
  <div>
    <strong>数学</strong>
    <p><code>0</code> と後者 <code>S</code> を出発点にし、再帰で加法を定義します。</p>
  </div>
  <div>
    <strong>データ表現</strong>
    <p><code>pre=None</code> が0、<code>pre=n</code> が <code>S(n)</code> です。</p>
  </div>
  <div>
    <strong>実装</strong>
    <p><code>successor</code>、<code>structural_str</code>、<code>__eq__</code>、<code>__add__</code>、<code>@log</code> を読みます。</p>
  </div>
</div>

<div class="source-reference"
     data-source-reference="peano/natural_number.py"
     data-test-reference="tests/test_natural_number.py">
  <strong>この章で横に置く実装</strong>
  <p>
    完全なクラスと生成関数:
    <a href="/assets/source/peano/natural_number.py"><code>peano/natural_number.py</code></a>。
    本文では <code>NaturalNumber</code>、<code>successor</code>、
    <code>natural_number</code>、<code>structural_str</code>、
    <code>__eq__</code>、<code>__add__</code> を必要な順に抜粋します。
  </p>
  <p>
    定義式の検査:
    <a href="/assets/source/tests/test_natural_number.py"><code>tests/test_natural_number.py</code></a>。
    ファイル索引は<a href="/reference/implementation/">実装リファレンス</a>にあります。
  </p>
</div>

<span class="lesson-layer" data-layer="definition">数学上の定義</span>

## 公理と定義を分ける

**公理**とは、その体系で出発点として採用する規則です。ペアノ算術では、
自然数について大まかに次のことを認めます。

| 公理の役割 | この章での読み方 |
| --- | --- |
| 0が自然数である | 出発点が一つある |
| 自然数 `n` には後者 `S(n)` がある | 次の数を作れる |
| 0は誰かの後者ではない | 0と `S(n)` を区別できる |
| `S(n)=S(m)` なら `n=m` | 次の数が同じなら、元の数も同じ |
| 数学的帰納法 | 0で成り立ち、後者へ進める性質は全自然数で成り立つ |

一方、次の二式はペアノの**公理そのものではなく**、
0と後者を使って加法を決める**再帰的定義**です。

<div class="peano-equation" data-reveal>
n + 0 = n<br>
n + S(m) = S(n + m)
</div>

最初の式は計算を止める**基底ケース**、二つ目は右の数を一段小さくする
**再帰ケース**です。この区別が、そのままPythonの `if` の二つの枝になります。

<span class="lesson-layer" data-layer="representation">データの表し方</span>

## 0と後者を、Pythonの値にする

実装の先頭は次の形です。準備章で見たdataclassの指定が、
ペアノの表現を作成後に変更できない値として支えます。

```python
@total_ordering
@dataclass(frozen=True, slots=True, eq=False, repr=False)
class NaturalNumber:
    pre: NaturalNumber | None = None

    def __post_init__(self) -> None:
        if self.pre is not None and not isinstance(self.pre, NaturalNumber):
            raise TypeError("pre must be a NaturalNumber or None")
```

`pre` は predecessor、つまり「一つ前の自然数」です。`None` は
「前の数がない」というPythonの値です。
生成された `__init__` が `pre` を保存したあと、`__post_init__` が自動で呼ばれます。
これにより `pre` は `None` か別の `NaturalNumber` に限られ、鎖の途中へ
無関係な型が入ることを防ぎます。

<div class="meta-note" data-meta="natural-dataclass" data-reveal>
  <strong>生成を使う部分と、止める部分</strong>
  <p>
    <code>__init__</code> はdataclassに生成させます。一方、
    <code>eq=False</code> と <code>repr=False</code> により、
    再帰構造をたどる等値比較と、構成を見せる表示は手書きします。
  </p>
</div>

| 数学 | 実際の構築 | `pre` の中身 |
| --- | --- | --- |
| `0` | `NaturalNumber()` | `None` |
| `S(0)=1` | `NaturalNumber(zero)` | 0のオブジェクト |
| `S(S(0))=2` | `NaturalNumber(one)` | 1のオブジェクト |

実ファイルでは、0と1、後者、教材用の生成関数を次のように用意しています。

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

`successor(n)` が `NaturalNumber(n)` を返すことから、数学の `S(n)` と
Pythonの `NaturalNumber(pre=n)` の対応を確認できます。
また、`natural_number(2)` のループを読むと、Python整数2を保存するのではなく、
0から `successor` を2回呼び、`S(S(0))` を構築すると分かります。

同じ値には、用途の異なる三つの表示があります。`str`と`repr`は値を短く読み、
`structural_str`は0と後者だけで構築過程を読みます。

```python
def structural_str(self) -> str:
    depth = 0
    current = self
    while current.pre is not None:
        depth += 1
        current = current.pre
    return f"{'S(' * depth}0{')' * depth}"
```

| 呼び出し | `natural_number(2)`の表示 | 用途 |
| --- | --- | --- |
| `str(n)` | `2` | 最終結果を人が読む |
| `repr(n)` | `<N(2)>` | Pythonオブジェクトの種類と値を短く読む |
| `n.structural_str()` | `S(S(0))` | 0と後者の構成を読む |

自然数の核となる等値・加法・乗法のログでは、通常の数字と後者表記を混ぜず、
三つ目の構造表示を使います。

!!! note "この表現から分かるライブラリの特性"
    各値は一つ前の値をたどれる鎖です。値は作成後に変更できない不変オブジェクトで、
    高速な整数計算より、0と後者の構造が実装から見えることを優先しています。

<span class="lesson-layer" data-layer="implementation">Pythonでの実装</span>

## 等しさの実装で、二つの公理を読む

`eq=False`にした理由は、dataclassの属性比較へ任せず、0と後者の規則を
コードに残すためです。次の`__eq__`では、`NaturalNumber`以外の型を扱う
最初の分岐を除くと、二つのペアノの公理との対応が見えます。

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
                f"{localized('[equality: zero case]', '[等値・0の場合]')} "
                f"eq({self.structural_str()}, "
                f"{other.structural_str()}) -> {result}"
            ),
        )
    return (
        left_predecessor == right_predecessor,
        lambda: (
            f"{localized('[equality: successor case]', '[等値・後者の場合]')} "
            f"eq({self.structural_str()}, "
            f"{other.structural_str()}) -> "
            f"eq({left_predecessor.structural_str()}, "
            f"{right_predecessor.structural_str()})"
        ),
    )
```

| 公理 | 実装上の対応 |
| --- | --- |
| 0は誰かの後者ではない | 一方の`predecessor`だけが`None`なら`result`は`False` |
| `S(n)=S(m)`なら`n=m` | 両方に前者があれば二つの`predecessor`の比較へ戻る |

後者が等しいなら元の数も等しく、異なる二数から同じ後者が生まれない性質を
**単射性**と呼びます。ログの`eq(a, b)`は、新しいPython関数ではなく、
`a.__eq__(b)`による比較を数式に近い形で表した記号です。

二つの後者を比較するたびに、一段前の値の比較へ進みます。最後に
`0 == 0`なら真、`0 == S(n)`なら偽になるため、有限の鎖全体の等しさが決まります。

<div class="learning-prompt" data-kind="prediction" data-reveal>
  <strong>公理から実装の分岐を予想</strong>
  <p>
    <code>eq(S(S(0)), S(0))</code>は、
    <code>eq(S(0), 0)</code>へ進んだあと真と偽のどちらになるか。
    <code>pre is None</code>を根拠に答えてください。
  </p>
</div>

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

<details class="self-check" data-reveal>
  <summary>等値ログを公理へ戻して確認する</summary>
  <ol>
    <li><code>等値・0の場合</code>で<code>eq(S(0), 0)</code>が偽だと決まります。</li>
    <li><code>等値・後者の場合</code>は、元の比較が一つ前の値の比較へ帰着したことを記録します。</li>
    <li>最後の<code>False</code>は、<code>left == right</code>の公開結果です。</li>
  </ol>
</details>

## 帰納法と再帰を、同じものにしない

通常の公開APIから作る`NaturalNumber`は、0か、既に作られた自然数の後者です。
したがって、値を処理する関数は「0の場合」と「`S(n)`の場合」に分けられます。
加法は、この**再帰原理**を右辺へ適用したものです。

一方、数学的帰納法は、ある性質が0で成り立ち、`n`から`S(n)`へ受け継がれるなら、
すべての自然数で成り立つと示す**証明原理**です。Pythonのクラスや有限個のテストが、
帰納法そのものを証明するわけではありません。この実装は、帰納法で読みやすい
0と後者の有限構造を提供しています。

## `+` は、どのメソッドを呼ぶのか

準備章の対応どおり、`n + m` は `n.__add__(m)` へ委譲されます。
ここで `self` は左辺 `n`、`other` は右辺 `m` です。

次は `NaturalNumber.__add__` の完全な実装です。直前の `@log` も含めて読みます。
各 `return` は、計算結果とログ用の説明文を遅延生成する関数を組にして返します。
まずログ用の部分を脇へ置いて結果だけ読むと、数学的な核は次の二行です。

```python
predecessor = other.pre
if predecessor is None:
    return self
return successor(self + predecessor)
```

実ファイルでは、この結果に「どの規則を適用したか」を返す処理を加えています。

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
                f"{localized('[addition: base]', '[加法・基底]')} "
                f"add({self.structural_str()}, 0) "
                f"-> {self.structural_str()}"
            ),
        )
    return (
        successor(self + predecessor),
        lambda: (
            f"{localized('[addition: recursive]', '[加法・再帰]')} "
            f"add({self.structural_str()}, "
            f"{other.structural_str()}) -> "
            f"S(add({self.structural_str()}, {predecessor.structural_str()}))"
        ),
    )
```

最初の `isinstance` はPythonの型境界です。数学の二つの定義式に対応するのは、
そのあとの基底ケースと再帰ケースです。
数学と実装を一行ずつ対応させると、偶然似ているのではなく、
同じ定義を別の記法で書いていることが分かります。

| 加法の定義 | 実装の条件・処理 |
| --- | --- |
| `n + 0 = n` | `predecessor is None`なら`self`を返す |
| `n + S(m) = S(n + m)` | `successor(self + predecessor)`を返す |

`predecessor = other.pre`は、`S(m)`から一つ前の`m`を取り出します。
そのため再帰呼び出しの右辺は必ず一段小さくなり、最後は0へ到達します。
`lambda: f"..."` は、呼ばれたときに説明文を作る引数なしの関数です。
ログを表示しない実行では呼ばれません。`[加法・基底]`と
`[加法・再帰]`は、どちらの再帰式を適用したかを示す規則名です。
ログの`add(a, b)`は`a + b`、つまり`a.__add__(b)`を表す表示上の記号であり、
別の公開関数を呼んでいるわけではありません。

<span class="lesson-layer" data-layer="trace">実行して確かめる</span>

## ログは「呼び出し時」ではなく「戻り時」に出る

<div class="meta-note" data-meta="log-decorator" data-reveal>
  <strong>デコレータ適用前後を分ける</strong>
  <p>
    元の <code>__add__</code> は <code>(result, message_factory)</code> を返します。
    クラスから公開される <code>__add__</code> は <code>@log</code> が作ったラッパーで、
    ログ有効時だけmessage_factoryを呼んで記録し、resultだけを返します。
  </p>
</div>

ラッパーは元の `__add__` を呼び、その二つを受け取って次の順に動きます。

```python
result, message = func(...)
if logger.isEnabledFor(log_level):
    logger.log(log_level, message if isinstance(message, str) else message())
return result
```

重要なのは、`func(...)` の計算が終わった**あと**でログを書くことです。
`2+2` では、まず呼び出しが0へ向かって深くなります。

| 呼び出しの順番 | 右の値 | 実装が次にすること |
| ---: | --- | --- |
| 1 | `S(S(0))` | `add(S(S(0)), S(0))`を先に計算する |
| 2 | `S(0)` | `add(S(S(0)), 0)`を先に計算する |
| 3 | `0` | 基底ケースなので`S(S(0))`を返す |

その後、結果とログが内側から外側へ戻ります。

| 戻る順番 | 得られる結果 | 記録する定義 |
| ---: | --- | --- |
| 1 | `S(S(0))` | `[加法・基底] add(S(S(0)), 0) → S(S(0))` |
| 2 | `S(S(S(0)))` | `[加法・再帰] add(S(S(0)), S(0)) → S(add(S(S(0)), 0))` |
| 3 | `S(S(S(S(0))))` | `[加法・再帰] add(S(S(0)), S(S(0))) → S(add(S(S(0)), S(0)))` |

したがってログは、紙で式を展開する上から下の順ではありません。
**再帰呼び出しから結果が戻った順**です。また、各行はその段階で適用した
定義を記録しており、各行の末尾に計算済みの3や4を表示する形式ではありません。

## 実装から出力を予想する

ログの`S(S(0))`は、表現の節で読んだ`structural_str`による構造表記です。
`加法・基底`と`加法・再帰`を見れば、完全な式を暗記しなくても実装の分岐へ戻れます。
最後の`print(answer)`だけは、人が読むための`str`表記を使うので`4`になります。

`config_log(log_level=4)`の4は再帰の深さや4番目の手順ではありません。
自然数の加法と減法を表示対象に含めるための内部フィルタ値です。
計算の理解には不要なので、通常のログ本文には表示しません。

<div class="learning-prompt" data-kind="prediction" data-reveal>
  <strong>実行前に、実装を根拠に予想</strong>
  <p>
    <code>__add__</code> と <code>@log</code> の順序から、
    最初の規則名が <code>加法・基底</code> と <code>加法・再帰</code> の
    どちらになるかを決め、その理由を一文で書いてください。
  </p>
</div>

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

<details class="self-check" data-reveal>
  <summary>4行を実装へ戻して確認する</summary>
  <ol>
    <li>1行目の <code>加法・基底</code> は、<code>if predecessor is None</code> の基底ケースです。</li>
    <li>2行目の <code>加法・再帰</code> は、右辺が <code>S(0)</code> だった呼び出しです。</li>
    <li>3行目の <code>加法・再帰</code> は、右辺が <code>S(S(0))</code> だった最初の呼び出しです。</li>
    <li>最後の4は、すべての <code>successor</code> が結果へ反映されたあとに <code>print</code> が表示します。</li>
  </ol>
  <p>
    つまり、このログは単独で読む説明文ではなく、
    <code>__add__</code> のどの分岐を通ったか検査する実装トレースです。
  </p>
</details>

<span class="lesson-layer" data-layer="test">テストで確かめる</span>

## テストは、定義との対応を機械的に確かめる

ログは理解を助けますが、それだけで実装の正しさを証明するものではありません。
このライブラリのテストは、まず小さな複数の値について二つの公理に対応する
実装上の性質を確認します。
準備章で確認したとおり、ここでの `self` は数ではなくテストケースです。

```python
self.assertNotEqual(N_ZERO, successor(n))
self.assertEqual(successor(n) == successor(m), n == m)
```

続いて、加法の二つの再帰式を直接確認します。

```python
self.assertEqual(n + natural_number(0), n)
self.assertEqual(n + successor(m), successor(n + m))
```

テスト名も`test_add_axioms`ではなく`test_add_recursive_equations`とし、
この教材で採用した「公理」と「演算の再帰的定義」の区別をコード上でも保ちます。
ただし、どちらも有限個の入力に対するテストであり、一般の場合の数学的証明ではありません。

公理・表現・定義、実装、ログ、テストにはそれぞれ違う役割があります。

| 層 | 役割 |
| --- | --- |
| 公理 | 0と後者について出発点となる性質を定める |
| 表現 | `None`と`pre`の鎖で0と後者を構築する |
| 再帰的定義 | その構造上で加法や乗法を一意に決める |
| 実装 | その規則をPythonで実行可能にする |
| ログ | 実行時にどの規則を通ったか観察する |
| テスト | 実装結果が規則を満たす具体例を継続的に検査する |

<span class="lesson-layer" data-layer="boundary">この実装で重視すること</span>

## 掛け算でも同じ対応を探す

掛け算は次の再帰的定義です。

<div class="peano-equation" data-reveal>
n × 0 = 0<br>
n × S(m) = n + (n × m)
</div>

実装の`NaturalNumber.__mul__`も、`predecessor is None`なら0を返し、
それ以外なら`self + self * predecessor`を返します。加法で学んだ
「定義 → 分岐 → 再帰 → 戻り時のログ」という読み方を、そのまま再利用できます。

```python
@log(log_level=5)
def __mul__(self, other: object) -> tuple[NaturalNumber, LogMessage]:
    if not isinstance(other, NaturalNumber):
        return (
            cast(NaturalNumber, NotImplemented),
            lambda: f"{self!r} * {other!r} = NotImplemented",
        )
    predecessor = other.pre
    if predecessor is None:
        return (
            N_ZERO,
            lambda: f"[乗法・基底] mul({self.structural_str()}, 0) -> 0",
        )
    return (
        self + self * predecessor,
        lambda: (
            f"[乗法・再帰] mul({self.structural_str()}, "
            f"{other.structural_str()}) -> "
            f"add({self.structural_str()}, "
            f"mul({self.structural_str()}, {predecessor.structural_str()}))"
        ),
    )
```

<div class="concept-note" data-reveal>
  <strong>このライブラリが優先するもの</strong>
  <p>
    Python標準の整数より遅くても、数学上の構造、演算の定義、
    実装の分岐が対応して見えることを優先しています。
    そのため2や3のような小さな値で、コードとログの妥当性を調べます。
  </p>
</div>

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

## 次へ

自然数の章で身につけた読み方を、次章から繰り返します。
数学上の構成、保存するデータ、演算メソッド、ログの順に整数を調べます。

[整数の表現と実装へ進む →](integers.md)
