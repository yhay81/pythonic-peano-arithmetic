# pythonic-peano-arithmetic

Peano 公理から自然数・整数・有理数・多項式を構成する学習用ライブラリです。  
演算子オーバーロードを通じて「式変形ログ」を出力し、定義の追体験ができます。

## 目的

- Peano 公理に基づく演算の定義を、公開コードで追いやすくする
- 演算の途中式をログとして観察できるようにする

## 特徴

- `NaturalNumber` / `Integer` / `Rational` / `Polynomial` を実装
- `peano.utils.config_log`で演算ログを出力

## 使い方

```python
from peano.utils import config_log
from peano.natural_number import natural_number

config_log(log_level=10, root=True)
natural_number(2) * natural_number(3)
```

詳細は `examples.ipynb` を参照してください。

## 制約

- 再帰ベースのため大きい数は遅く、実用的ではありません
- `Polynomial` は最小実装のため、未実装/未検証の演算があります

## 注意

- `rational(p, q)` の `q` は 0 を許容しません。
- 分母は負でも入力できますが、比較と `hash` は分母の符号を正に正規化して扱います。
- 多項式は末尾の係数 0 を省略しても同じ多項式として扱います。
- `natural_number` は 0 以上の整数のみを受け付けます。
- `Rational` の `hash` は約分後の値に基づきます。
- 演算・比較は同型同士を前提とし、異種型は例外になる場合があります。
- 各型は不変として扱い、属性は読み取り専用です。
