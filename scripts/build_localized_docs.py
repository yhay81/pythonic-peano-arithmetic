"""Build the translated course variants from one checked learning structure."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import cast

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRANSLATIONS_PATH = PROJECT_ROOT / "docs" / "i18n" / "course.json"
GENERATED_ROOT = PROJECT_ROOT / "build" / "localized-course"
GENERATED_DOCS = GENERATED_ROOT / "docs"
GENERATED_CONFIGS = GENERATED_ROOT


@dataclass(frozen=True)
class Locale:
    """A published course locale."""

    code: str
    route: str
    native_name: str
    theme_language: str
    font: str
    direction: str = "ltr"


LOCALES = (
    Locale("ja", "", "日本語", "ja", "Noto Sans JP"),
    Locale("en", "en", "English", "en", "Inter"),
    Locale("zh-Hans", "zh", "简体中文", "zh", "Noto Sans SC"),
    Locale("zh-Hant", "zh-hant", "繁體中文", "zh", "Noto Sans TC"),
    Locale("es", "es", "Español", "es", "Inter"),
    Locale("pt-BR", "pt-br", "Português (Brasil)", "pt", "Inter"),
    Locale("fr", "fr", "Français", "fr", "Inter"),
    Locale("de", "de", "Deutsch", "de", "Inter"),
    Locale("ko", "ko", "한국어", "ko", "Noto Sans KR"),
    Locale("ru", "ru", "Русский", "ru", "Inter"),
    Locale("ar", "ar", "العربية", "ar", "Noto Sans Arabic", "rtl"),
    Locale("hi", "hi", "हिन्दी", "hi", "Noto Sans Devanagari"),
)
GENERATED_LOCALES = tuple(
    locale for locale in LOCALES if locale.route not in ("", "en")
)
LESSONS = (
    (
        "python-basics",
        "peano/utils.py",
        "tests/test_utils.py",
    ),
    (
        "natural-numbers",
        "peano/natural_number.py",
        "tests/test_natural_number.py",
    ),
    (
        "integers",
        "peano/integer.py",
        "tests/test_integer.py",
    ),
    (
        "rationals",
        "peano/rational.py",
        "tests/test_rational.py",
    ),
    (
        "polynomials",
        "peano/polynomial.py",
        "tests/test_polynomial.py",
    ),
    (
        "algebraic-roots",
        "peano/algebraic_root.py",
        "tests/test_algebraic_root.py",
    ),
)
# Short excerpts isolate the operation used in the worked example.
CALCULATION_EXCERPTS = {
    "python-basics": """result, message = func(*args, **kwargs)
if logger.isEnabledFor(log_level):
    logger.log(log_level, message if isinstance(message, str) else message())
return result""",
    "natural-numbers": """predecessor = other.pre
if predecessor is None:
    return self
return successor(self + predecessor)""",
    "integers": """result = Integer(
    self.a * converted.a + self.b * converted.b,
    self.a * converted.b + self.b * converted.a,
)""",
    "rationals": """result = Rational(
    self.p * converted.q + self.q * converted.p,
    self.q * converted.q,
)""",
    "polynomials": """result = Q_ZERO
for coefficient in reversed(self.coefficients):
    result = (result * point + coefficient).reduction()""",
    "algebraic-roots": """midpoint = interval.midpoint
midpoint_sign = polynomial_value.sign_at(midpoint)
lower_sign = polynomial_value.sign_at(interval.lower)
if midpoint_sign == 0:
    result = RationalInterval(midpoint, midpoint)
elif lower_sign != midpoint_sign:
    result = RationalInterval(interval.lower, midpoint)
else:
    result = RationalInterval(midpoint, interval.upper)""",
}

RUNNER_SOURCES = {
    "python-basics": """class Score:
    def __init__(self, points):
        self.points = points

    def __add__(self, other):
        return Score(self.points + other.points)


a = Score(2)
b = Score(1)
print((a + b).points)""",
    "natural-numbers": """from peano import config_log, natural_number

