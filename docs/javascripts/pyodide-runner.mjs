const workerUrl = new URL("./pyodide-worker.mjs", import.meta.url);
const shikiVersion = "4.3.1";
const executionTimeoutMs = 5000;
const isJapanese = document.documentElement.lang.toLowerCase().startsWith("ja");
const text = (english, japanese) => (isJapanese ? japanese : english);

let syntaxHighlighterPromise;

function getSyntaxHighlighter() {
  if (!syntaxHighlighterPromise) {
    syntaxHighlighterPromise = Promise.all([
      import(`https://esm.sh/shiki@${shikiVersion}/core`),
      import(`https://esm.sh/shiki@${shikiVersion}/engine/javascript`),
      import(`https://esm.sh/@shikijs/langs@${shikiVersion}/python`),
      import(`https://esm.sh/@shikijs/themes@${shikiVersion}/github-dark`),
    ]).then(([core, engine, python, theme]) =>
      core.createHighlighterCore({
        langs: [python.default],
        themes: [theme.default],
        engine: engine.createJavaScriptRegexEngine(),
      }),
    );
  }
  return syntaxHighlighterPromise;
}

async function initSyntaxHighlight(source) {
  if (source.dataset.highlightReady === "true") {
    return;
  }
  source.dataset.highlightReady = "true";

  const editor = document.createElement("div");
  editor.className = "peano-runner__editor";

  const highlight = document.createElement("div");
  highlight.className = "peano-runner__highlight";
  highlight.setAttribute("aria-hidden", "true");

  source.before(editor);
  editor.append(highlight, source);

  const syncScroll = () => {
    const highlightedCode = highlight.firstElementChild;
    if (highlightedCode) {
      highlightedCode.scrollTop = source.scrollTop;
      highlightedCode.scrollLeft = source.scrollLeft;
    }
  };

  try {
    const highlighter = await getSyntaxHighlighter();
    let animationFrame;
    const render = () => {
      window.cancelAnimationFrame(animationFrame);
      animationFrame = window.requestAnimationFrame(() => {
        highlight.innerHTML = highlighter.codeToHtml(source.value || " ", {
          lang: "python",
          theme: "github-dark",
        });
        highlight.firstElementChild?.removeAttribute("tabindex");
        editor.dataset.highlighted = "true";
        syncScroll();
      });
    };

    source.addEventListener("input", render);
    source.addEventListener("scroll", syncScroll, { passive: true });
    render();
  } catch (error) {
    console.warn("Python syntax highlighting is unavailable.", error);
  }
}

class PeanoRuntime {
  constructor() {
    this.worker = null;
    this.readyPromise = null;
    this.readyResolve = null;
    this.readyReject = null;
    this.pending = new Map();
    this.nextId = 1;
  }

  ensureReady() {
    if (this.readyPromise) {
      return this.readyPromise;
    }

    this.readyPromise = new Promise((resolve, reject) => {
      this.readyResolve = resolve;
      this.readyReject = reject;
    });
    this.worker = new Worker(workerUrl, { type: "module" });

    this.worker.addEventListener("message", (event) => {
      const message = event.data;
      if (message.type === "ready") {
        this.readyResolve();
        return;
      }
      if (message.type === "fatal") {
        const error = new Error(message.error);
        this.readyReject(error);
        this.reset(error);
        return;
      }
      if (message.type === "result" || message.type === "stale") {
        const request = this.pending.get(message.id);
        if (request) {
          window.clearTimeout(request.timeoutId);
          this.pending.delete(message.id);
          request.resolve(message);
        }
      }
    });

    this.worker.addEventListener("error", (event) => {
      const error = new Error(
        event.message ||
          text(
            "Could not start the Python runtime.",
            "Python実行環境を開始できませんでした",
          ),
      );
      this.readyReject?.(error);
      this.reset(error);
    });

    return this.readyPromise;
  }

  async run(code, canRefresh = true) {
    await this.ensureReady();
    const id = this.nextId++;
    const result = await new Promise((resolve, reject) => {
      const timeoutId = window.setTimeout(() => {
        if (this.pending.has(id)) {
          this.reset(
            new Error(
              text(
                "The calculation exceeded five seconds. Use smaller inputs and try again.",
                "計算が5秒を超えたため停止しました。入力を小さくして再実行してください。",
              ),
            ),
          );
        }
      }, executionTimeoutMs);
      this.pending.set(id, { resolve, reject, timeoutId });
      this.worker.postMessage({ type: "run", id, code });
    });
    if (result.type !== "stale") {
      return result;
    }
    this.reset();
    if (!canRefresh) {
      throw new Error(
        text(
          "Could not refresh the course library. Reload the page and try again.",
          "教材ライブラリを更新できませんでした。ページを再読み込みしてください。",
        ),
      );
    }
    return this.run(code, false);
  }

