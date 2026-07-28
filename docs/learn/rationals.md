<span class="lesson-number">第3章 · 有理数</span>

# 整数の比から、有理数を実装する

<p class="lesson-lead">
  整数まで広げても <code>1÷2</code> の答えは作れません。
  分子と分母に整数を保存し、異なる分数表現を同じ値として扱う規則を、
  コンストラクタ・等号・約分の実装へ接続します。
</p>

<div class="lesson-context" data-reveal>
  <div>
    <strong>前章から使うもの</strong>
    <p>整数の代表元、同値関係、整数の乗法と等号、ログの表示範囲。</p>
  </div>
  <div>
    <strong>この章で学ぶこと</strong>
    <p>整数の比、分母の不変条件、交差積、約分を必要なときだけ行う設計。</p>
  </div>
</div>

<div class="lesson-goals" data-reveal>
  <strong>この章を終えると</strong>
  <ul>
    <li><code>Rational.p</code> と <code>Rational.q</code> が何を保存するか説明できる</li>
    <li>交差積の定義を <code>__eq__</code> と実行ログへ対応付けられる</li>
    <li>表現を保存すること、値が等しいこと、約分することを区別できる</li>
  </ul>
</div>

<div class="implementation-bridge" data-reveal aria-label="有理数の数学・表現・実装">
  <div>
    <strong>数学</strong>
    <p>整数の比 <code>p/q</code> を作り、交差積が等しい比を同じ値とします。</p>
  </div>
  <div>
    <strong>データ表現</strong>
    <p><code>Rational.p</code> と <code>Rational.q</code> に、分子と分母の整数を保存します。</p>
  </div>
  <div>
    <strong>実装</strong>
    <p><code>__post_init__</code> が分母を検査し、<code>__eq__</code> が交差積を比較します。</p>
  </div>
</div>

<div class="source-reference"
     data-source-reference="peano/rational.py"
     data-test-reference="tests/test_rational.py">
  <strong>この章で横に置く実装</strong>
  <p>
    完全なクラス:
    <a href="/assets/source/peano/rational.py"><code>peano/rational.py</code></a>
    の <code>Rational</code>。本文では作成時検査、等号、加法、約分、ハッシュを抜粋します。
  </p>
  <p>
    分母0・交差積・約分の検査:
    <a href="/assets/source/tests/test_rational.py"><code>tests/test_rational.py</code></a>。
    ファイル索引は<a href="/reference/implementation/">実装リファレンス</a>にあります。
  </p>
</div>

<span class="lesson-layer" data-layer="definition">数学上の定義</span>

## 分数の等しさを、整数の演算だけで定義する

`p/q` の上の `p` を**分子**、下の `q` を**分母**と呼びます。
分母は0にできません。0で割ることは有理数の演算として定義しないためです。

`1/2` と `2/4` は表記が違いますが、同じ大きさです。小数へ直さなくても、
斜めに掛けた二つの積で判定できます。

<div class="peano-equation" data-reveal>
p/q ∼ r/s ⇔ p×s = q×r
</div>

`1/2` と `2/4` なら `1×4=2×2` です。前章と同じく、`∼` は
「違う代表元だが同じ値を表す」という同値関係です。この関係で整数の比を
まとめたものを**有理数**と呼びます。

有理数の加法も、整数の演算だけで定義できます。

<div class="peano-equation" data-reveal>
p/q + r/s = (p×s + q×r)/(q×s)
</div>

たとえば `1/2+1/3=(1×3+2×1)/(2×3)=5/6` です。

<span class="lesson-layer" data-layer="representation">データの表し方</span>

## 作成時に守る条件と、あえて変えない表現

実装では、有理数一つが二つの `Integer` を持ちます。

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

`Rational` を作った直後に `__post_init__` が呼ばれ、表現が最低限の条件を
満たしているか検査します。

<div class="meta-note" data-meta="post-init" data-reveal>
  <strong>生成された <code>__init__</code> と、手書きの検査を接続する</strong>
  <p>
    <code>__post_init__</code> を利用者が直接呼ぶ必要はありません。
    dataclassが生成した <code>__init__</code> が <code>p</code> と <code>q</code> を設定し、
    直後にこの検査処理を呼びます。作成に成功したすべてのRationalで
    「両方がIntegerで、分母は0でない」という不変条件が成立します。
  </p>
</div>

ここで `self.q == Z_ZERO` は、前章で読んだ整数の同値関係を使います。
分母の代表元が `(2,2)` でも、それは整数0と等しいので拒否されます。
上の数体系が下の数体系の実装を再利用している具体例です。

`rational(1,2)` は、Python標準の整数1と2から `Integer` を二つ作り、
`Rational` へ渡す短縮関数です。このライブラリの有理数が、
Pythonに用意された別の数値型へ置き換わるわけではありません。

```python
def rational(numerator: int, denominator: int) -> Rational:
    return Rational(integer(numerator), integer(denominator))
```

このライブラリは、作成時に `2/4` を `1/2` へ自動約分しません。
また `1/−2` の分母を自動で正にしません。

| 操作 | 保存される表現 | 表す値 |
| --- | --- | --- |
| `rational(2,4)` | `2/4` | `1/2` と等しい |
| `rational(1,-2)` | `1/−2` | `−1/2` と等しい |
| `rational(2,4).reduction()` | `1/2` | 元と同じ |

<span class="lesson-layer" data-layer="implementation">Pythonでの実装</span>

## 交差積と通分を、そのままメソッドにする

Pythonの `half == two_quarters` は `Rational.__eq__` を呼びます。
次がログ文字列を含む完全な実装です。

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