config_log(log_level=4, max_lines=20, locale="{locale}")
left = natural_number(2)
right = natural_number(2)
print(left + right)""",
    "integers": """from peano import Integer, natural_number

left = Integer(natural_number(0), natural_number(2))
right = Integer(natural_number(3), natural_number(0))
print(left * right)""",
    "rationals": """from peano import rational

left = rational(1, 2)
right = rational(1, 3)
print(left + right)
print(rational(1, 2) == rational(2, 4))""",
    "polynomials": """from peano import count_real_roots, polynomial, rational, sign_variations, sturm_sequence

p = polynomial((-2, 1), (0, 1), (1, 1))
x = rational(3, 2)
print(x, p.evaluate(x))

left = rational(-2, 1)
right = rational(2, 1)
sequence = sturm_sequence(p)
for point in (left, right):
    print(point, sign_variations(sequence, point))
print(count_real_roots(p, left, right))""",
    "algebraic-roots": """from peano import algebraic_root, polynomial

p = polynomial((-2, 1), (0, 1), (1, 1))
root = algebraic_root(p, (1, 1), (2, 1))
for interval in root.trace(2):
    print(interval)""",
}

# These short experiments establish facts used by the next calculation.
WARMUP_SOURCES = {
    "natural-numbers": """from peano import natural_number

two = natural_number(2)
one = natural_number(1)
print(two == two)
print(two == one)""",
    "rationals": """from peano import rational

half = rational(1, 2)
quarters = rational(2, 4)
print(half == quarters)
print(quarters.p, quarters.q)""",
}


# The options use the same mathematical notation in every edition.
QUIZ_OPTIONS = {
    "python-basics": ("3", "6", "4"),
    "natural-numbers": ("2 + 0", "2 + 1", "2 + 2"),
    "integers": ("6", "−2", "−6"),
    "rationals": ("2/5", "5/6", "1/6"),
    "polynomials": ("2", "0", "1"),
    "algebraic-roots": ("[1, 3/2]", "[7/4, 2]", "[3/2, 7/4]"),
}
QUIZ_ANSWERS = {
    "python-basics": "6",
    "natural-numbers": "2 + 0",
    "integers": "−6",
    "rationals": "5/6",
    "polynomials": "2",
    "algebraic-roots": "[3/2, 7/4]",
}


def load_translations() -> dict[str, dict[str, object]]:
    """Load and validate all authored translation records."""

    translations = cast(
        dict[str, dict[str, object]],
        json.loads(TRANSLATIONS_PATH.read_text(encoding="utf-8")),
    )
    expected = {locale.code for locale in GENERATED_LOCALES}
    if set(translations) != expected:
        raise RuntimeError(
            "translation locales differ from configured locales: "
            f"expected {sorted(expected)}, found {sorted(translations)}"
        )
    return translations


def text(record: dict[str, object], key: str) -> str:
    """Read one required translated string."""

    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"missing translated string: {key}")
    return value


def lesson_records(record: dict[str, object]) -> list[dict[str, object]]:
    """Read the six translated lesson records."""

    value = record.get("lessons")
    if (
        not isinstance(value, list)
        or len(value) != len(LESSONS)
        or any(not isinstance(item, dict) for item in value)
    ):
        raise RuntimeError("lessons must contain six translation records")
    return cast(list[dict[str, object]], value)


def render_runner(
    common: dict[str, object],
    title: str,
    source: str,
) -> str:
    """Render one editable Pyodide exercise."""

    return f"""
<div class="peano-runner" data-state="idle" data-reveal>
  <div class="peano-runner__header">
    <span>{text(common, "experiment")} · {title}</span>
    <span class="peano-runner__status" data-role="status">{text(common, "not_run")}</span>
  </div>
  <textarea class="peano-runner__source" data-role="source" aria-label="{text(common, "source_label")}: {title}"
    spellcheck="false">{escape(source, quote=False)}</textarea>
  <div class="peano-runner__controls">
    <button class="peano-runner__button peano-runner__button--run"
      data-action="run">▶ {text(common, "run")}</button>
    <button class="peano-runner__button"
      data-action="reset">{text(common, "reset")}</button>
    <span class="peano-runner__shortcut">⌘ / Ctrl + Enter</span>
  </div>
  <div class="peano-runner__output-wrap">
    <span class="peano-runner__output-label">{text(common, "output")}</span>
    <pre class="peano-runner__output" data-role="output"
      aria-live="polite">{text(common, "predict_first")}</pre>
  </div>
