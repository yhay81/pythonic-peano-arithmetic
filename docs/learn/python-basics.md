<span class="lesson-number">第0章 · Pythonの仕組み</span>

# 演算子とデコレータの裏側を読む

<p class="lesson-lead">
  この教材では、基本的なPython構文は知っているものとします。
  ここで準備するのは構文ではなく、ライブラリがPythonの記号へ
  独自の意味を与える仕組みです。
</p>

<div class="lesson-context" data-reveal>
  <div>
    <strong>ここまでに必要なもの</strong>
    <p>関数、クラス、属性、条件分岐、ループ、コレクション、例外、型注釈を読めること。</p>
  </div>
  <div>
    <strong>この章で学ぶこと</strong>
    <p>特殊メソッド、デコレータ、<code>dataclass</code>、<code>property</code>がコードを組み替える仕組みです。</p>
  </div>
</div>

<div class="lesson-goals" data-reveal>
  <strong>この章を終えると</strong>
  <ul>
    <li><code>a + b</code> から、型が実装した特殊メソッドを探せる</li>
    <li>デコレータ適用前の関数と、適用後の公開関数を区別できる</li>
    <li><code>dataclass</code> が生成する処理と、手書きする処理を区別できる</li>
    <li>テストコードの <code>self</code> と演算メソッドの <code>self</code> を区別できる</li>
  </ul>
</div>

<div class="implementation-bridge" data-reveal aria-label="Pythonの構文・データモデル・ライブラリ実装">
  <div>
    <strong>表面の構文</strong>
    <p><code>a + b</code> や <code>obj.width</code> を利用者が書きます。</p>
  </div>
  <div>
    <strong>Pythonの規約</strong>
    <p>特殊メソッドや<code>property</code>へ処理が委譲されます。</p>
  </div>
  <div>
    <strong>このライブラリ</strong>
    <p>委譲先へ、数の定義・検査・ログを実装します。</p>
  </div>
</div>

## 基本構文は前提、実行環境はブラウザ

各実験のコード欄は編集でき、実行すると結果が「出力」欄へ表示されます。
最初の実行だけはPythonとライブラリの読み込みに数秒かかることがあります。
「環境をリセット」は、このページで作った名前を消して最初からやり直す操作です。

以後、代入、関数定義、クラス定義、`if`、`while`、内包表記、添字、
タプルの展開、例外、型注釈そのものは説明しません。
一方、次の節で扱うPythonのデータモデルとメタプログラミングは、
このライブラリの数学的な意味を決めるため、教材の本題として説明します。

## `+` は型へ処理を依頼する

<div class="meta-note" data-meta="operator-protocol" data-reveal>
  <strong>Pythonのデータモデル · 特殊メソッド</strong>
  <p>
    <code>a + b</code> は、組み込みの足し算だけを意味しません。
    Pythonは <code>a</code> の型が持つ <code>__add__</code> へ処理を委譲します。
    そのため、クラスの作者が <code>+</code> の意味を定義できます。
  </p>
</div>

この教材のコードを追うときは、まず次の対応で実装の入口を探します。

| 利用者が書く形 | 最初に探す実装 | この教材で決める意味 |
| --- | --- | --- |
| `a + b` | `a.__add__(b)` | 足し算 |
| `a * b` | `a.__mul__(b)` | 掛け算 |
| `a == b` | `a.__eq__(b)` | 数学的に同じ値か |
| `a < b` | `a.__lt__(b)` | 大小関係 |
| `str(a)` | `a.__str__()` | 学習者向けの表示 |
| `repr(a)` | `a.__repr__()` | 内部表現を示す表示 |
| `int(a)` | `a.__int__()` | 組み込み整数への変換 |

厳密な演算子探索には、右側の型による反射演算や継承関係も関わります。
まずはこのライブラリ内の同じ型どうしの演算を読み、必要になった整数章で
異なる型を受け入れる処理へ進みます。

<div class="source-reference"
     data-source-reference="peano/utils.py"
     data-test-reference="tests/test_utils.py">
  <strong>この章で参照する実ファイル</strong>
  <p>
    デコレータ本体:
    <a href="/assets/source/peano/utils.py"><code>peano/utils.py</code></a>
    の <code>log</code>。
    演算メソッドの例:
    <a href="/assets/source/peano/natural_number.py"><code>peano/natural_number.py</code></a>
    の <code>NaturalNumber.__add__</code>。
  </p>
  <p>
    メタデータの検査:
    <a href="/assets/source/tests/test_utils.py"><code>tests/test_utils.py</code></a>。
    全章の索引は<a href="/reference/implementation/">実装リファレンス</a>にあります。
  </p>
</div>

<div class="learning-prompt" data-kind="prediction" data-reveal>
  <strong>実行前に予想</strong>
  <p>
    <code>two + one</code> と <code>two.__add__(one)</code> は、
    上の演算子対応だけから考えると、同じ処理へ到達するでしょうか。
    内部用のタプルを公開しない理由は、実行後に次節の実装で確認します。
  </p>
</div>

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

どちらも公開された同じ `__add__` を通るため、結果は `3` と `True` です。
「内部用のタプルを返さない」理由は、次のデコレータにあります。

## デコレータは、関数を受け取って公開関数を作る

<div class="meta-note" data-meta="decorator" data-reveal>
  <strong>メタプログラミング · 関数を別の関数で包む</strong>
  <p>
    Pythonでは関数も値です。デコレータは関数を受け取り、
    元の関数を呼ぶ別の関数を返します。クラスの外から見える振る舞いを、
    本体を書き換えずに追加・変換できます。
  </p>
</div>

引数のないデコレータなら、次の二つは同じ意味です。

```python
@decorator
def operation(value):
    # 関数本体
    ...
```

