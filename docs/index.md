---
title: 数はどこまで自分で作れるか
hide:
  - toc
---

<section class="course-hero">
  <div class="course-hero__content">
    <h1>数はどこまで自分で作れるか</h1>
    <p>0と「次の数」だけを使って、足し算の手順を書けるでしょうか。そこから負の数、分数へ進み、最後は小数に頼らずに √2 の位置を求めます。</p>
    <div class="course-actions">
      <a class="course-action course-action--primary" href="learn/python-basics/">第0章から読む</a>
    </div>
  </div>
  <figure class="course-hero__diagram">
    <figcaption>√2を探すのに必要なもの</figcaption>
    <ol>
      <li><strong>分数</strong><span>候補の長さを 3/2 と書ける</span></li>
      <li><strong>式</strong><span>候補を2乗して、2より大きいか調べる</span></li>
      <li><strong>区間</strong><span>答えを挟む二つの端を決める</span></li>
    </ol>
  </figure>
</section>

## 学ぶ順番 { #route }

普段使っている整数や分数を、今度は中身から作ります。前の章で作った数と計算が、次の章の材料になります。Pythonの変数、関数、条件分岐を少し読める人向けに、第0章ではクラスと演算記号のつながりから説明します。

<nav class="learning-path" aria-label="学ぶ順番">
  <a href="learn/python-basics/" data-step="00"><span><strong>Pythonの仕組み</strong>足し算の記号から、動くコードを見つける</span></a>
  <a href="learn/natural-numbers/" data-step="01"><span><strong>自然数</strong>足し算の規則を二行で決める</span></a>
  <a href="learn/integers/" data-step="02"><span><strong>整数</strong>自然数の組で負の数を表す</span></a>
  <a href="learn/rationals/" data-step="03"><span><strong>有理数</strong>分数の比較と足し算を作る</span></a>
  <a href="learn/polynomials/" data-step="04"><span><strong>多項式</strong>式の値を計算し、根を数える</span></a>
  <a href="learn/algebraic-roots/" data-step="05"><span><strong>代数的実根</strong>根を取り逃さずに範囲を半分にする</span></a>
</nav>

## コードを動かす

各章の「実行」を押すと、その場で例を試せます。まず手で結果を予想し、入力を一つ変えてみてください。章ごとの追加課題は[実験ページ](playground.md)にあります。