</div>
"""


def render_home(
    locale: Locale,
    record: dict[str, object],
    lessons: list[dict[str, object]],
) -> str:
    """Render a translated course introduction."""

    common = cast(dict[str, object], record["common"])
    lesson_links = "\n".join(
        f"- [{index:02d} · {text(lesson, 'title')}](learn/{slug}.md)"
        for index, ((slug, _, _), lesson) in enumerate(
            zip(LESSONS, lessons, strict=True)
        )
    )
    return f"""<span class="lesson-number">{text(common, "course")}</span>

# {text(record, "home_title")}

<p class="lesson-lead">{text(record, "home_lead")}</p>

<div class="lesson-context" data-reveal>
  <strong>{text(common, "assumption")}</strong>
  <p>{text(record, "home_assumption")}</p>
</div>

## {text(record, "home_method_title")}

{text(record, "home_method")}

<div class="implementation-bridge" data-reveal>
  <div><strong>{text(common, "definition")}</strong><p>{text(common, "definition_help")}</p></div>
  <div><strong>{text(common, "representation")}</strong><p>{text(common, "representation_help")}</p></div>
  <div><strong>{text(common, "implementation")}</strong><p>{text(common, "implementation_help")}</p></div>
</div>

## {text(common, "chapters")}

{lesson_links}

{text(record, "home_finish")}
"""


def render_lesson(
    locale: Locale,
    record: dict[str, object],
    lesson: dict[str, object],
    index: int,
) -> str:
    """Render one translated lesson with the shared learning progression."""

    common = cast(dict[str, object], record["common"])
    slug, source_path, test_path = LESSONS[index]
    title = text(lesson, "title")
    question = text(lesson, "prediction")
    options = []
    for option in QUIZ_OPTIONS[slug]:
        correct = option == QUIZ_ANSWERS[slug]
        feedback = text(lesson, "trace") if correct else text(common, "wrong_feedback")
        marker = " data-correct" if correct else ""
        options.append(
            f'<label><input type="radio" name="{slug}-check"{marker} '
            f'data-feedback="{escape(feedback, quote=True)}"> '
            f'<bdi dir="ltr">{option}</bdi></label>'
        )
    worked_example = text(lesson, "worked")
    if slug in WARMUP_SOURCES:
        warmup = render_runner(
            common, text(common, "representation"), WARMUP_SOURCES[slug]
        )
        worked_example += "\n\n" + warmup
    choices = "\n    ".join(options)
    lessons = lesson_records(record)
    next_link = (
        f"[{text(lessons[index + 1], 'title')}]({LESSONS[index + 1][0]}.md)"
        if index + 1 < len(lessons)
        else f"[{text(record, 'nav_playground')}](../playground.md)"
    )
    runner = render_runner(
        common, title, RUNNER_SOURCES[slug].format(locale=locale.code)
    )
    if slug == "python-basics":
        worked_example += "\n\n" + runner
        runner = ""
    return f"""<span class="lesson-number">{index:02d}</span>

# {title}

<div class="lesson-goals"><p>{text(lesson, "lead")}</p></div>

<h2 data-layer="definition">{text(common, "definition")}</h2>

{text(lesson, "definition")}

<h2 data-layer="representation">{text(common, "representation")}</h2>

{text(lesson, "representation")}

{worked_example}

<div class="implementation-bridge" data-source-reference="{source_path}" data-test-reference="{test_path}">
  <a href="/assets/source/{source_path}">{source_path}</a>
  <a href="/assets/source/{test_path}">{test_path}</a>
