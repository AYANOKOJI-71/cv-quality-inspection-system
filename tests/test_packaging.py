from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_release_contains_documented_local_stack() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Kolektor" in readme
    assert "CC BY-NC-SA 4.0" in readme
    assert (ROOT / "docker-compose.yml").exists()
    assert (ROOT / ".github/workflows/ci.yml").exists()
