"""Verify the built bilingual course, runnable wheel, and source snapshots."""

from __future__ import annotations

import json
import re
from contextlib import redirect_stderr, redirect_stdout
from hashlib import sha256
from html import unescape
from io import StringIO
from pathlib import Path
from textwrap import dedent
from typing import cast

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SITE_WHEEL_DIRECTORY = PROJECT_ROOT / "site" / "assets" / "wheels"
SITE_MANIFEST_PATH = SITE_WHEEL_DIRECTORY / "manifest.json"
SITE_SOURCE_DIRECTORY = PROJECT_ROOT / "site" / "assets" / "source"
LESSON_PATHS = tuple(sorted((PROJECT_ROOT / "docs" / "learn").glob("*.md")))
ENGLISH_LESSON_PATHS = tuple(
    sorted((PROJECT_ROOT / "docs" / "en" / "learn").glob("*.md"))
)
CORE_LESSON_PATHS = tuple(
    lesson_path
    for lesson_path in LESSON_PATHS
    if lesson_path.name != "python-basics.md"
)
LEARNING_LAYERS = (
    "definition",
    "representation",
    "implementation",
    "trace",
    "test",
    "boundary",
)
REQUIRED_META_TOPICS = {
    "python-basics.md": ("operator-protocol", "decorator", "dataclass", "test-api"),
    "natural-numbers.md": ("log-decorator",),
    "integers.md": ("dataclass-equality",),
    "rationals.md": ("post-init",),
    "polynomials.md": ("custom-init",),
    "algebraic-roots.md": ("property",),
}
EXPECTED_SOURCE_REFERENCES = {
    "python-basics.md": ("peano/utils.py", "tests/test_utils.py"),
    "natural-numbers.md": (
        "peano/natural_number.py",
        "tests/test_natural_number.py",
    ),
    "integers.md": ("peano/integer.py", "tests/test_integer.py"),
    "rationals.md": ("peano/rational.py", "tests/test_rational.py"),
    "polynomials.md": ("peano/polynomial.py", "tests/test_polynomial.py"),
    "algebraic-roots.md": (
        "peano/algebraic_root.py",
        "tests/test_algebraic_root.py",
    ),
}
REQUIRED_IMPLEMENTATION_SYMBOLS = {
    "python-basics.md": ("def inner(", "@wraps(func)"),
    "natural-numbers.md": (
        "def structural_str(",
        "def __eq__(",
        "localized('[equality: zero case]', '[等値・0の場合]')",
        "def __add__(",
        "localized('[addition: base]', '[加法・基底]')",
        "@log(log_level=4)",
    ),
    "integers.md": ("def __eq__(", "def _coerce_integer("),
    "rationals.md": ("def __eq__(", "def __add__(", "def reduction("),
    "polynomials.md": (
        "def evaluate(",
        "def sturm_sequence(",
        "def count_real_roots(",
    ),
    "algebraic-roots.md": ("def __post_init__(", "def _bisect(", "def trace("),
}
SOURCE_SNAPSHOT_PATHS = tuple(
    Path(path)
    for path in (
        "peano/utils.py",
        "peano/natural_number.py",
        "peano/integer.py",
        "peano/rational.py",
        "peano/polynomial.py",
        "peano/algebraic_root.py",
        "tests/test_utils.py",
        "tests/test_natural_number.py",
        "tests/test_integer.py",
        "tests/test_rational.py",
        "tests/test_polynomial.py",
        "tests/test_algebraic_root.py",
        "tests/test_numeric_tower.py",
    )
)
RUNNER_SOURCE_PATTERN = re.compile(
    r'<textarea[^>]*data-role="source"[^>]*>(.*?)</textarea>',
    re.DOTALL,
)
FENCED_PYTHON_PATTERN = re.compile(r"```python\n(.*?)\n```", re.DOTALL)
JAPANESE_STYLE_FORBIDDEN_PATTERNS = {
    "教材内で「監査」ではなく、何を確かめるかを具体的に書いてください": re.compile(
        r"監査|\baudit\b",
        re.IGNORECASE,
    ),
    "学習者向けの章・実験・出力ラベルは日本語で書いてください": re.compile(
        r"\bLesson\s+\d|\bExperiment\b|>Output<"
    ),
    "学習段階のラベルは日本語だけで書いてください": re.compile(
        r" · (?:Definition|Representation|Implementation|Trace|Test)"
    ),
    "本文では「ペアノ」と表記してください": re.compile(r"\bPeano\b"),
    "コード由来の英語は日本語で説明してください": re.compile(
        r"公開helper|module内|coercion（|well-defined|metadataの|"
        r"公開signature|decorated関数|assertionを|観察倍率|"
        r"実装境界|高速化境界|Python外部の型|辞書やset|hashする|"
        r"tuple unpacking"
    ),
}


