<span class="lesson-number">第5章 · 代数的実根</span>

# 根を「式と分離区間」の組として実装する

<p class="lesson-lead">
  <code>√2</code> を有理数一つで表すことはできません。
  代わりに、どの多項式の根か、その根だけを含む区間はどこかを保存します。
  作成時の検査と二分法の分岐を読み、ログが区間の不変条件を保つか確かめます。
</p>

<div class="lesson-context" data-reveal>
  <div>
    <strong>前章から使うもの</strong>
    <p>有理数、多項式の符号、スツルム列による根の個数、根の存在と一意性の区別。</p>
  </div>
  <div>
    <strong>この章で学ぶこと</strong>
    <p>閉区間、分離区間、不変条件、二分法の分岐、有限計算と実数の存在保証の境界。</p>
  </div>
</div>

<div class="lesson-goals" data-reveal>
  <strong>この章を終えると</strong>
  <ul>
    <li><code>AlgebraicRoot</code> が小数ではなく何を保存するか説明できる</li>
    <li><code>_bisect</code> の分岐から、次に残る半区間を予想できる</li>
    <li>区間二分ログ、テスト、実数の定理がそれぞれ保証する範囲を区別できる</li>
  </ul>
</div>

<div class="implementation-bridge" data-reveal aria-label="代数的実根の数学・表現・実装">
  <div>
    <strong>数学</strong>
    <p>多項式の根を一つだけ含む閉区間を保ち、幅を二分法で縮めます。</p>
  </div>
  <div>
    <strong>データ表現</strong>
    <p><code>AlgebraicRoot</code> が多項式と有理端点の <code>RationalInterval</code> を持ちます。</p>
  </div>
  <div>
    <strong>実装</strong>
    <p><code>__post_init__</code> が前提を検査し、<code>trace</code> が <code>_bisect</code> を繰り返します。</p>
  </div>
</div>

<div class="source-reference"
     data-source-reference="peano/algebraic_root.py"
     data-test-reference="tests/test_algebraic_root.py">
  <strong>この章で横に置く実装</strong>
  <p>
    区間・根・二分法:
    <a href="/assets/source/peano/algebraic_root.py"><code>peano/algebraic_root.py</code></a>。
    本文では二つの <code>__post_init__</code>、<code>trace</code>、
    <code>_bisect</code> を抜粋します。
  </p>
  <p>
    有効・無効な区間と二分結果の検査:
    <a href="/assets/source/tests/test_algebraic_root.py"><code>tests/test_algebraic_root.py</code></a>。
    ファイル索引は<a href="/reference/implementation/">実装リファレンス</a>にあります。
  </p>
</div>

<span class="lesson-layer" data-layer="definition">数学上の定義</span>

## 根を一つだけ含む区間を用意する

**代数的実数**とは、有理数係数を持つ0でない多項式の実数の根です。
`√2` は `x²−2` の実数の根なので代数的実数です。この章の `AlgebraicRoot` は、
代数的実数すべての演算を行う型ではなく、そのうち一つの根を
「多項式と、その根を一つだけ含む区間」で指定する教材用の表現です。

`[1,2]` は1以上2以下の数をすべて含む**閉区間**です。
角括弧は端点も含むことを表します。前章で、`x²−2` は1で負、2で正になり、
開区間 `(1,2)` に根がちょうど一つあると確認しました。

多項式の相異なる実根を一つだけ含み、端点自身は根でない区間を、
ここでは根の**分離区間**として使います。`x²−2` の正の根に対する
`[1,2]` がその例です。

区間の中点 `m=(lower+upper)/2` で多項式の符号を調べます。

- 中点が根なら、区間を一点 `[m,m]` にする
- 左端と中点の符号が違えば、左半分 `[lower,m]` を残す
- そうでなければ、右半分 `[m,upper]` を残す

連続性により、符号が変わる側には根があります。元の区間に根が一つだけなら、
残した半区間にもその一つだけが残ります。これが二分法で保つ**不変条件**です。

<span class="lesson-layer" data-layer="representation">データの表し方</span>

## 多項式と区間を、別々の型で保存する

`RationalInterval` は、二つの有理数を持ちます。

```python
@dataclass(frozen=True, slots=True)
class RationalInterval:
    lower: Rational
    upper: Rational

    def __post_init__(self) -> None:
        if not isinstance(self.lower, Rational) or not isinstance(self.upper, Rational):
            raise TypeError("interval endpoints must be Rational values")
        lower_fraction = _as_fraction(self.lower)
        upper_fraction = _as_fraction(self.upper)
        if lower_fraction > upper_fraction:
            raise ValueError("lower must be less than or equal to upper")
        object.__setattr__(self, "lower", _from_fraction(lower_fraction))
        object.__setattr__(self, "upper", _from_fraction(upper_fraction))
```