</div>

<h2 data-layer="implementation">{text(common, "implementation")}</h2>

{text(lesson, "implementation")}

```python
{CALCULATION_EXCERPTS[slug]}
```

<h2 data-layer="trace">{text(common, "trace")}</h2>

<div class="learning-prompt"><strong>{text(common, "prediction")}</strong><p>{question}</p></div>

{runner}

<form class="knowledge-check" data-reveal>
  <fieldset>
    <legend>{text(common, "check")}</legend>
    {choices}
  </fieldset>
  <button type="submit">{text(common, "check")}</button>
  <p data-role="feedback" aria-live="polite"></p>
</form>

<details class="self-check"><summary>{text(common, "output")}</summary><p>{text(lesson, "trace")}</p></details>

<h2 data-layer="test">{text(common, "test")}</h2>

{text(lesson, "test")}

<h2 data-layer="boundary">{text(common, "boundary")}</h2>

{text(lesson, "boundary")}

{next_link}
"""


def render_playground(locale: Locale, record: dict[str, object]) -> str:
    """Render a translated free-experiment page."""

    common = cast(dict[str, object], record["common"])
    return f"""# {text(record, "playground_title")}

<p class="lesson-lead">{text(record, "playground_lead")}</p>

<div class="learning-prompt" data-kind="prediction" data-reveal>
  <strong>{text(common, "prediction")}</strong>
  <p>{text(record, "playground_prediction")}</p>
</div>

{
        render_runner(
            common,
            text(record, "playground_experiment"),
            RUNNER_SOURCES["natural-numbers"].format(locale=locale.code),
        )
    }

## {text(record, "playground_next_title")}

{text(record, "playground_next")}
"""


def render_about(record: dict[str, object]) -> str:
    """Render translated course scope and method."""

    return f"""# {text(record, "about_title")}

{text(record, "about_intro")}

## {text(record, "about_python_title")}

{text(record, "about_python")}

## {text(record, "about_runtime_title")}

{text(record, "about_runtime")}

## {text(record, "about_limits_title")}

{text(record, "about_limits")}
"""


def render_reference(
    record: dict[str, object],
    lessons: list[dict[str, object]],
) -> str:
    """Render translated source-reference index."""

    rows = "\n".join(
        f"| {text(lesson, 'title')} | "
        f"[`{source}`](/assets/source/{source}) | "
        f"[`{test}`](/assets/source/{test}) |"
        for (_, source, test), lesson in zip(LESSONS, lessons, strict=True)
    )
    return f"""# {text(record, "reference_title")}

{text(record, "reference_intro")}

| {text(record, "reference_chapter")} | {text(record, "reference_source")} | {text(record, "reference_test")} |
| --- | --- | --- |
{rows}

{text(record, "reference_note")}
"""


def toml_string(value: str) -> str:
    """Encode a simple TOML string."""

    return json.dumps(value, ensure_ascii=False)


def render_config(locale: Locale, record: dict[str, object]) -> str:
    """Render one Zensical project configuration."""

    lessons = lesson_records(record)
    common = cast(dict[str, object], record["common"])
    alternate = ",\n  ".join(
        (
            "{name = "
            f"{toml_string(item.native_name)}, "
            f"link = {toml_string('/' if not item.route else f'/{item.route}/')}, "
            f"lang = {toml_string(item.code)}"
            "}"
        )
        for item in LOCALES
    )
    lesson_nav_entries = []
    for index, ((slug, _, _), lesson) in enumerate(zip(LESSONS, lessons, strict=True)):
        label = f"{index:02d} {text(lesson, 'title')}"
        lesson_nav_entries.append(
            f"{{{toml_string(label)} = {toml_string(f'learn/{slug}.md')}}}"
        )
    lesson_nav = ",\n    ".join(lesson_nav_entries)
    route = locale.route
    return f"""[project]