  reset(
    error = new Error(
      text("The runtime was reset.", "実行環境がリセットされました"),
    ),
  ) {
    this.worker?.terminate();
    for (const request of this.pending.values()) {
      window.clearTimeout(request.timeoutId);
      request.reject(error);
    }
    this.pending.clear();
    this.worker = null;
    this.readyPromise = null;
    this.readyResolve = null;
    this.readyReject = null;
  }
}

const runtime = new PeanoRuntime();
const observedSearchRoots = new WeakSet();

function setRunnerState(runner, state, label) {
  runner.dataset.state = state;
  const status = runner.querySelector("[data-role='status']");
  const runButton = runner.querySelector("[data-action='run']");
  if (status) {
    status.textContent = label;
  }
  if (runButton) {
    runButton.disabled = state === "loading" || state === "running";
  }
}

function formatResult(result) {
  const sections = [];
  if (result.stderr) {
    sections.push(result.stderr);
  }
  if (result.stdout) {
    sections.push(result.stdout);
  }
  if (result.error) {
    sections.push(result.error);
  }
  return (
    sections.join("\n").trim() ||
    text(
      "Execution finished without output.",
      "実行は完了しました（出力はありません）",
    )
  );
}

function initRunner(runner) {
  if (runner.dataset.peanoReady === "true") {
    return;
  }
  runner.dataset.peanoReady = "true";

  const source = runner.querySelector("[data-role='source']");
  const output = runner.querySelector("[data-role='output']");
  const runButton = runner.querySelector("[data-action='run']");
  const resetButton = runner.querySelector("[data-action='reset']");
  const title = runner.querySelector(".peano-runner__header > span:first-child")?.textContent?.trim();
  const shortcut = runner.querySelector(".peano-runner__shortcut");

  if (!source || !output || !runButton) {
    return;
  }

  initSyntaxHighlight(source);

  if (!source.hasAttribute("aria-label")) {
    source.setAttribute(
      "aria-label",
      isJapanese
        ? `${title || "実験"}のPythonコード`
        : `Python code for ${title || "experiment"}`,
    );
  }
  if (!output.hasAttribute("aria-label")) {
    output.setAttribute(
      "aria-label",
      isJapanese
        ? `${title || "実験"}の実行結果`
        : `Output from ${title || "experiment"}`,
    );
  }
  output.tabIndex = 0;
  if (shortcut) {
    shortcut.textContent = text(
      "Run with ⌘ / Ctrl + Enter · Tab to continue",
      "⌘ / Ctrl + Enterで実行 · Tabで次へ",
    );
  }

  const run = async () => {
    setRunnerState(
      runner,
      "loading",
      text("Preparing Python…", "Pythonを準備中…"),
    );
    output.textContent = text(
      "The first run takes a moment while the Python runtime loads.",
      "初回は実行環境の読み込みに少し時間がかかります。",
    );

    try {
      await runtime.ensureReady();
      setRunnerState(runner, "running", text("Running…", "実行中…"));
      const result = await runtime.run(source.value);
      output.textContent = formatResult(result);
      setRunnerState(
        runner,
        result.error ? "error" : "success",
        result.error ? text("Error", "エラー") : text("Complete", "実行完了"),
      );
      output.scrollTop = 0;
    } catch (error) {
      output.textContent = error instanceof Error ? error.message : String(error);
      setRunnerState(
        runner,
        "error",
        text("Could not run the code", "実行できませんでした"),
      );
    }
  };

  runButton.addEventListener("click", run);
  resetButton?.addEventListener("click", () => {
    runtime.reset();
    output.textContent = text(
      "The runtime was reset. Python will reload on the next run.",
      "環境をリセットしました。次の実行時にPythonを再読み込みします。",
    );
    setRunnerState(runner, "idle", text("Not run", "未実行"));
  });

  source.addEventListener("keydown", (event) => {
    if (event.key === "Tab" && !event.shiftKey) {
      const nextControl = runButton.disabled ? resetButton : runButton;
      if (nextControl && !nextControl.disabled) {
        event.preventDefault();
        nextControl.focus();
        return;
      }
    }
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      event.preventDefault();
      run();
    }
  });
}

function initKnowledgeCheck(check) {
  if (check.dataset.peanoReady === "true") {
    return;
  }
  check.dataset.peanoReady = "true";

  const choices = [...check.querySelectorAll("input[type='radio']")];
  const feedback = check.querySelector("[data-role='feedback']");
  if (!choices.length || !feedback) {
    return;
  }

  check.addEventListener("submit", (event) => {
    event.preventDefault();
    const selected = choices.find((choice) => choice.checked);
    if (!selected) {
      check.dataset.state = "unanswered";
      feedback.textContent = text(
        "Choose one answer.",
        "選択肢を一つ選んでください。",
      );
      choices[0].focus();
      return;
    }

    const explanation = selected.dataset.feedback || "";
    const correct = selected.hasAttribute("data-correct");
    check.dataset.state = correct ? "correct" : "incorrect";
    feedback.textContent = correct
      ? text(`Correct. ${explanation}`, `正解です。${explanation}`)
      : text(
          `Not quite. Try again. ${explanation}`,
          `もう一度考えてみましょう。${explanation}`,
        );
  });
}