作成時に端点が有理数であること、`lower <= upper` であることを検査します。
同じ端点は許され、`[m,m]` は有理数の根をちょうど見つけた一点区間を表します。
`width` と `midpoint` は、保存した端点から計算するプロパティです。

```python
@property
def width(self) -> Rational:
    return _from_fraction(_as_fraction(self.upper) - _as_fraction(self.lower))
```

`_as_fraction` は構成した有理数を同じ値のPython `Fraction` へ移し、
`_from_fraction` は結果をこのライブラリの `Rational` へ戻します。
これは後で説明する、反復を実用的にするための境界です。

<div class="meta-note" data-meta="property" data-reveal>
  <strong>保存した属性と、取得時に計算する属性を分ける</strong>
  <p>
    保存されるのは <code>lower</code> と <code>upper</code> です。
    <code>interval.width</code> を読むと、<code>@property</code> が包んだメソッドが
    実行されます。幅を重複して保存しないため、端点と食い違う状態を作れません。
  </p>
</div>

`AlgebraicRoot` は、多項式と区間を一緒に持ちます。

```python
@dataclass(frozen=True, slots=True, eq=False)
class AlgebraicRoot:
    polynomial: Polynomial
    interval: RationalInterval
```

ここでも `frozen=True` により作成後の指定を変えられません。
`eq=False` は意図的です。同じ実数を別の多項式や区間で指定できるため、
二属性の一致から根の数学的等号を自動生成するのは不適切です。
この教材用クラスは、根どうしの一般的な等号を実装しない範囲を選んでいます。

これは `1.414...` のような小数近似を保存する型ではありません。
「多項式 `x²−2` の、区間 `[1,2]` に分離された根」という指定を保存します。

作成直後の `__post_init__` は、次を順に検査します。

1. 多項式が1次以上で、初期区間に正の幅がある
2. 両端自身は根ではなく、両端で符号が異なる
3. `count_real_roots` の結果が1である

実ファイルでは、この三段階が次のように並びます。

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

どれかを満たさなければ `ValueError` になり、不完全な
`AlgebraicRoot` は作られません。前章のスツルム列は、ここでは
コンストラクタの不変条件を支える部品として再利用されています。

<span class="lesson-layer" data-layer="implementation">Pythonでの実装</span>

## 公開された補助関数が二つの型を組み立てる

実験で使う `algebraic_root` は、短い入力から上の二種類のオブジェクトを作る
公開された補助関数です。

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

たとえば `lower=(1, 1)` なら、`rational(*lower)` は
`rational(1, 1)` と同じタプルの展開です。この補助関数は数学的な検査を省略せず、
構築した `RationalInterval` と `AlgebraicRoot` の `__post_init__` へ委譲します。
したがって、短縮記法を使っても分離区間の不変条件は同じです。

## `_bisect` の三つの経路を読む

実装の中心は、先ほどの数学的な場合分けと同じです。

<div class="meta-note" data-meta="free-function-decorator" data-reveal>
  <strong>デコレータはメソッド専用ではない</strong>
  <p>
    <code>_bisect</code> はクラスのメソッドではなくモジュール内の関数ですが、
    <code>@log(log_level=41)</code> で同じように包まれます。
    元の関数は区間と説明文を返し、モジュール内でその名前に割り当てられるラッパーは
    説明文を記録して区間だけを返します。
  </p>
</div>

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
            lambda: f"{polynomial_value!r}: 中点 {midpoint!r} は根",
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

`x²−2` と `[1,2]` では、中点は `3/2` です。

| 点 | 多項式の値 | 符号 |
| --- | ---: | --- |
| 左端 `1` | `−1` | 負 |
| 中点 `3/2` | `1/4` | 正 |
| 右端 `2` | `2` | 正 |

左端と中点の符号が異なるため、2番目の経路で `[1,3/2]` を返します。

`trace` は初期区間をリストへ入れ、指定回数だけ `_bisect` の戻り値を追加します。

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

`_` は繰り返し番号自体を使わないときの慣習的な名前です。
中点が厳密な根なら一点区間になり、それ以上狭める必要がないので `break` します。

<span class="lesson-layer" data-layer="trace">実行して確かめる</span>

