"""Build the documentation wheel and its manifest."""

from __future__ import annotations

import json
import shutil
import subprocess
from hashlib import sha256
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WHEEL_DIRECTORY = PROJECT_ROOT / "docs" / "assets" / "wheels"
MANIFEST_PATH = WHEEL_DIRECTORY / "manifest.json"
SOURCE_DIRECTORY = PROJECT_ROOT / "docs" / "assets" / "source"
SOURCE_PATHS = (
    Path("peano/utils.py"),
    Path("peano/natural_number.py"),
    Path("peano/integer.py"),
    Path("peano/rational.py"),
    Path("peano/polynomial.py"),
    Path("peano/algebraic_root.py"),
    Path("tests/test_utils.py"),
    Path("tests/test_natural_number.py"),
    Path("tests/test_integer.py"),
    Path("tests/test_rational.py"),
    Path("tests/test_polynomial.py"),
    Path("tests/test_algebraic_root.py"),
    Path("tests/test_numeric_tower.py"),
)


def prepare_source_snapshots() -> None:
    """Expose source snapshots from the same tree as the runnable wheel."""

    if SOURCE_DIRECTORY.exists():
        shutil.rmtree(SOURCE_DIRECTORY)
    for relative_path in SOURCE_PATHS:
        source_path = PROJECT_ROOT / relative_path
        destination_path = SOURCE_DIRECTORY / relative_path
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, destination_path)


def main() -> None:
    WHEEL_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for wheel in WHEEL_DIRECTORY.glob("*.whl"):
        wheel.unlink()

    subprocess.run(
        (
            "uv",
            "build",
            "--wheel",
            "--out-dir",
            str(WHEEL_DIRECTORY),
        ),
        cwd=PROJECT_ROOT,
        check=True,
    )

    wheels = sorted(WHEEL_DIRECTORY.glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"expected exactly one wheel, found: {wheels}")

    wheel = wheels[0]
    MANIFEST_PATH.write_text(
        json.dumps(
            {
                "wheel": wheel.name,
                "sha256": sha256(wheel.read_bytes()).hexdigest(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    prepare_source_snapshots()


if __name__ == "__main__":
    main()
