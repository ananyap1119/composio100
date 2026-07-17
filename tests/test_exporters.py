import csv
import json
from pathlib import Path

from conftest import result_payload

from agent.exporters import CSV_FIELDS, export_final_results
from agent.schemas import FinalAppResult


def _final(order: int, app_id: str = "example-app") -> FinalAppResult:
    payload = result_payload()
    payload["source_order"] = order
    payload["app_id"] = app_id
    return FinalAppResult.model_validate(payload)


def test_empty_export_is_valid(tmp_path: Path) -> None:
    json_path, csv_path = export_final_results([], tmp_path)
    assert json.loads(json_path.read_text(encoding="utf-8")) == []
    with csv_path.open(encoding="utf-8", newline="") as handle:
        assert next(csv.reader(handle)) == CSV_FIELDS


def test_export_serializes_enums_preserves_urls_and_sorts(tmp_path: Path) -> None:
    json_path, csv_path = export_final_results(
        [_final(2, "second-app"), _final(1, "first-app")], tmp_path
    )
    records = json.loads(json_path.read_text(encoding="utf-8"))
    assert [record["app_id"] for record in records] == ["first-app", "second-app"]
    assert records[0]["authentication"]["methods"] == ["api_key"]
    with csv_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["source_order"] == "1"
    assert "https://example.com/authentication" in rows[0]["evidence_urls"]