docs_dir = {toml_string(f"docs/{route}")}
site_dir = {toml_string(f"site/{route}")}
site_name = "Peano Arithmetic"
site_description = {toml_string(text(record, "site_description"))}
site_url = {toml_string(f"https://peano.yhay81.com/{route}/")}
repo_url = "https://github.com/yhay81/pythonic-peano-arithmetic"
edit_uri = "edit/main/docs/i18n/"
copyright = "Copyright &copy; 2026 Yusuke Hayashi"
extra_css = ["/stylesheets/extra.css"]
extra_javascript = ["/javascripts/pyodide-runner.mjs"]
nav = [
  {{{toml_string(text(record, "nav_home"))} = "index.md"}},
  {{{toml_string(text(record, "nav_learn"))} = [
    {lesson_nav},
  ]}},
  {{{toml_string(text(record, "nav_playground"))} = "playground.md"}},
  {{{toml_string(text(record, "nav_about"))} = "about.md"}},
  {{{toml_string(text(record, "nav_reference"))} = "reference/implementation.md"}},
]

[project.extra]
alternate = [
  {alternate},
]
direction = {toml_string(locale.direction)}

[project.theme]
language = {toml_string(locale.theme_language)}
font.text = {toml_string(locale.font)}
font.code = "IBM Plex Mono"
features = [
  "navigation.instant",
  "navigation.instant.progress",
  "navigation.path",
  "navigation.sections",
  "navigation.tracking",
  "navigation.top",
  "toc.follow",
  "content.code.copy",
]

[[project.theme.palette]]
media = "(prefers-color-scheme: light)"
scheme = "default"
primary = "custom"
accent = "custom"
toggle.icon = "lucide/sun"
toggle.name = {toml_string(text(common, "dark_mode"))}

[[project.theme.palette]]
media = "(prefers-color-scheme: dark)"
scheme = "slate"
primary = "custom"
accent = "custom"
toggle.icon = "lucide/moon"
toggle.name = {toml_string(text(common, "light_mode"))}
"""


def build_locale(locale: Locale, record: dict[str, object]) -> None:
    """Generate and build one translated locale."""

    destination = GENERATED_DOCS / locale.route
    lessons_destination = destination / "learn"
    reference_destination = destination / "reference"
    lessons_destination.mkdir(parents=True)
    reference_destination.mkdir(parents=True)
    lessons = lesson_records(record)

    (destination / "index.md").write_text(
        render_home(locale, record, lessons), encoding="utf-8"
    )
    (destination / "playground.md").write_text(
        render_playground(locale, record), encoding="utf-8"
    )
    (destination / "about.md").write_text(render_about(record), encoding="utf-8")
    (reference_destination / "implementation.md").write_text(
        render_reference(record, lessons), encoding="utf-8"
    )
    for index, ((slug, _, _), lesson) in enumerate(zip(LESSONS, lessons, strict=True)):
        (lessons_destination / f"{slug}.md").write_text(
            render_lesson(locale, record, lesson, index), encoding="utf-8"
        )

    config_path = GENERATED_CONFIGS / f"{locale.route}.toml"
    config_path.write_text(render_config(locale, record), encoding="utf-8")
    subprocess.run(
        (
            "uv",
            "run",
            "--locked",
            "zensical",
            "build",
            "--clean",
            "--config-file",
            str(config_path),
        ),
        cwd=PROJECT_ROOT,
        check=True,
    )
    built_site = GENERATED_CONFIGS / "site" / locale.route
    published_site = PROJECT_ROOT / "site" / locale.route
    if published_site.exists():
        shutil.rmtree(published_site)
    shutil.copytree(built_site, published_site)


def main() -> None:
    """Generate and build every locale not maintained as authored Markdown."""

    translations = load_translations()
    if GENERATED_DOCS.exists():
        shutil.rmtree(GENERATED_DOCS)
    if GENERATED_CONFIGS.exists():
        shutil.rmtree(GENERATED_CONFIGS)
    GENERATED_CONFIGS.mkdir(parents=True)
    for locale in GENERATED_LOCALES:
        build_locale(locale, translations[locale.code])


if __name__ == "__main__":
    main()
