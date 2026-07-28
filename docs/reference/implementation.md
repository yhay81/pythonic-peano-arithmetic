# 実装リファレンス

このページは、教材で使う `peano` の実装を探すための索引です。
教材本文には、その場の問いを考えるために必要な実装を抜粋します。
前後の処理、`import`、別の演算まで確認したいときは、ここから完全なファイルを開いてください。
下のリンクは、ブラウザで実行するwheelと同じビルド時点のソースを表示します。

## 抜粋の読み方

- 「実ファイルから抜粋」と書かれたコードは、import、docstring、空行、
  対象外のメソッドを除き、実装と同じです。表示幅のための改行だけ変えることがあります。
- `...` を含むコードは説明用の短縮です。短縮であることを本文にも明記します。
- メソッド本体だけでなく、直前の `@log` や `@dataclass` も振る舞いの一部として読みます。
- テストの抜粋は証明ではなく、どの入力でどの性質を検査するかを確認する材料です。

## 章から実ファイルを探す

| 教材 | 実装ファイル | まず探す名前 | 対応するテスト |
| --- | --- | --- | --- |
| 00 Pythonの仕組み | [`peano/utils.py`](/assets/source/peano/utils.py) | `log`, `_public_return_annotation` | [`tests/test_utils.py`](/assets/source/tests/test_utils.py) |
| 01 自然数 | [`peano/natural_number.py`](/assets/source/peano/natural_number.py) | `NaturalNumber`, `successor`, `structural_str`, `__eq__`, `__add__` | [`tests/test_natural_number.py`](/assets/source/tests/test_natural_number.py) |
| 02 整数 | [`peano/integer.py`](/assets/source/peano/integer.py) | `Integer`, `_coerce_integer`, `normalize` | [`tests/test_integer.py`](/assets/source/tests/test_integer.py) |
| 03 有理数 | [`peano/rational.py`](/assets/source/peano/rational.py) | `Rational`, `reduction`, `_coerce_rational` | [`tests/test_rational.py`](/assets/source/tests/test_rational.py) |
| 04 多項式 | [`peano/polynomial.py`](/assets/source/peano/polynomial.py) | `Polynomial`, `sturm_sequence`, `count_real_roots` | [`tests/test_polynomial.py`](/assets/source/tests/test_polynomial.py) |
| 05 代数的実根 | [`peano/algebraic_root.py`](/assets/source/peano/algebraic_root.py) | `RationalInterval`, `AlgebraicRoot`, `_bisect` | [`tests/test_algebraic_root.py`](/assets/source/tests/test_algebraic_root.py) |

型をまたぐ等値性とハッシュの契約は、
[`tests/test_numeric_tower.py`](/assets/source/tests/test_numeric_tower.py)
にまとまっています。

リポジトリ全体は
[`pythonic-peano-arithmetic`](https://github.com/yhay81/pythonic-peano-arithmetic)
から参照できます。教材内のスナップショットは「いま実行している版」、
GitHubは履歴や他ファイルをたどるための参照先です。

## 呼び出しの全体像

利用者が書く一行と、実装内の処理は次の順につながります。

```text
left + right
    ↓ Pythonが left.__add__(right) へ委譲
@log が作った inner(...)
    ↓
元の __add__(...) が (result, message_factory) を返す
    ↓
inner がログ有効時だけ message_factory() を評価して送り、result だけを返す
```

通常の教材出力は、規則名と式だけを表示します。`log_level`の数値は
表示範囲を絞る内部情報であり、計算内容ではないためです。

```text
[加法・基底] add(S(S(0)), 0) -> S(S(0))
```

ロギング実装を調査するときだけ、`fmt`で内部レベルを表示できます。

```python
config_log(
    log_level=4,
    fmt="Level %(levelno)s: %(message)s",
    locale="ja",
)
```

数の作成では、`dataclass` が生成する処理と、手書きの検査がつながります。

```text
Rational(p, q)
    ↓ dataclassが生成した __init__ が属性を設定
Rational.__post_init__()
    ↓ 型と分母0を検査
作成に成功した Rational
```

各章では、この索引を覚える必要はありません。予想問題の直前までに、
必要なコードと参照先を本文内へもう一度示します。
