# pythonic-peano-arithmetic

Peano 公理から自然数・整数・有理数・多項式を構成し、有理数では
表せない代数的実根を有理区間で追いかける学習用ライブラリです。
演算子オーバーロードを通じて「式変形ログ」を出力し、定義の追体験ができます。

## 目的

- Peano 公理に基づく演算の定義を、公開コードで追いやすくする
- 演算の途中式をログとして観察できるようにする
- 有理数係数多項式から、Sturm 列と二分法で実根へ進む流れを学ぶ

## セットアップ

Python 3.10 以上と `uv` を使用します。

```bash
uv sync
uv run python -m unittest
```

## 5〜10分チュートリアル（最短ルート）

小さな値だけで「定義 → ログ → 結果」を体験する最短セットです。

### 1) 自然数: 加法の再帰

```python
from peano.utils import config_log
from peano.natural_number import natural_number

config_log(log_level=4)
natural_number(2) + natural_number(1)
```

期待ログ（抜粋）:

```text
Level 4: <N(2)> + <N(0)> = <N(2)>
Level 4: <N(2)> + S(<N(0)>) = S(<N(2)> + <N(0)>)
```

### 2) 整数: 同値類の等号

```python
from peano.integer import Integer
from peano.natural_number import natural_number

config_log(log_level=11)
Integer(natural_number(3), natural_number(1)) == Integer(
    natural_number(4), natural_number(2)
)
```

期待ログ（抜粋）:

```text
Level 11: <Z(3,1)> == <Z(4,2)> iff <N(3)> + <N(2)> == <N(1)> + <N(4)>
```

### 3) 有理数: 等号の交差積

```python
from peano.rational import rational

config_log(log_level=21)
rational(1, 2) == rational(2, 4)
```

期待ログ（抜粋）:

```text
Level 21: <Q(1/2)> == <Q(2/4)> iff <Z(1,0)> * <Z(4,0)> == <Z(2,0)> * <Z(2,0)>
```

### 4) 多項式: 係数列の和（ログは出ません）

```python
from peano.polynomial import Polynomial
from peano.rational import rational

str(Polynomial(rational(1, 1), rational(1, 1)) + Polynomial(rational(1, 1)))
```

結果例:

```text
2 + x
```

### 5) 有理数の「穴」: √2 を挟み込む

`x² - 2` は有理数の根を持ちません。そこで、根がちょうど1つある
有理区間を Sturm 列で確認し、二分法で区間を縮めます。

```python
from peano import Polynomial, algebraic_root, rational

x2_minus_2 = Polynomial(
    rational(-2, 1),
    rational(0, 1),
    rational(1, 1),
)
sqrt_two = algebraic_root(x2_minus_2, (1, 1), (2, 1))

for interval in sqrt_two.trace(5):
    print(interval)
```

```text
[1/1, 2/1]
[1/1, 3/2]
[5/4, 3/2]
[11/8, 3/2]
[11/8, 23/16]
[45/32, 23/16]
```

各区間は前の区間に含まれ、幅は `1, 1/2, ..., 1/32` と半分になります。
どの段階でも端点は有理数ですが、区間の共通部分が √2 を指定します。

## 学習ルート

1. 自然数: 0 と後者から構成されること、加法/乗法の再帰を追う
2. 整数: `(a,b)` の同値類として差を表すことを確認する
3. 有理数: `p/q` の同値類と比較時の符号の扱いを追う
4. 多項式: 係数列として扱い、和/積/除算の流れを確かめる
5. 代数的実根: Sturm 列で根を分離し、有理区間を二分して近似する

## 読む順番ガイド（見どころ）

1. `peano/natural_number.py`: 0/後者の構成、`__add__`/`__mul__` の再帰、`set_repr`/`set_str`
2. `peano/integer.py`: `(a,b)` による差の表現、`__eq__` と `normalize`
3. `peano/rational.py`: 通分/比較の符号処理、`reduction`（ユークリッドの互除法）
4. `peano/polynomial.py`: 係数列の正規化、`__floordiv__` の長除法
5. `peano/algebraic_root.py`: 分離区間と二分法による実根近似
6. `peano/utils.py`: 演算ログのデコレータ

## 特徴

- `NaturalNumber` / `Integer` / `Rational` / `Polynomial` を不変型として実装
- 下位型から上位型への自動昇格により、混合型演算を左右対称に実行
- `Polynomial` の評価、微分、GCD、Sturm 列、実根数え上げを実装
- `AlgebraicRoot` で有理分離区間を二分して実根を近似
- `peano.utils.config_log` で演算ログを出力

## 教材としての終点

`AlgebraicRoot` は名前に反して、完全な代数的実数の数値型ではありません。
多項式・分離区間・二分法をひとまとまりにした教材用オブジェクトです。

- 構築時に Sturm 列を使い、開区間内の相異なる実根が1つだと検証する
- 端点で符号が変わることを検証し、二分法の不変条件を保証する
- `approximate` と `trace` で有理区間の縮小だけを提供する
- 根同士の四則演算や数学的な等号は提供しない

これにより、実数・複素数・数値解析全般へ範囲を広げず、
「なぜ有理数の先に完備化が必要か」を観察したところで学習を終えます。

## 公理/定義 ↔ 実装対応表

- 自然数の後者: `S(n)` は `n` の後者
  実装: `successor`, `NaturalNumber(pre=...)`
- 自然数の加法: `n+0=n`, `n+S(m)=S(n+m)`
  実装: `NaturalNumber.__add__`
- 自然数の乗法: `n*0=0`, `n*S(m)=n+(n*m)`
  実装: `NaturalNumber.__mul__`
- 自然数の等号: `0=0`, `S(n)=S(m)↔n=m`
  実装: `NaturalNumber.__eq__`