## 区間二分ログで、どちらの半分を残したか確かめる

`_bisect` には `@log(log_level=41)` が付いています。ログは各回の
入力区間と戻り値を一行で記録します。

<div class="learning-prompt" data-kind="prediction" data-reveal>
  <strong>最初の二回を、実装の分岐から予想</strong>
  <p>
    上に抜粋した <code>_bisect</code> の <code>midpoint_sign</code> と
    <code>lower_sign</code> の分岐を参照します。
    最初の中点 <code>3/2</code> と、次の中点 <code>5/4</code> の符号を調べ、
    最初の二つの区間二分ログで残る区間を書いてください。
  </p>
</div>

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

実行順に注目してください。`sqrt_two.trace(4)` が4回の二分とログ記録を
すべて終えてから、下の `for` が保存済みの5区間を `print` します。
したがって、出力では二分ログが先にまとまり、そのあと区間列が並びます。

| 二分後 | 残る区間 | 幅 |
| ---: | --- | --- |
| 0回 | `[1,2]` | 1 |
| 1回 | `[1,3/2]` | `1/2` |
| 2回 | `[5/4,3/2]` | `1/4` |
| 3回 | `[11/8,3/2]` | `1/8` |
| 4回 | `[11/8,23/16]` | `1/16` |

設定値41では、多項式の `sign_at` が内部で行う計算はログに出ません。
ログの矢印だけを信用するのではなく、中点の符号と `_bisect` の分岐へ戻して
区間選択の妥当性を判断します。

<span class="lesson-layer" data-layer="test">テストで確かめる</span>

## テストは「狭くなる」と「根を失わない」を同時に調べる

3回二分すると幅は `1/8` です。テストは幅だけでなく、
新しい両端でも符号が異なることを確かめます。

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

中点が厳密な根だった場合には一点区間になることも、別の経路として検査します。

```python
approximation = root.approximate(1)
self.assertTrue(approximation.is_point)
self.assertEqual(approximation.midpoint, Q_ZERO)
```

さらに、根を含まない `[2,3]` や複数の根を含む区間は、
作成時に拒否されることをテストします。正常な反復だけでなく、
不変条件を破る入力が通らないことも型の責務です。

<span class="lesson-layer" data-layer="boundary">有限の計算で分かること</span>

## 有限回の区間と、実数としての根を区別する

4回でも100回でも、プログラムが直接返すのは有理数の端点を持つ区間です。
`√2` と厳密に等しい有理数を返してはいません。

| 根拠 | ここで保証すること |
| --- | --- |
| `_bisect` の実装 | 符号が変わる半区間を選ぶ |
| テスト | 調べた例で幅と不変条件が期待どおり保たれる |
| スツルムの定理 | 初期区間に相異なる根が一つある |
| 入れ子区間の定理・実数の完備性 | 幅が0へ近づく全区間に共通の実数が一つある |

ここで**入れ子**とは、次の区間が必ず前の区間に含まれることです。
二分のたびに幅は半分になり、0へ近づきます。実数の**完備性**は、
このような無限列が指し示す極限に「穴がない」ことを保証します。
有限回のプログラム実行が無限回を終えたという意味ではなく、
数学の定理が有限の各区間を一つの実数へ結び付けています。

`AlgebraicRoot` は、あらゆる実数を扱う完全な数値型ではありません。
根どうしの四則演算や一般の等号は提供せず、多項式・分離区間・二分法の
対応を学ぶための機能に絞っています。

また、区間の端点計算と符号判定では、前章で説明した `Fraction` への変換を使います。
そのため「自然数から構成した演算だけで任意回数を進める実装」ではありません。
構成の意味を保ちながら、反復を実用的にする明示的な境界です。

<form class="knowledge-check" data-reveal>
  <fieldset>
    <legend>確認問題 · <code>trace(4)</code> を実行して直接得られるものは何ですか。</legend>
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

## ここまでで身に付けた読み方

1. 数学上の対象と規則を言葉と式で区別する
2. その対象をライブラリがどの属性へ保存するか調べる
3. 演算子が呼ぶメソッドと、条件分岐を定義へ対応付ける
4. 実装から出力を予想し、実際のログと照らし合わせる
5. テストが検査する性質と、数学の定理が保証する範囲を分ける
6. 高速化のための選択や、この実装で扱わないことを明示する

この手順を使えば、別の演算や別の数体系も「ログが出たから正しい」で終わらず、
定義・実装・観察結果の対応として読めます。

[実験室で自分の予想を確かめる →](../playground.md)