def verify_lesson_structure() -> None:
    """Verify the prediction, execution, and reflection loop in each lesson."""

    for lesson_path in LESSON_PATHS:
        source = lesson_path.read_text(encoding="utf-8")
        visible_numeric_levels = re.findall(r"\bLevel\s+\d+\b", source)
        if visible_numeric_levels:
            raise RuntimeError(
                f"{lesson_path.relative_to(PROJECT_ROOT)} exposes internal log "
                f"levels in learner-facing prose: {visible_numeric_levels}"
            )
        required_markers = (
            'class="lesson-goals"',
            'class="implementation-bridge"',
            'class="learning-prompt"',
            'class="knowledge-check"',
            'data-role="feedback"',
        )
        missing = [marker for marker in required_markers if marker not in source]
        if missing:
            raise RuntimeError(
                f"{lesson_path.relative_to(PROJECT_ROOT)} is missing course "
                f"elements: {missing}"
            )

        runner_count = source.count('data-role="source"')
        labelled_runner_count = source.count('data-role="source" aria-label=')
        if runner_count != labelled_runner_count:
            raise RuntimeError(
                f"{lesson_path.relative_to(PROJECT_ROOT)} has a runner source "
                "without an aria-label"
            )

        if source.count('class="knowledge-check"') != source.count("data-correct"):
            raise RuntimeError(
                f"{lesson_path.relative_to(PROJECT_ROOT)} must have exactly one "
                "correct answer per knowledge check"
            )

        missing_meta_topics = [
            topic
            for topic in REQUIRED_META_TOPICS[lesson_path.name]
            if f'data-meta="{topic}"' not in source
        ]
        if missing_meta_topics:
            raise RuntimeError(
                f"{lesson_path.relative_to(PROJECT_ROOT)} is missing Python "
                f"data-model topics: {missing_meta_topics}"
            )

        implementation_path, test_path = EXPECTED_SOURCE_REFERENCES[lesson_path.name]
        source_reference = f'data-source-reference="{implementation_path}"'
        test_reference = f'data-test-reference="{test_path}"'
        implementation_link = f'href="/assets/source/{implementation_path}"'
        test_link = f'href="/assets/source/{test_path}"'
        if (
            source_reference not in source
            or test_reference not in source
            or implementation_link not in source
            or test_link not in source
        ):
            raise RuntimeError(
                f"{lesson_path.relative_to(PROJECT_ROOT)} is missing an "
                "implementation or test reference"
            )
        if source.index(source_reference) > source.index('class="learning-prompt"'):
            raise RuntimeError(
                f"{lesson_path.relative_to(PROJECT_ROOT)} must show source "
                "references before the first prediction"
            )

        missing_implementation_symbols = [
            symbol
            for symbol in REQUIRED_IMPLEMENTATION_SYMBOLS[lesson_path.name]
            if symbol not in source
        ]
        if missing_implementation_symbols:
            raise RuntimeError(
                f"{lesson_path.relative_to(PROJECT_ROOT)} lacks implementation "
                f"symbols needed for reasoning: {missing_implementation_symbols}"
            )

    for lesson_path in CORE_LESSON_PATHS:
        source = lesson_path.read_text(encoding="utf-8")
        missing_layers = [
            layer for layer in LEARNING_LAYERS if f'data-layer="{layer}"' not in source
        ]
        if missing_layers:
            raise RuntimeError(
                f"{lesson_path.relative_to(PROJECT_ROOT)} is missing learning "
                f"layers: {missing_layers}"
            )


