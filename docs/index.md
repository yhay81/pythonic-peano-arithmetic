---
title: 数を、一歩ずつ作る。
hide:
  - toc
---

<section class="course-hero">
  <div class="course-hero__content">
    <span class="course-kicker">Pythonの仕組みから読む、数の構成</span>
    <h1>数を、一歩ずつ作る。</h1>
    <p>
      基本的なPythonを道具として、数の規則がクラス、演算子、
      デコレータへどう移されるかを読みます。
      ペアノ算術や数の構成は、知らない状態から始められます。
    </p>
    <div class="course-actions">
      <a class="course-action course-action--primary" href="learn/python-basics/">準備から始める</a>
      <a class="course-action" href="#route">道順を見る</a>
    </div>
  </div>
  <figure class="course-hero__diagram">
    <figcaption>この教材でたどる道</figcaption>
    <ol>
      <li>
        <strong>0 と「次の数」</strong>
        <span>自然数の保存方法と足し算を作る</span>
      </li>
      <li>
        <strong>二つの自然数</strong>
        <span>差が同じ組を、同じ整数として扱う</span>
      </li>
      <li>
        <strong>二つの整数</strong>
        <span>比が同じ組を、同じ有理数として扱う</span>
      </li>
      <li>
        <strong>式と範囲</strong>
        <span>有理数で書けない実数を指定する</span>
      </li>
    </ol>
  </figure>
</section>

<section class="course-intro" data-reveal>
  <p class="course-intro__lead">
    「数を構成する」とは、最初から使えるものとルールを決め、
    そこから新しい数を作ることです。
  </p>
  <div class="course-intro__body">
    <p>
      普段は <code>2</code> や <code>1/2</code> を完成した数として使います。
      この教材では、まず <code>0</code> と「次の数を作る操作」だけを用意し、
      足し算、負の数、分数へ進みます。そのたびに、数学の定義が
      どの属性・メソッド・分岐へ移されたかを実コードで確かめます。
    </p>
    <p>
      ペアノ算術は、0と「次の数」を手掛かりに自然数を考えるための枠組みです。
      この名前も内容も、最初の章で具体例から説明します。
    </p>
  </div>
</section>

## 前提にするPython、前提にしない数学

代入、関数、クラス、条件分岐、ループ、コレクション、例外、型注釈など、
基本的なPython構文は読めるものとします。一方で、次の仕組みは前提にしません。
このライブラリの設計を理解するために必要なので、最初の準備章から説明します。

- `a + b` と `__add__` を結ぶPythonのデータモデル
- 関数を別の関数で包むデコレータ
- `dataclass` が生成するメソッドと、その生成を止める指定
- `__post_init__`、`property`、`total_ordering`
- 等値比較・ハッシュ・`NotImplemented` が守る約束

インストールは不要です。入力したコードはブラウザ内で実行されます。
ペアノ算術、整数や有理数の構成、多項式による実数の指定は、最初から説明します。

## この教材での学び方

<div class="learning-cycle" data-reveal aria-label="各章の学習サイクル">
  <span><strong>1 · 数学</strong>何を対象とし、どの規則で扱うかを定める</span>
  <span><strong>2 · 表現</strong>対象をどの属性と、常に守る条件で保存するか読む</span>
  <span><strong>3 · 実装</strong>定義に対応するメソッドと分岐を読む</span>
  <span><strong>4 · 観察</strong>実装から出力を予想し、ログと照合する</span>
  <span><strong>5 · テスト</strong>どの性質を、どの入力で検査しているか読む</span>
  <span><strong>6 · 境界</strong>定理、設計上の選択、高速化、未実装を分ける</span>
</div>

各章の冒頭には「ここまでに分かったこと」と「この章で学ぶこと」があります。
その後、上の6項目を同じ順序で進みます。実行ログは最初から意味が分かる説明文ではなく、
実装を読んだあとに、予想と実際の動きを照らし合わせる材料です。テストが通ることと、
数学の一般的な証明が済むことも区別します。

各章には、その場の問いに必要な `peano` の実装を掲載します。
抜粋の前後や別メソッドまで読みたい場合は、章内のリンクまたは
[実装リファレンス](reference/implementation.md)から完全なファイルを開けます。
実装を事前に読んでいることは前提にしません。

<div class="concept-note" data-reveal>
  <strong>読み終わりの基準</strong>
  <p>
    答えを出せるだけでなく、「どの定義を、どの表現と分岐で実行し、
    このログとテストから何が言えるか」を自分の言葉で説明できたら、その章の完了です。
  </p>
</div>

## 学習ルート { #route }

<nav class="learning-path" aria-label="学習ルート" data-reveal>
  <a href="learn/python-basics/" data-step="00">
    <span><strong>Pythonの仕組み</strong>演算子、デコレータ、dataclassの読み方を知る</span>
  </a>
  <a href="learn/natural-numbers/" data-step="01">
    <span><strong>自然数</strong>0と「次」の規則を、保存と足し算へ移す</span>
  </a>
  <a href="learn/integers/" data-step="02">
    <span><strong>整数</strong>自然数の組から、負の数と等しさを作る</span>
  </a>
  <a href="learn/rationals/" data-step="03">
    <span><strong>有理数</strong>整数の組から、分数の等しさと演算を作る</span>
  </a>
  <a href="learn/polynomials/" data-step="04">
    <span><strong>多項式</strong>式をデータにし、範囲にある根の個数を調べる</span>
  </a>
  <a href="learn/algebraic-roots/" data-step="05">
    <span><strong>代数的実根</strong>式と範囲で根を指定し、範囲を狭める</span>
  </a>
</nav>

## この教材の範囲

ここでは、数体系の完全な形式化よりも、数学上の構成と公開ライブラリの実装を
対応付けて読むことを重視します。証明を省略する定理は、使う前に内容と役割を明示します。

次の内容は、最後まで前提にしません。

- Pythonの開発環境やパッケージ管理
- Pythonの基本構文そのものの入門
- ペアノ公理系の形式的な証明
- 抽象代数学や解析学の履修
- このリポジトリを事前に読んだ経験

準備ができたら、まずPythonが演算をライブラリへ委譲する仕組みから始めてください。

[準備: Pythonのデータモデルとメタプログラミングへ →](learn/python-basics.md)
