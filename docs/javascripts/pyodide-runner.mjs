const workerUrl = new URL("./pyodide-worker.mjs", import.meta.url);
const shikiVersion = "4.3.1";
const executionTimeoutMs = 5000;
const isJapanese = document.documentElement.lang.toLowerCase().startsWith("ja");
const routeLocale =
  [
    ["zh-hant", "zh-Hant"],
    ["pt-br", "pt-BR"],
    ["zh", "zh-Hans"],
    ["es", "es"],
    ["fr", "fr"],
    ["de", "de"],
    ["ko", "ko"],
    ["ru", "ru"],
    ["ar", "ar"],
    ["hi", "hi"],
  ].find(([route]) => location.pathname.startsWith(`/${route}/`))?.[1] ??
  (isJapanese ? "ja" : "en");
const uiTranslations = {
  "zh-Hans": {
    "Could not start the Python runtime.": "无法启动 Python 运行环境。",
    "The calculation exceeded five seconds. Use smaller inputs and try again.": "计算超过五秒。请减小输入后重试。",
    "Could not refresh the course library. Reload the page and try again.": "无法更新课程库。请重新加载页面。",
    "The runtime was reset.": "运行环境已重置。",
    "Execution finished without output.": "执行完成，但没有输出。",
    "Preparing Python…": "正在准备 Python…",
    "The first run takes a moment while the Python runtime loads.": "第一次运行需要一些时间加载 Python。",
    "Running…": "运行中…",
    Error: "错误",
    Complete: "完成",
    "Could not run the code": "无法运行代码",
    "The runtime was reset. Python will reload on the next run.": "环境已重置，下次运行时会重新加载 Python。",
    "Not run": "尚未运行",
    "Choose one answer.": "请选择一个答案。",
    "Course navigation": "课程导航",
    Breadcrumbs: "面包屑导航",
    "Search this site": "搜索本站",
    Search: "搜索",
    "Open search filters": "打开搜索筛选",
    "Search filters": "搜索筛选",
  },
  "zh-Hant": {
    "Could not start the Python runtime.": "無法啟動 Python 執行環境。",
    "The calculation exceeded five seconds. Use smaller inputs and try again.": "計算超過五秒。請縮小輸入後重試。",
    "Could not refresh the course library. Reload the page and try again.": "無法更新課程函式庫。請重新載入頁面。",
    "The runtime was reset.": "執行環境已重設。",
    "Execution finished without output.": "執行完成，但沒有輸出。",
    "Preparing Python…": "正在準備 Python…",
    "The first run takes a moment while the Python runtime loads.": "第一次執行需要一些時間載入 Python。",
    "Running…": "執行中…",
    Error: "錯誤",
    Complete: "完成",
    "Could not run the code": "無法執行程式",
    "The runtime was reset. Python will reload on the next run.": "環境已重設，下次執行時會重新載入 Python。",
    "Not run": "尚未執行",
    "Choose one answer.": "請選擇一個答案。",
    "Course navigation": "課程導覽",
    Breadcrumbs: "麵包屑導覽",
    "Search this site": "搜尋本站",
    Search: "搜尋",
    "Open search filters": "開啟搜尋篩選",
    "Search filters": "搜尋篩選",
  },
  es: {
    "Could not start the Python runtime.": "No se pudo iniciar Python.",
    "The calculation exceeded five seconds. Use smaller inputs and try again.": "El cálculo superó cinco segundos. Reduce la entrada.",
    "Could not refresh the course library. Reload the page and try again.": "No se pudo actualizar la biblioteca. Recarga la página.",
    "The runtime was reset.": "El entorno se reinició.",
    "Execution finished without output.": "La ejecución terminó sin salida.",
    "Preparing Python…": "Preparando Python…",
    "The first run takes a moment while the Python runtime loads.": "La primera ejecución tarda mientras se carga Python.",
    "Running…": "Ejecutando…",
    Error: "Error",
    Complete: "Completado",
    "Could not run the code": "No se pudo ejecutar el código",
    "The runtime was reset. Python will reload on the next run.": "Entorno reiniciado. Python se cargará en la próxima ejecución.",
    "Not run": "Sin ejecutar",
    "Choose one answer.": "Elige una respuesta.",
    "Course navigation": "Navegación del curso",
    Breadcrumbs: "Ruta de navegación",
    "Search this site": "Buscar en el sitio",
    Search: "Buscar",
    "Open search filters": "Abrir filtros",
    "Search filters": "Filtros de búsqueda",
  },
  "pt-BR": {
    "Could not start the Python runtime.": "Não foi possível iniciar o Python.",
    "The calculation exceeded five seconds. Use smaller inputs and try again.": "O cálculo passou de cinco segundos. Reduza a entrada.",
    "Could not refresh the course library. Reload the page and try again.": "Não foi possível atualizar a biblioteca. Recarregue a página.",
    "The runtime was reset.": "O ambiente foi reiniciado.",
    "Execution finished without output.": "A execução terminou sem saída.",
    "Preparing Python…": "Preparando Python…",
    "The first run takes a moment while the Python runtime loads.": "A primeira execução demora enquanto o Python é carregado.",
    "Running…": "Executando…",
    Error: "Erro",
    Complete: "Concluído",
    "Could not run the code": "Não foi possível executar o código",
    "The runtime was reset. Python will reload on the next run.": "Ambiente reiniciado. O Python será carregado na próxima execução.",
    "Not run": "Não executado",
    "Choose one answer.": "Escolha uma resposta.",
    "Course navigation": "Navegação do curso",
    Breadcrumbs: "Trilha de navegação",
    "Search this site": "Pesquisar neste site",
    Search: "Pesquisar",
    "Open search filters": "Abrir filtros",
    "Search filters": "Filtros de pesquisa",
  },
  fr: {
    "Could not start the Python runtime.": "Impossible de démarrer Python.",
    "The calculation exceeded five seconds. Use smaller inputs and try again.": "Le calcul a dépassé cinq secondes. Réduisez les entrées.",
    "Could not refresh the course library. Reload the page and try again.": "Impossible d’actualiser la bibliothèque. Rechargez la page.",
    "The runtime was reset.": "L’environnement a été réinitialisé.",
    "Execution finished without output.": "Exécution terminée sans sortie.",
    "Preparing Python…": "Préparation de Python…",
    "The first run takes a moment while the Python runtime loads.": "Le premier lancement prend un moment pour charger Python.",
    "Running…": "Exécution…",
    Error: "Erreur",
    Complete: "Terminé",
    "Could not run the code": "Impossible d’exécuter le code",
    "The runtime was reset. Python will reload on the next run.": "Environnement réinitialisé. Python sera rechargé au prochain lancement.",
    "Not run": "Non exécuté",
    "Choose one answer.": "Choisissez une réponse.",
    "Course navigation": "Navigation du cours",
    Breadcrumbs: "Fil d’Ariane",
    "Search this site": "Rechercher sur ce site",
    Search: "Rechercher",
    "Open search filters": "Ouvrir les filtres",
    "Search filters": "Filtres de recherche",
  },
  de: {
    "Could not start the Python runtime.": "Python konnte nicht gestartet werden.",
    "The calculation exceeded five seconds. Use smaller inputs and try again.": "Die Berechnung dauerte länger als fünf Sekunden. Verkleinern Sie die Eingabe.",
    "Could not refresh the course library. Reload the page and try again.": "Die Bibliothek konnte nicht aktualisiert werden. Laden Sie die Seite neu.",
    "The runtime was reset.": "Die Umgebung wurde zurückgesetzt.",
    "Execution finished without output.": "Ausführung ohne Ausgabe beendet.",
    "Preparing Python…": "Python wird vorbereitet…",
    "The first run takes a moment while the Python runtime loads.": "Der erste Lauf benötigt Zeit zum Laden von Python.",
    "Running…": "Wird ausgeführt…",
    Error: "Fehler",
    Complete: "Fertig",
    "Could not run the code": "Code konnte nicht ausgeführt werden",
    "The runtime was reset. Python will reload on the next run.": "Umgebung zurückgesetzt. Python wird beim nächsten Lauf geladen.",
    "Not run": "Nicht ausgeführt",
    "Choose one answer.": "Wählen Sie eine Antwort.",
    "Course navigation": "Kursnavigation",
    Breadcrumbs: "Navigationspfad",
    "Search this site": "Website durchsuchen",
    Search: "Suchen",
    "Open search filters": "Suchfilter öffnen",
    "Search filters": "Suchfilter",
  },
  ko: {
    "Could not start the Python runtime.": "Python 실행 환경을 시작할 수 없습니다.",
    "The calculation exceeded five seconds. Use smaller inputs and try again.": "계산이 5초를 넘었습니다. 입력을 줄여 다시 실행하세요.",
    "Could not refresh the course library. Reload the page and try again.": "강의 라이브러리를 갱신할 수 없습니다. 페이지를 새로 고치세요.",
    "The runtime was reset.": "실행 환경이 초기화되었습니다.",
    "Execution finished without output.": "출력 없이 실행이 끝났습니다.",
    "Preparing Python…": "Python 준비 중…",
    "The first run takes a moment while the Python runtime loads.": "첫 실행에는 Python을 불러오는 시간이 필요합니다.",
    "Running…": "실행 중…",
    Error: "오류",
    Complete: "완료",
    "Could not run the code": "코드를 실행할 수 없습니다",
    "The runtime was reset. Python will reload on the next run.": "환경을 초기화했습니다. 다음 실행 때 Python을 다시 불러옵니다.",
    "Not run": "실행 전",
    "Choose one answer.": "답을 하나 고르세요.",
    "Course navigation": "강의 탐색",
    Breadcrumbs: "이동 경로",
    "Search this site": "사이트 검색",
    Search: "검색",
    "Open search filters": "검색 필터 열기",
    "Search filters": "검색 필터",
  },
  ru: {
    "Could not start the Python runtime.": "Не удалось запустить Python.",
    "The calculation exceeded five seconds. Use smaller inputs and try again.": "Вычисление превысило пять секунд. Уменьшите вход.",
    "Could not refresh the course library. Reload the page and try again.": "Не удалось обновить библиотеку. Перезагрузите страницу.",
    "The runtime was reset.": "Среда сброшена.",
    "Execution finished without output.": "Выполнение завершено без вывода.",
    "Preparing Python…": "Подготовка Python…",
    "The first run takes a moment while the Python runtime loads.": "Первый запуск требует времени на загрузку Python.",
    "Running…": "Выполняется…",
    Error: "Ошибка",
    Complete: "Готово",
    "Could not run the code": "Не удалось выполнить код",
    "The runtime was reset. Python will reload on the next run.": "Среда сброшена. Python загрузится при следующем запуске.",
    "Not run": "Не запущено",
    "Choose one answer.": "Выберите один ответ.",
    "Course navigation": "Навигация курса",
    Breadcrumbs: "Навигационная цепочка",
    "Search this site": "Поиск по сайту",
    Search: "Поиск",
    "Open search filters": "Открыть фильтры",
    "Search filters": "Фильтры поиска",
  },
  ar: {
    "Could not start the Python runtime.": "تعذر بدء بيئة Python.",
    "The calculation exceeded five seconds. Use smaller inputs and try again.": "تجاوز الحساب خمس ثوانٍ. صغّر المدخلات.",
    "Could not refresh the course library. Reload the page and try again.": "تعذر تحديث المكتبة. أعد تحميل الصفحة.",
    "The runtime was reset.": "أُعيد ضبط البيئة.",
    "Execution finished without output.": "انتهى التنفيذ بلا مخرجات.",
    "Preparing Python…": "جارٍ إعداد Python…",
    "The first run takes a moment while the Python runtime loads.": "يستغرق التشغيل الأول وقتًا لتحميل Python.",
    "Running…": "جارٍ التنفيذ…",
    Error: "خطأ",
    Complete: "اكتمل",
    "Could not run the code": "تعذر تنفيذ الشفرة",
    "The runtime was reset. Python will reload on the next run.": "أُعيد ضبط البيئة وسيُحمّل Python في التشغيل التالي.",
    "Not run": "لم يُشغّل",
    "Choose one answer.": "اختر إجابة واحدة.",
    "Course navigation": "تنقل الدورة",
    Breadcrumbs: "مسار التنقل",
    "Search this site": "البحث في الموقع",
    Search: "بحث",
    "Open search filters": "فتح مرشحات البحث",
    "Search filters": "مرشحات البحث",
  },
  hi: {
    "Could not start the Python runtime.": "Python runtime शुरू नहीं हो सका।",
    "The calculation exceeded five seconds. Use smaller inputs and try again.": "गणना पाँच सेकंड से अधिक चली। input छोटा करें।",
    "Could not refresh the course library. Reload the page and try again.": "पाठ्यक्रम library अपडेट नहीं हुई। पृष्ठ reload करें।",
    "The runtime was reset.": "runtime reset हो गया।",
    "Execution finished without output.": "execution बिना output के पूरा हुआ।",
    "Preparing Python…": "Python तैयार हो रहा है…",
    "The first run takes a moment while the Python runtime loads.": "पहली बार Python load होने में कुछ समय लगता है।",
    "Running…": "चल रहा है…",
    Error: "त्रुटि",
    Complete: "पूरा",
    "Could not run the code": "कोड नहीं चल सका",
    "The runtime was reset. Python will reload on the next run.": "runtime reset हुआ। अगली बार Python फिर load होगा।",
    "Not run": "अभी नहीं चला",
    "Choose one answer.": "एक उत्तर चुनें।",
    "Course navigation": "पाठ्यक्रम navigation",
    Breadcrumbs: "navigation path",
    "Search this site": "इस site में खोजें",
    Search: "खोजें",
    "Open search filters": "search filter खोलें",
    "Search filters": "search filter",
  },
};
const text = (english, japanese) =>
  isJapanese
    ? japanese
    : (uiTranslations[routeLocale]?.[english] ?? english);

if (routeLocale === "ar") {
  document.documentElement.dir = "rtl";
}

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
      title || text("Python code", "Pythonコード"),
    );
  }
  if (!output.hasAttribute("aria-label")) {
    output.setAttribute(
      "aria-label",
      title || text("Output", "実行結果"),
    );
  }
  output.tabIndex = 0;
  if (shortcut) {
    shortcut.textContent = "⌘ / Ctrl + Enter";
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
    feedback.textContent = `${correct ? "✓" : "↻"} ${explanation}`;
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