| 数学 | 実装 |
| --- | --- |
| 左の交差積 `p×s` | `self.p * converted.q` |
| 右の交差積 `q×r` | `self.q * converted.p` |
| 二つの積が等しい | 整数の `__eq__` で比較 |

`Rational.__add__` も加法の定義から直接、新しい分子と分母を作ります。

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

この一行の中では整数の乗法と加法が動き、その内部ではさらに自然数の演算が動きます。
自然数 → 整数 → 有理数は、説明上の順序だけでなく実際の呼び出し関係です。

約分は別の `reduction()` に分離されています。

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

まず分子・分母を整数として正規化し、分母を正に揃え、最大公約数で割ります。
元の `Rational` は不変なので、`reduction()` は同じ値を表す新しいオブジェクトを返します。

<span class="lesson-layer" data-layer="trace">実行して確かめる</span>

## 有理数の等号ログは、内部の整数計算を要約する

`Rational.__eq__` のログレベルは21です。次の実験では、
交差積を作ったという有理数層の一行だけを表示します。

<div class="learning-prompt" data-kind="prediction" data-reveal>
  <strong>実行前に、ログの部品を予想</strong>
  <p>
    上に抜粋した <code>Rational.__eq__</code> の <code>result</code> と
    ログ文字列を参照し、<code>1/2</code> と <code>2/4</code> の
    どの整数どうしが掛けられるかを書き、
    最後の判定を予想してください。
  </p>
</div>

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

<details class="self-check" data-reveal>
  <summary><code>Q</code> と <code>Z</code> を層として読む</summary>
  <p>
    <code>&lt;Q(1/2)&gt;</code> と <code>&lt;Q(2/4)&gt;</code> は比較した有理数の代表元です。
    右側の <code>&lt;Z(1,0)&gt; * &lt;Z(4,0)&gt;</code> と
    <code>&lt;Z(2,0)&gt; * &lt;Z(2,0)&gt;</code> は交差積を作る整数演算です。
    <code>Q</code> は有理数、<code>Z</code> は整数という実装上の表示です。
  </p>
  <p>
    ログには、等しさを判定する二つの交差積が表示されます。
    それぞれの積4までは表示しないため、式を実装へ戻し、
    最後の <code>True</code> と合わせて判断します。
  </p>
</details>

`log_level=21` は21未満の整数・自然数ログを隠します。
`log_level=15` に変えると整数乗法も見え、`log_level=4` まで下げると
自然数加法も見えます。ただし出力量は急に増えます。ログレベルは、
自然数や整数の途中計算まで表示するか選ぶためのフィルターで、
通常の本文には表示されません。

有理数の加法だけを見る次の実験では、設定値24を使います。

<div class="learning-prompt" data-kind="prediction" data-reveal>
  <strong>もう一度、実装から予想</strong>
  <p>
    上に抜粋した <code>Rational.__add__</code> の <code>result</code> を参照し、
    新しい分子と分母を先に計算してください。
  </p>
</div>

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

<span class="lesson-layer" data-layer="test">テストで確かめる</span>

## テストは定義、不変条件、正規化を別々に確かめる

加法のテストは、分子・分母を小さな範囲で動かし、定義式と照合します。

```python
self.assertEqual(
    rational(i, j) + rational(k, m),
    rational(i * m + j * k, j * m),
)
```

表現が異なっても同じハッシュ値になること、約分が値を変えないことも別に検査します。

```python
self.assertEqual(hash(rational(i, j)), hash(rational(i * 2, j * 2)))
self.assertEqual(rational(16, 9).reduction(), rational(16, 9))
```

ハッシュは、辞書や集合が値をすばやく探すために使う整数です。
Pythonのデータモデルには「`a == b` なら `hash(a) == hash(b)`」という契約があります。
そのため `Rational.__hash__` は、保存された `2/4` から直接ハッシュ値を求めず、
`reduction()` で同じ値を同じ標準形へ揃えてから求めます。
数学上の等値関係を `__eq__` だけでなく、コンテナの振る舞いへも反映する実装です。

```python
def __hash__(self) -> int:
    reduced = self.reduction()
    if reduced.q == Z_ONE:
        return hash(reduced.p)
    return hash(("Rational", int(reduced.p), int(reduced.q)))
```

そして、分母0は正常な値を返すのではなく、例外になることを確かめます。

```python
with self.assertRaises(ZeroDivisionError):
    rational(1, 0)
```

「正しい入力の演算」と「不正な入力を拒否する不変条件」は、異なる責務なので
テストも分かれています。

<span class="lesson-layer" data-layer="boundary">次に必要になるもの</span>

## 有理数で表せない数が、次の実装課題になる

`x×x=2` を満たす数を `√2` と書きます。`√2` は整数どうしの比では
表せないため、この `Rational` だけでは値を構築できません。

<details class="proof-note" data-reveal>
  <summary>発展 · √2が有理数でない理由</summary>
  <p>
    √2を既約分数 <code>p/q</code> と仮定すると <code>p²=2q²</code> です。
    ここから <code>p</code> と <code>q</code> が両方とも2で割れることになり、
    既約という仮定に反します。したがって√2は有理数ではありません。
  </p>
</details>

この不足はライブラリの失敗ではなく、数体系を広げる動機です。次章では
`√2` をいきなり小数として近似せず、まず `x²−2` という多項式を保存し、
0になる場所を調べます。

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
      分母が既約でないため例外になる
    </label>
    <button type="submit">答え合わせ</button>
    <p class="knowledge-check__feedback" data-role="feedback" aria-live="polite"></p>
  </fieldset>
</form>

[多項式へ進む →](polynomials.md)
