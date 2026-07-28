<span class="lesson-number">第2章 · 整数</span>

# 同じ差をまとめて、整数を実装する

<p class="lesson-lead">
  自然数だけでは <code>1−2</code> の答えを表せません。
  二つの自然数を「差の代表」として保存し、見た目が違っても同じ差なら
  等しいと判定する実装を読みます。
</p>

<div class="lesson-context" data-reveal>
  <div>
    <strong>前章から使うもの</strong>
    <p>自然数の表現、自然数の加法、演算子がメソッドを呼ぶこと、戻り時に出るログ。</p>
  </div>
  <div>
    <strong>この章で学ぶこと</strong>
    <p>代表元、同値関係、演算が代表元の選び方に依存しないこと、ログの表示範囲。</p>
  </div>
</div>

<div class="lesson-goals" data-reveal>
  <strong>この章を終えると</strong>
  <ul>
    <li><code>Integer(a, b)</code> が何を保存し、どの整数を表すか説明できる</li>
    <li>整数の等号を、数学の定義・<code>__eq__</code>・実行ログへ対応付けられる</li>
    <li>正規化しない設計と、値が等しいことを区別できる</li>
  </ul>
</div>

<div class="implementation-bridge" data-reveal aria-label="整数の数学・表現・実装">
  <div>
    <strong>数学</strong>
    <p>組 <code>(a,b)</code> を差 <code>a−b</code> と読み、同じ差を表す組をまとめます。</p>
  </div>
  <div>
    <strong>データ表現</strong>
    <p><code>Integer.a</code> と <code>Integer.b</code> に、二つの自然数をそのまま保存します。</p>
  </div>
  <div>
    <strong>実装</strong>
    <p><code>__eq__</code> が交差和、<code>__add__</code> が成分ごとの加法を実行します。</p>
  </div>
</div>

<div class="source-reference"
     data-source-reference="peano/integer.py"
     data-test-reference="tests/test_integer.py">
  <strong>この章で横に置く実装</strong>
  <p>
    完全なクラス:
    <a href="/assets/source/peano/integer.py"><code>peano/integer.py</code></a>
    の <code>Integer</code> と <code>_coerce_integer</code>。
    本文では等号・加法・正規化を省略せずに抜粋します。
  </p>
  <p>
    代表元と演算の検査:
    <a href="/assets/source/tests/test_integer.py"><code>tests/test_integer.py</code></a>。
    ファイル索引は<a href="/reference/implementation/">実装リファレンス</a>にあります。
  </p>
</div>

<span class="lesson-layer" data-layer="definition">数学上の定義</span>

## 自然数の組を「差」と読む

自然数の中では `1−2` の答えを表せません。そこで自然数を二つ並べた
`(a,b)` を用意し、「左から右を引いた差」を表すと決めます。

| 組 | 差として読む | 表す整数 |
| --- | --- | ---: |
| `(3,1)` | `3−1` | 2 |
| `(1,3)` | `1−3` | −2 |
| `(2,2)` | `2−2` | 0 |

ただし、一つの整数を表す組は一つではありません。`(3,1)`、`(4,2)`、
`(5,3)` はどれも2を表します。このような一つひとつの組を**代表元**と呼びます。

まだ整数の引き算を実装していなくても、自然数の加法だけなら使えます。
そこで二つの組が同じ整数を表す条件を、次のように定義します。

<div class="peano-equation" data-reveal>
(a,b) ∼ (c,d) ⇔ a+d = b+c
</div>

`∼` は「同じ整数を表す」という関係です。`(3,1)` と `(4,2)` なら、
`3+2=1+4` が成り立ちます。このように、違う表現を同じ値としてまとめる関係を
**同値関係**と呼びます。

<span class="lesson-layer" data-layer="representation">データの表し方</span>

## ライブラリは代表元を消さずに保存する

実装の中心は、`Integer` が持つ二つの属性です。

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

`a` と `b` は、どちらも前章の `NaturalNumber` です。生成された `__init__` のあと、
`__post_init__` が両方の型を検査します。

<div class="meta-note" data-meta="dataclass-equality" data-reveal>
  <strong>属性の一致ではなく、構成した整数の等しさを使う</strong>
  <p>
    <code>eq=False</code> が重要です。dataclassに等号を生成させると、
    二つの属性を順に比較するため、異なる代表元を同じ整数として扱えません。
    手書きの <code>__eq__</code> が同値関係を実行し、
    <code>@total_ordering</code> はその比較をもとに残りの順序演算を補います。
  </p>
</div>

Pythonに自動生成させる等号では `(3,1)` と `(4,2)` は
異なります。このライブラリは、数学で定めた同値関係を使う
`Integer.__eq__` を自分で実装します。

`Integer(natural_number(4), natural_number(2))` を作っても、内部の組は
`(2,0)` へ自動変換されません。`repr` では `<Z(4,2)>` と表示されます。
一方、`print` は差を計算して `2` と表示します。

| 観察したいもの | Pythonの表示 | `(4,2)` の場合 |
| --- | --- | --- |
| 保存された代表元 | `repr(value)` | `<Z(4,2)>` |
| 人が読む整数値 | `print(value)` | `2` |

!!! note "数学の必然ではなく、教材としての設計"
    常に `(2,0)` のような形へ直す実装も可能です。このライブラリは、
    同じ整数に複数の代表元があることを観察できるよう、入力された組を残します。

<span class="lesson-layer" data-layer="implementation">Pythonでの実装</span>

## `==` を同値関係へ接続する

Pythonで `left == right` と書くと、`left.__eq__(right)` が呼ばれます。
次は、直前のデコレータを含む `Integer.__eq__` の完全な実装です。

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

`self` が左、`converted` が右の整数です。`_coerce_integer` は、
次の実装で、比較相手が自然数なら `(n,0)` という整数へ持ち上げます。