def verify_english_lesson_structure() -> None:
    """Verify that the English course covers every chapter and learning layer."""

    expected_names = {path.name for path in LESSON_PATHS}
    actual_names = {path.name for path in ENGLISH_LESSON_PATHS}
    if actual_names != expected_names:
        raise RuntimeError(
            "English lesson set differs from Japanese lesson set: "
            f"expected {sorted(expected_names)}, found {sorted(actual_names)}"
        )

    for lesson_path in ENGLISH_LESSON_PATHS:
        source = lesson_path.read_text(encoding="utf-8")
        required_markers = (
            'class="lesson-goals"',
            'class="implementation-bridge"',
            'class="learning-prompt"',
            'class="knowledge-check"',
            'data-role="feedback"',
        )
        missing = [marker for marker in required_markers if marker not in source]
        if missing:
            raise RuntimeError(
                f"{lesson_path.relative_to(PROJECT_ROOT)} is missing course "
                f"elements: {missing}"
            )
        if source.count('class="knowledge-check"') != source.count("data-correct"):
            raise RuntimeError(
                f"{lesson_path.relative_to(PROJECT_ROOT)} must have exactly one "
                "correct answer per knowledge check"
            )
        runner_count = source.count('data-role="source"')
        labelled_runner_count = source.count('data-role="source" aria-label=')
        if runner_count != labelled_runner_count:
            raise RuntimeError(
                f"{lesson_path.relative_to(PROJECT_ROOT)} has a runner source "
                "without an aria-label"
            )

    for lesson_path in ENGLISH_LESSON_PATHS:
        if lesson_path.name == "python-basics.md":
            continue
        source = lesson_path.read_text(encoding="utf-8")
        missing_layers = [
            layer for layer in LEARNING_LAYERS if f'data-layer="{layer}"' not in source
        ]
        if missing_layers:
            raise RuntimeError(
                f"{lesson_path.relative_to(PROJECT_ROOT)} is missing learning "
                f"layers: {missing_layers}"
            )


def verify_runner_examples() -> None:
    """Run course examples to detect prose/implementation drift."""

    markdown_paths = tuple(sorted((PROJECT_ROOT / "docs").rglob("*.md")))
    for markdown_path in markdown_paths:
        source = markdown_path.read_text(encoding="utf-8")
        for index, match in enumerate(RUNNER_SOURCE_PATTERN.finditer(source), start=1):
            example = unescape(match.group(1))
            namespace = {"__name__": "__docs_example__"}
            try:
                with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                    exec(
                        compile(
                            example,
                            f"{markdown_path.relative_to(PROJECT_ROOT)}:runner-{index}",
                            "exec",
                        ),
                        namespace,
                    )
            except Exception as error:
                raise RuntimeError(
                    f"runner {index} in "
                    f"{markdown_path.relative_to(PROJECT_ROOT)} failed"
                ) from error


def verify_fenced_python() -> None:
    """Compile function and class excerpts as Python syntax."""

    markdown_paths = tuple(sorted((PROJECT_ROOT / "docs").rglob("*.md")))
    for markdown_path in markdown_paths:
        source = markdown_path.read_text(encoding="utf-8")
        for index, match in enumerate(FENCED_PYTHON_PATTERN.finditer(source), start=1):
            example = dedent(match.group(1))
            stripped = example.lstrip()
            if not stripped.startswith(("@", "def ", "class ")):
                continue
            try:
                compile(
                    example,
                    f"{markdown_path.relative_to(PROJECT_ROOT)}:python-{index}",
                    "exec",
                )
            except SyntaxError as error:
                raise RuntimeError(
                    f"Python excerpt {index} in "
                    f"{markdown_path.relative_to(PROJECT_ROOT)} has invalid syntax"
                ) from error


