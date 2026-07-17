import csv
import json
from pathlib import Path

from agent.cli import validate_inventory


def _rows(path: Path = Path("data/apps.csv")) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_inventory_has_exactly_100_unique_ids() -> None:
    rows = _rows()
    assert len(rows) == 100
    assert len({row["app_id"] for row in rows}) == 100
    assert [int(row["source_order"]) for row in rows] == list(range(1, 101))
    assert validate_inventory() == {
        "apps": 100,
        "calibration_apps": 10,
        "source_values_preserved": 100,
        "unresolved_normalized_domains": ["paygent-connect"],
    }


def test_first_ten_are_only_calibration_apps() -> None:
    rows = _rows()
    assert [row["calibration_set"] for row in rows[:10]] == ["true"] * 10
    assert [row["calibration_set"] for row in rows[10:]] == ["false"] * 90
    configured = json.loads(Path("config/calibration_apps.json").read_text(encoding="utf-8"))
    assert configured == [row["app_id"] for row in rows[:10]]


def test_all_source_values_are_preserved_exactly() -> None:
    rows = _rows()
    supplied = _rows(Path("provided_apps.csv"))
    assert len(rows) == len(supplied) == 100
    for row, source in zip(rows, supplied, strict=True):
        assert row["source_order"] == source["source_order"]
        assert row["app_name"] == source["app_name"]
        assert row["category_group"] == source["category_group"]
        assert row["website_hint"] == source["website_hint"]


def test_source_hints_are_not_silently_normalized_or_removed() -> None:
    rows = _rows()
    annotated_hints = {
        row["app_id"]: row["website_hint"] for row in rows if "(" in row["website_hint"]
    }
    assert annotated_hints["twenty"] == "twenty.com (open-source CRM)"
    assert annotated_hints["harvest"] == "harvestapp.com (help.getharvest.com/api-v2)"
    assert annotated_hints["notebooklm"] == "cloud.google.com/gemini (Enterprise API)"
    assert annotated_hints["grain"] == "grain.com (meeting notes)"
    assert all("(" not in row["normalized_domain"] for row in rows)
    assert next(row for row in rows if row["app_id"] == "paygent-connect")[
        "normalized_domain"
    ] == ""