function initReveals(root) {
  const elements = root.querySelectorAll?.("[data-reveal]:not([data-reveal-ready])") ?? [];
  const observer = new IntersectionObserver(
    (entries, instance) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.dataset.visible = "true";
          instance.unobserve(entry.target);
        }
      }
    },
    { threshold: 0.14 },
  );

  for (const element of elements) {
    element.dataset.revealReady = "true";
    observer.observe(element);
  }
}

function initShellAccessibility(root = document) {
  document
    .querySelector(".md-nav--primary")
    ?.setAttribute(
      "aria-label",
      text("Course navigation", "教材ナビゲーション"),
    );
  document
    .querySelector(".md-path")
    ?.setAttribute("aria-label", text("Breadcrumbs", "パンくずリスト"));

  const progress = document.querySelector(".md-progress");
  if (progress) {
    progress.removeAttribute("role");
    progress.setAttribute("aria-hidden", "true");
  }

  document.querySelector(".md-overlay")?.setAttribute("aria-hidden", "true");

  for (const [index, navigation] of [
    ...document.querySelectorAll(".md-code__nav"),
  ].entries()) {
    navigation.setAttribute(
      "aria-label",
      text(
        `Actions for code block ${index + 1}`,
        `コードブロック${index + 1}の操作`,
      ),
    );
  }

  for (const lineAnchor of root.querySelectorAll?.('a[id^="__codelineno-"]') ?? []) {
    const line = lineAnchor.id.split("-").at(-1);
    lineAnchor.setAttribute(
      "aria-label",
      text(`Code line ${line}`, `コード ${line}行目`),
    );
  }

  const candidates = [
    root,
    ...(root.querySelectorAll?.("*") ?? []),
  ];
  for (const candidate of candidates) {
    const shadow = candidate.shadowRoot;
    if (shadow && !observedSearchRoots.has(shadow)) {
      observedSearchRoots.add(shadow);
      new MutationObserver(() => initShellAccessibility(candidate)).observe(
        shadow,
        { childList: true, subtree: true },
      );
    }

    const searchInput = shadow?.querySelector('input[role="combobox"]');
    if (!shadow || !searchInput) {
      continue;
    }

    candidate.setAttribute("role", "search");
    candidate.setAttribute(
      "aria-label",
      text("Search this site", "サイト内検索"),
    );

    const results = shadow.querySelector("ol");
    if (results) {
      results.id ||= "peano-search-results";
      searchInput.setAttribute("aria-controls", results.id);
    }
    searchInput.setAttribute("aria-expanded", "false");
    searchInput.setAttribute(
      "aria-label",
      text("Search this site", "サイト内検索"),
    );

    const buttons = shadow.querySelectorAll("button");
    buttons[0]?.setAttribute("aria-label", text("Search", "検索"));
    buttons[1]?.setAttribute(
      "aria-label",
      text("Open search filters", "検索フィルターを開く"),
    );

    for (const heading of shadow.querySelectorAll("h3, h4")) {
      heading.setAttribute("role", "presentation");
    }
    const filtersHeading = [...shadow.querySelectorAll("h3")].find(
      (heading) => heading.textContent?.trim() === "Filters",
    );
    const filtersRegion = filtersHeading?.parentElement?.parentElement;
    if (filtersRegion) {
      filtersRegion.tabIndex = 0;
      filtersRegion.setAttribute("role", "region");
      filtersRegion.setAttribute(
        "aria-label",
        text("Search filters", "検索フィルター"),
      );
    }
  }
}

function initPage(root = document) {
  const runners = root.querySelectorAll?.(".peano-runner") ?? [];
  for (const runner of runners) {
    initRunner(runner);
  }
  const checks = root.querySelectorAll?.(".knowledge-check") ?? [];
  for (const check of checks) {
    initKnowledgeCheck(check);
  }
  initReveals(root);
  initShellAccessibility(root);
}

initPage();

const pageObserver = new MutationObserver((records) => {
  for (const record of records) {
    for (const node of record.addedNodes) {
      if (node instanceof Element) {
        if (node.matches(".peano-runner")) {
          initRunner(node);
        }
        initPage(node);
      }
    }
  }
});

pageObserver.observe(document.body, { childList: true, subtree: true });
