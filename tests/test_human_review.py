import json
from pathlib import Path

import pytest

from agent.human_review import apply_human_review


def _setup(tmp_path: Path) -> tuple[Path, bytes]:
    (tmp_path / "data" / "researcher").mkdir(parents=True)
    source = Path("data/researcher/salesforce.json")
    raw = source.read_bytes()
    (tmp_path / "data" / "researcher" / "salesforce.json").write_bytes(raw)
    decisions = json.loads(Path("data/reviewed/salesforce_human_decisions.json").read_text())
    path = tmp_path / "decisions.json"
    path.write_text(json.dumps(decisions), encoding="utf-8")
    return path, raw


def test_blank_decisions_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path, _ = _setup(tmp_path)
    payload = json.loads(path.read_text())
    for item in payload["decisions"]:
        item["human_value"] = None
    path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="blank"):
        apply_human_review(path)


def test_human_audit_final_does_not_overwrite_researcher(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path, original = _setup(tmp_path)
    monkeypatch.chdir(tmp_path)
    output = apply_human_review(path)
    assert output == Path("data/final/salesforce.json")
    assert Path("data/researcher/salesforce.json").read_bytes() == original
    final = json.loads(output.read_text())
    assert final["buildability"]["verdict"] == "build_now"
    audit = json.loads(Path("evaluation/salesforce_manual_audit.json").read_text())
    assert len(audit["decisions"]) == 11