```python
def operation(value):
    # 関数本体
    ...


operation = decorator(operation)
```

このライブラリの `@log(log_level=4)` は、先にログレベルを受け取り、
その結果として得たデコレータでメソッドを包みます。

```python
@log(log_level=4)
def __add__(self, other):
    # 演算本体
    ...
```

概念上は、次の再代入です。

```python
original_add = __add__
__add__ = log(log_level=4)(original_add)
```

元の `__add__` は、計算結果と「説明文を必要なときに作る関数」のタプルを返します。
公開された `__add__` は、ラッパー `inner` です。
次は `peano/utils.py` の `log` から、実行に関わる部分をそのまま抜粋したものです。

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

`...` の箇所だけは、次の小節で説明するメタデータの更新を省略しています。
完全な実装は上の `peano/utils.py` から参照できます。
したがって利用者が `two + one` と書いたときに受け取るのは計算結果だけです。
説明文は戻り値には混ざらず、設定されたログへ送られます。ログが無効なら
`message()` を呼ばないため、表示のためだけの文字列も作りません。
自然数の章では、この変換と再帰呼び出しを組み合わせてログ順を予想します。

### ラッパーが名前や型情報を壊さないための処理

実際の `log` は `functools.wraps` を使い、`__name__` や `__wrapped__` を保存します。
さらに、元の内部実装が `tuple[Result, LogMessage]` を返すという型注釈から
公開結果 `Result` を取り出し、`__annotations__` と `__signature__` を更新します。

これは単なる表示機能ではありません。「内部では説明文を遅延生成できるが、
公開APIは数だけ返す」
という二層の契約を、実行時のラッパーと、プログラムから関数情報を調べる
**イントロスペクション**用メタデータの両方へ反映するメタプログラミングです。

## `dataclass` はクラス定義からコードを生成する

<div class="meta-note" data-meta="dataclass" data-reveal>
  <strong>メタプログラミング · 宣言からメソッドを生成する</strong>
  <p>
    <code>@dataclass</code> は型注釈付きの属性を読み、
    主に <code>__init__</code> などを生成します。この教材では、
    数の保存方法を短く宣言しつつ、数学的な等しさや表示は手書きします。
  </p>
</div>

たとえば整数クラスの先頭は次の形です。

```python
@total_ordering
@dataclass(frozen=True, slots=True, eq=False, repr=False)
class Integer:
    a: NaturalNumber
    b: NaturalNumber
```

| 指定 | 生成または制限されるもの | このライブラリでの理由 |
| --- | --- | --- |
| 型注釈付き属性 | `__init__(a, b)` | 何を保存する型かを宣言する |
| `frozen=True` | 作成後の属性変更を拒否 | 数の内部表現を途中で変えない |
| `slots=True` | 属性名を固定 | 宣言していない状態を持たせない |
| `eq=False` | dataclass版`__eq__`を生成しない | 属性の一致ではない数学的な等しさを書く |
| `repr=False` | dataclass版`__repr__`を生成しない | 数学的構成が見える表示を書く |
| `init=False` | `__init__`を生成しない | 多項式で正規化する独自コンストラクタを書く |

生成された `__init__` は、属性を設定したあと `__post_init__` を自動で呼びます。
有理数はそこで「分母が0ではない」という、作成後も常に守る条件を検査します。
このような条件を、この教材では**不変条件**と呼びます。

`@total_ordering` もコード生成です。クラスが核となる等値・順序比較を実装すると、
残りの `>`, `<=`, `>=` を補います。各数体系では、生成される便利さより先に、
核として手書きされた比較が数学のどの定義に対応するかを読みます。

## `property` はメソッド呼び出しを属性アクセスに見せる

次は `peano/polynomial.py` にある、実ファイルからの短い抜粋です。

```python
@property
def coefficients(self) -> tuple[Rational, ...]:
    return self._coefficients
```

`@property` もデコレータです。利用者は `polynomial.coefficients()` ではなく
`polynomial.coefficients` と書きますが、取得時には上の関数が実行されます。
最終章では、端点から毎回計算する `interval.width` と `interval.midpoint` を
実コードと一緒に読みます。

## テストコードの読み方を揃える

<div class="meta-note" data-meta="test-api" data-reveal>
  <strong>同じ <code>self</code> でも、指す値は文脈で変わる</strong>
  <p>
    演算メソッドの <code>self</code> は左辺の数です。
    <code>unittest.TestCase</code> のテストメソッドでは、
    <code>assertEqual</code> などの検査メソッドを提供するテストケース自身です。
  </p>
</div>

| テストコード | 確かめること |
| --- | --- |
| `self.assertEqual(actual, expected)` | 二つが等しい |
| `self.assertTrue(condition)` | 条件が真になる |
| `self.assertLess(left, right)` | 左が右より小さい |
| `with self.assertRaises(Error):` | 内側の処理が指定した例外を出す |

テストが通ることは、調べた入力について実装が期待どおりだった証拠です。
すべての数について成り立つ数学的証明とは区別します。

## 各章で答える六つの質問

1. どの数学的対象と規則を使うのか
2. その対象をどの属性と不変条件で保存するのか
3. どの特殊メソッドや生成された処理が規則を実行するのか
4. デコレータを含む実装から、どのログを予想できるか
5. テストはどの性質を、どの入力で調べるのか
6. 数学の定理、実装上の選択、未実装の範囲はどこか

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

## 次へ

これで、`+` から `__add__` を探し、デコレータ適用前後の戻り値を分け、
`dataclass` が生成した処理と手書きの処理を見分けられます。
次章では、この読み方だけを使って0から自然数を構成します。

[自然数へ進む →](natural-numbers.md)
