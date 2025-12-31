# pythonic-peano-arithmetic

Peano 公理から自然数・整数・有理数・多項式を構成する学習用ライブラリです。
演算子オーバーロードを通じて「式変形ログ」を出力し、定義の追体験ができます。

## 目的

- Peano 公理に基づく演算の定義を、公開コードで追いやすくする
- 演算の途中式をログとして観察できるようにする

## 特徴

- `NaturalNumber` / `Integer` / `Rational` / `Polynomial` を実装
- `peano.utils.config_log`で演算ログを出力

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

## 使い方

```python
from peano.utils import config_log
from peano.natural_number import natural_number

config_log(log_level=10, root=True)
natural_number(2) * natural_number(3)
```

詳細は `examples.ipynb` を参照してください。

## ログの読み方

- `log_level` はしきい値です。小さいほど詳細なログが出ます。
- 例: 自然数の式変形を見たい場合は `log_level=4` 前後を指定します。

出力例:

```text
Level 4: <N(2)> + <N(1)> = NaturalNumber(pre=<N(2)> + <N(0)>)
Level 5: <N(2)> * <N(3)> = <N(2)> + <N(2)> * <N(3)>.pre =
  <N(2)> + <N(2)> * <N(2)>
```

## 開発

- 依存関係の更新は `make update` を使用します。
- Python は 3.10 以上を使用します。
- 開発用依存の追加は `poetry add -G dev <package>` を使用します。
- パッケージング対象は `peano` ディレクトリです。

## 制約

- 再帰ベースのため大きい数は遅く、実用的ではありません
- `Polynomial` は最小実装で、`//` は長除法の商のみを返し、`%` や評価は未実装です

## 計算量/再帰深さの注意

- 再帰が深くなるため、学習用途では 10〜30 程度の小さな値を目安にしてください（100 以上は非常に遅くなります）。

## 注意

- `rational(p, q)` の `q` は 0 を許容しません。
- 分母は負でも入力できますが、比較と `hash` は分母の符号を正に正規化して扱います。
- 多項式は末尾の係数 0 を省略しても同じ多項式として扱います。
- 多項式の大小比較は「次数 → 最高次係数 → …」の辞書順です。
- `natural_number` は 0 以上の整数のみを受け付けます。
- `Rational` の `hash` は約分後の値に基づきます。
- 演算・比較は同型同士を前提とし、異種型は例外になる場合があります。
- 各型は不変として扱い、属性は読み取り専用です。