- 整数の等号: `(a,b)=(c,d) ↔ a+d=b+c`
  実装: `Integer.__eq__`
- 整数の加法/乗法:
  `(a,b)+(c,d)=(a+c,b+d)`
  `(a,b)*(c,d)=(ac+bd,ad+bc)`
  実装: `Integer.__add__`, `Integer.__mul__`
- 有理数の等号: `p/q = r/s ↔ ps=qr`
  実装: `Rational.__eq__`
- 有理数の加法/乗法:
  `p/q + r/s = (ps+qr)/(qs)`
  `p/q * r/s = (pr)/(qs)`
  実装: `Rational.__add__`, `Rational.__mul__`
- 多項式:
  係数列 `(a0,a1,...)` を `a0 + a1 x + ...` とみなす
  実装: `Polynomial.__init__`, `Polynomial.__add__`,
  `Polynomial.__mul__`

## 集合としての自然数（フォン・ノイマン）

- `NaturalNumber.set_repr` はフォン・ノイマン順序数の集合表示を返す
- `NaturalNumber.set_str` は可読な文字列表示に変換する

## 正規化と埋め込み

- 正規化:
  - `Integer.normalize`: `(a,b)` を `(a-b,0)` か `(0,b-a)` の形に寄せる
  - `Rational.reduction`: 分母の符号を正に寄せた上で最大公約数で約分する
  - `Polynomial.__init__`: 末尾の 0 係数を削除する
- 埋め込み:
  - `n2z`/`n2r`/`n2p`: 自然数の拡張
  - `z2r`/`z2p`: 整数の拡張
  - `r2p`: 有理数の拡張

## 同値類と正規化の図式

- 整数の同値類: `(a,b) ~ (c,d) ↔ a+d=b+c`
  例: `(3,1) ~ (4,2)`（`3+2=1+4`）
- 有理数の同値類: `p/q ~ r/s ↔ ps=qr`
  例: `1/2 ~ 2/4`
- 正規化の向き:
  - 整数: `(a,b)` → `(a-b,0)` または `(0,b-a)`
  - 有理数: `p/q` → `p'/q'`（分母を正にし、最大公約数で約分）

## 使い方

```python
from peano.utils import config_log
from peano.natural_number import natural_number

config_log(log_level=10)
natural_number(2) * natural_number(3)
```

詳細は `examples.ipynb` を参照してください。

## ログ設計の意図

- 各演算は「結果」と「式」を返し、デコレータが式だけをログに出します。
- これにより通常の式のまま計算でき、式変形の過程だけを観察できます。
- ログを増やすための分岐はなく、演算本体は単一路線で実装しています。

## ログの読み方

- `log_level` はしきい値です。小さいほど詳細なログが出ます。
- 例: 自然数の式変形を見たい場合は `log_level=4` 前後を指定します。

### ログレベルの目安

- 1〜6: 自然数（例: 4=加法, 5=乗法）
- 11〜16: 整数（例: 11=等号, 15=乗法）
- 21〜26: 有理数（例: 21=等号, 24=加法）
- 31: 多項式の評価
- 41: 代数的実根の二分法

出力例:

```text
Level 4: <N(2)> + S(<N(0)>) = S(<N(2)> + <N(0)>)
Level 5: <N(2)> * S(<N(2)>) = <N(2)> + (<N(2)> * <N(2)>)
```

## 開発

- 環境構築は `make install`、全検証は `make check` を使用します。
- 依存関係とpre-commit hookの更新は `make update` を使用します。
- Python 3.10〜3.14をCIで検証します。
- 開発用依存は `[dependency-groups].dev` に追加し、`uv lock --upgrade` で更新します。
- PEP 621メタデータと`uv_build`で`peano`をパッケージングします。

## テストを演習として読む

- `tests/test_natural_number.py`: 0 と後者から始まる定義、加法/乗法の公理テスト
- `tests/test_integer.py`: `(a,b)` の同値関係や符号付き演算の確認
- `tests/test_rational.py`: 通分・比較・約分の性質の確認
- `tests/test_polynomial.py`: 係数列の正規化と除算の確認
- `tests/test_numeric_tower.py`: 型昇格、左右対称性、等値/hash契約の確認
- `tests/test_algebraic_root.py`: Sturm 列と実根の区間近似の確認
- `tests/test_utils.py`: ログの重複防止とhandler保全の確認

## 制約

- 再帰ベースのため大きい数は遅く、実用的ではありません
- `AlgebraicRoot` は教材用の区間近似であり、完全な実数型や四則演算は提供しません
- 根の二分回数を増やすと分子・分母が急速に成長するため、小さい回数で観察してください
- 根の反復では、符号判定と区間端点の既約化だけを Python の任意精度整数比で行います。
  これは巨大な Peano 中間値を避けるためで、返す端点は常に `Rational` です。

## 計算量/再帰深さの注意

- 再帰が深くなるため、学習用途では 10〜30 程度の小さな値を目安にしてください（100 以上は非常に遅くなります）。

## 注意

- `rational(p, q)` の `q` は 0 を許容しません。
- 分母は負でも入力できますが、比較と `hash` は分母の符号を正に正規化して扱います。
- 多項式は末尾の係数 0 を省略しても同じ多項式として扱います。
- 多項式の大小比較は「次数 → 最高次係数 → …」の辞書順です。
- `natural_number` は 0 以上の整数のみを受け付けます。
- `Rational` の `hash` は約分後の値に基づきます。
- `NaturalNumber → Integer → Rational → Polynomial` の混合演算は上位型へ昇格します。
- 等しい値は型をまたいでも同じ`hash`を持ちます。
- 各型は不変で、属性は読み取り専用です。