```python
def _coerce_integer(value: object) -> Integer | None:
    if isinstance(value, NaturalNumber):
        return n2z(value)
    if isinstance(value, Integer):
        return value
    return None
```

整数にも自然数にも変換できない相手なら `None` を返し、特殊メソッドは
`NotImplemented` を返します。これは偽という判定ではなく、
「この左辺の実装では扱えない」というPythonデータモデル上の合図です。
Pythonは必要なら右辺側の反射演算を試し、それでも扱えなければ演算に応じて
`False` や `TypeError` へ進みます。

このように**型をそろえる処理**と `NotImplemented` を組み合わせることで、
`integer_value + natural_value` のような異なる型の組合せを、
各演算本体へ重複して書かずに扱えます。
その後の一行は数学の定義と同じ順序になっています。

| 数学の記号 | 実装 |
| --- | --- |
| `a` | `self.a` |
| `b` | `self.b` |
| `c` | `converted.a` |
| `d` | `converted.b` |
| `a+d = b+c` | `self.a + converted.b == self.b + converted.a` |

加法も同じ方針です。

<div class="peano-equation" data-reveal>
(a,b) + (c,d) = (a+c,b+d)
</div>

```python
@log(log_level=14)
def __add__(self, other: object) -> tuple[Integer, LogMessage]:
    converted = _coerce_integer(other)
    if converted is None:
        return (
            cast(Integer, NotImplemented),
            lambda: f"{self!r} + {other!r} = NotImplemented",
        )
    result = Integer(self.a + converted.a, self.b + converted.b)
    return (
        result,
        lambda: (
            f"{self!r} + {converted!r} = "
            f"({self.a!r} + {converted.a!r}, "
            f"{self.b!r} + {converted.b!r})"
        ),
    )
```

たとえば `(3,1)+(1,2)=(4,3)` です。代表する値で読むと
`2+(−1)=1` になります。

<span class="lesson-layer" data-layer="trace">実行して確かめる</span>

## 整数の等号ログを、実装へ戻して読む

`Integer.__eq__` には `@log(log_level=11)` が付いています。
次のコードは、整数の等号だけが見える最小の設定です。

<div class="learning-prompt" data-kind="prediction" data-reveal>
  <strong>実行前に、定義と実装から予想</strong>
  <p>
    上に抜粋した <code>Integer.__eq__</code> の <code>result</code> と
    ログ文字列を参照し、ログに現れる二つの自然数の和を書いてください。
    最後の値が
    <code>True</code> になる理由を一文で説明してください。
  </p>
</div>

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

<details class="self-check" data-reveal>
  <summary>ログを4つの部分へ分ける</summary>
  <ol>
    <li><code>&lt;Z(3,1)&gt; == &lt;Z(4,2)&gt;</code> は、比較した代表元です。</li>
    <li><code>⇔</code> は、左右が同値であることを表します。</li>
    <li><code>&lt;N(3)&gt;+&lt;N(2)&gt;</code> と <code>&lt;N(1)&gt;+&lt;N(4)&gt;</code> は、実装が作る交差和です。</li>
    <li>最後の <code>True</code> はログではなく、<code>print</code> が表示した判定結果です。</li>
  </ol>
</details>

`log_level=11` の11は、11番目の処理や再帰の深さではありません。
このライブラリは自然数を1〜6、整数を11〜16、有理数を21〜26という範囲に分けています。
設定値は**表示する最小レベル**なので、11では内部の自然数加法ログを隠します。
この内部値は通常のログ本文には表示されません。

`config_log(log_level=4)` に変えてもう一度実行すると、二つの交差和を作る
自然数加法のログも現れ、最後に整数の等号ログが出ます。これは証明の詳細度を
変えているのではなく、同じ実行をどの層まで観察するか変えています。

<span class="lesson-layer" data-layer="test">テストで確かめる</span>

## 値を変えながら、同じ性質を確かめる

この実験は `(3,1)` と `(4,2)` の一例です。実際のテストは、整数 `i` と
余分に足す自然数 `j` を範囲内で変え、`(i+j,j)` が同じ整数になることを調べます。

```python
for i in range(-10, 10):
    for j in range(abs(i), 10):
        self.assertEqual(
            integer(i),
            Integer(natural_number(i + j), natural_number(j)),
        )
```

加法についても、小さなすべての組合せでライブラリの結果と
Python整数の `i+j` を照合します。

```python
self.assertEqual(integer(i) + integer(j), integer(i + j))
```

ログは「今回どの規則を通ったか」を見せ、テストは「多数の入力でも期待する性質が
壊れていないか」を繰り返し調べます。どちらも一般の場合の数学的証明そのものではありません。

<span class="lesson-layer" data-layer="boundary">代表元を使うときの注意</span>

## 代表元と、表される値を混同しない

代表元を使った演算は、別の代表元を選んでも同じ整数を表さなければなりません。
この性質を「**代表元の選び方によらず定まる**」といいます。
テストは具体例を確認しますが、一般の場合には同値関係の定義から証明する必要があります。

`normalize()` は `(4,2)` を `(2,0)` のような見やすい代表元へ変えます。
元のオブジェクトは不変なので、書き換えるのではなく新しい `Integer` を返します。
正規化前後で `repr` は変わっても、`==` の結果は変わりません。

```python
def normalize(self) -> Integer:
    if self.a >= self.b:
        return Integer(self.a - self.b, N_ZERO)
    return Integer(N_ZERO, self.b - self.a)
```

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

## 次へ

整数で `1−2` を表せるようになりました。しかし `1÷2` はまだ整数ではありません。
次章では、整数の組の間に同値関係を定めて有理数を構成します。

[有理数へ進む →](rationals.md)
