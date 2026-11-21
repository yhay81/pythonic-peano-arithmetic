<span class="lesson-number">自由実験</span>

# 数字を変えて、足し算を試そう

<p class="lesson-lead">下の「実行」を押すと、Pythonが 2＋1 を計算します。「出力」のいちばん下に、答えの3が出るか見てみましょう。</p>

もう一度、今度は `right = natural_number(1)` の `1` を `3` に変えて実行します。
2から3歩進むと、最後に出る数字はいくつでしょう？

<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>自由実験 · 自然数の加法</span>
    <span class="peano-runner__status" data-role="status">未実行</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="自由実験: 自然数加法の定義・実装・ログを確かめるPythonコード" spellcheck="false">from peano import config_log, natural_number

config_log(log_level=4, max_lines=200, locale="ja")

left = natural_number(2)
right = natural_number(1)
answer = left + right

print(answer)</textarea>
  <div class="peano-runner__controls">
    <button class="peano-runner__button peano-runner__button--run" data-action="run">▶ 実行</button>
    <button class="peano-runner__button" data-action="reset">環境をリセット</button>
    <span class="peano-runner__shortcut">⌘ / Ctrl + Enter</span>
  </div>
  <div class="peano-runner__output-wrap">
    <span class="peano-runner__output-label">出力</span>
    <pre class="peano-runner__output" data-role="output" aria-live="polite">実行すると、ここに計算の途中経過と答えが出ます。</pre>
  </div>
</div>

<details class="self-check" data-reveal>
  <summary>変更前の予想を確かめる</summary>
  <p>
    右辺1は <code>S(0)</code> なので、再帰ケースが1回、その内側で
    基底ケースが1回通ります。ログは戻り時に出るため基底ケースが先、
    再帰ケースが後です。最後の3だけが <code>print(answer)</code> の出力です。
  </p>
</details>

## 途中の計算をどこまで表示するか選ぶ

`config_log(log_level=n)` の `n` は、表示する**最小レベル**です。
数字を下げると下位の数体系まで見えますが、出力は増えます。
この数値は絞り込み専用で、通常のログ本文には表示しません。
ブラウザ教材では `max_lines=200` を指定し、上限を超えたログを省略します。
これは計算規則を変える設定ではなく、読めない量の出力で画面を埋めないための制限です。

| 範囲 | 主に対応する実装 |
| ---: | --- |
| 1〜6 | 自然数 |
| 11〜16 | 整数 |
| 21〜26 | 有理数 |
| 31 | 多項式の代入 |
| 41 | 根の区間二分 |

たとえば有理数の等号を設定値21で実行すると、有理数の交差積だけが見えます。
15へ下げると整数乗法が加わり、4へ下げると自然数加法も加わります。
ログレベルを変えても計算規則や答えは変わりません。

## 章ごとの確認課題

対応する章の実行セル全体をコピーして始めてください。変更前と変更後を比べるため、
一度に変える条件は一つにします。

| 章 | 一つの変更 | 注目するPythonの仕組み | 実装から予想すること |
| --- | --- | --- | --- |
| [自然数](learn/natural-numbers.md) | 加法の右辺を1増やす | `__add__`と`@log` | 再帰ケースと戻り時ログが1回増える |
| [整数](learn/integers.md) | 両成分へ同じ自然数を足す | `eq=False`と手書き`__eq__` | 代表元は違っても交差和は等しい |
| [有理数](learn/rationals.md) | 分子・分母を同じ整数倍にする | `__post_init__`と`__hash__` | 自動約分なしでも等値・ハッシュの契約を保つ |
| [多項式](learn/polynomials.md) | 末尾へ0係数を足す | `init=False`と独自`__init__` | 正規化後の係数列は変わらない |
| [代数的実根](learn/algebraic-roots.md) | `trace` の回数を1増やす | `@property`と関数デコレータ | 幅が半分、区間二分ログが1個増える |

未知の名前だけを単独で入力すると、その名前をまだ作っていない環境では動きません。
`from ... import ...`、値の作成、実行、`print` を一つのセルへまとめると、
実験を再現しやすくなります。

## 失敗も、実装の仕様として読む

エラーが出たら、すぐ数を変えて消す前に次を確かめます。

1. エラーになった行はどこか
2. 作成時の不変条件に反していないか
3. その入力を拒否するテストがあるか

例として `rational(1,0)` は、分母0を拒否する `__post_init__` に対応して
`ZeroDivisionError` になります。これは実験の失敗ではなく、
有理数表現の条件が実装されている証拠です。

<div class="concept-note">
  <strong>大きな数より、小さな反例候補</strong>
  <p>
    このライブラリは高速な数値計算より、定義と実装の対応を見せることを優先します。
    2や3程度の値で、予想を壊しそうな境界条件を一つ選び、
    コード・ログ・テストを往復する使い方に向いています。
  </p>
</div>