def verify_japanese_style() -> None:
    """Keep translation artifacts out of learner-facing Japanese prose."""

    markdown_paths = tuple(
        path
        for path in sorted((PROJECT_ROOT / "docs").rglob("*.md"))
        if (PROJECT_ROOT / "docs" / "en") not in path.parents
    )
    for markdown_path in markdown_paths:
        source = markdown_path.read_text(encoding="utf-8")
        for message, pattern in JAPANESE_STYLE_FORBIDDEN_PATTERNS.items():
            match = pattern.search(source)
            if match is None:
                continue
            line_number = source.count("\n", 0, match.start()) + 1
            raise RuntimeError(
                f"{markdown_path.relative_to(PROJECT_ROOT)}:{line_number}: "
                f"{message}（{match.group(0)!r}）"
            )


def verify_natural_axiom_sequence() -> None:
    """Verify the intended axiom, recursion, and operation sequence."""

    lesson_source = (PROJECT_ROOT / "docs" / "learn" / "natural-numbers.md").read_text(
        encoding="utf-8"
    )
    ordered_sections = (
        "## 等しさの実装で、二つの公理を読む",
        "## 帰納法と再帰を、同じものにしない",
        "## `+` は、どのメソッドを呼ぶのか",
    )
    positions = tuple(lesson_source.index(section) for section in ordered_sections)
    if positions != tuple(sorted(positions)):
        raise RuntimeError(
            "The natural-number chapter must explain equality axioms, "
            "induction/recursion, and addition in that order"
        )

    test_source = (PROJECT_ROOT / "tests" / "test_natural_number.py").read_text(
        encoding="utf-8"
    )
    required_tests = (
        "def test_zero_is_not_a_successor(",
        "def test_successor_is_injective(",
        "def test_add_recursive_equations(",
        "def test_mul_recursive_equations(",
    )
    missing_tests = [test for test in required_tests if test not in test_source]
    if missing_tests:
        raise RuntimeError(
            "Tests corresponding to natural-number axioms and recursive "
            f"equations are missing: {missing_tests}"
        )
    if "def test_add_axioms(" in test_source or "def test_mul_axioms(" in test_source:
        raise RuntimeError(
            "Do not name tests for recursive addition/multiplication equations "
            "as Peano axioms"
        )


def verify_source_snapshots() -> None:
    """Verify linked sources match the tree used for the runnable wheel."""

    for relative_path in SOURCE_SNAPSHOT_PATHS:
        project_source = PROJECT_ROOT / relative_path
        site_source = SITE_SOURCE_DIRECTORY / relative_path
        if not site_source.is_file():
            raise FileNotFoundError(f"course source snapshot is missing: {site_source}")
        if project_source.read_bytes() != site_source.read_bytes():
            raise RuntimeError(
                f"course source snapshot differs from the source: {relative_path}"
            )


def main() -> None:
    verify_japanese_style()
    verify_lesson_structure()
    verify_english_lesson_structure()
    verify_natural_axiom_sequence()
    verify_runner_examples()
    verify_fenced_python()
    verify_source_snapshots()

    manifest = cast(
        dict[str, object],
        json.loads(SITE_MANIFEST_PATH.read_text(encoding="utf-8")),
    )
    wheel_name = manifest.get("wheel")
    wheel_sha256 = manifest.get("sha256")
    if (
        not isinstance(wheel_name, str)
        or Path(wheel_name).name != wheel_name
        or not wheel_name.endswith(".whl")
    ):
        raise RuntimeError(f"invalid wheel manifest: {manifest!r}")

    wheel_path = SITE_WHEEL_DIRECTORY / wheel_name
    if not wheel_path.is_file():
        raise FileNotFoundError(f"course wheel is missing: {wheel_path}")
    expected_sha256 = sha256(wheel_path.read_bytes()).hexdigest()
    if wheel_sha256 != expected_sha256:
        raise RuntimeError("wheel hash in the course manifest does not match the wheel")


if __name__ == "__main__":
    main()
