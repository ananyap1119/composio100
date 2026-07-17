"""Minimal Phase 1 command-line interface."""

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from agent.exporters import export_final_results
from agent.human_review import apply_human_review
from agent.research.composio_tools import ComposioUnavailable
from agent.research.researcher import (
    CoverageError,
    MissingEnvironment,
    run_research,
    run_research_batch,
)
from agent.schemas import (
    AppResearchResult,
    FinalAppResult,
)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"file not found: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON in {path}: {error}") from error


SOURCE_FIELDS = ("source_order", "category_group", "app_name", "website_hint")
INVENTORY_FIELDS = (
    "app_id",
    "source_order",
    "category_group",
    "app_name",
    "website_hint",
    "normalized_domain",
    "calibration_set",
)
NORMALIZED_DOMAIN = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?(?:/[A-Za-z0-9._~!$&'*+,;=:@%/-]*)?$"
)


def _read_csv(path: Path, label: str) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
            fields = reader.fieldnames or []
    except FileNotFoundError as error:
        raise ValueError(f"{label} not found: {path}") from error
    return fields, rows


def validate_inventory(
    path: Path = Path("data/apps.csv"),
    source_path: Path = Path("provided_apps.csv"),
) -> dict[str, int | list[str]]:
    fields, rows = _read_csv(path, "inventory")
    source_fields, source_rows = _read_csv(source_path, "source inventory")
    if fields != list(INVENTORY_FIELDS):
        raise ValueError(f"inventory columns must be exactly: {list(INVENTORY_FIELDS)}")
    if source_fields != list(SOURCE_FIELDS):
        raise ValueError(f"source inventory columns must be exactly: {list(SOURCE_FIELDS)}")
    if len(rows) != 100:
        raise ValueError(f"expected exactly 100 apps, found {len(rows)}")
    if len(source_rows) != 100:
        raise ValueError(f"expected exactly 100 source apps, found {len(source_rows)}")
    ids = [row["app_id"] for row in rows]
    names = [row["app_name"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("app_id values must be unique")
    if len(names) != len(set(names)):
        raise ValueError("app_name values must be unique")
    try:
        orders = [int(row["source_order"]) for row in rows]
    except ValueError as error:
        raise ValueError("source_order values must be integers") from error
    if orders != list(range(1, 101)):
        raise ValueError("source_order must preserve the contiguous supplied order 1..100")
    for index, (row, source_row) in enumerate(zip(rows, source_rows, strict=True), start=1):
        for field in SOURCE_FIELDS:
            if row[field] != source_row[field]:
                raise ValueError(
                    f"source value changed at row {index}, field {field}: "
                    f"{row[field]!r} != {source_row[field]!r}"
                )
    flags = [row["calibration_set"].lower() == "true" for row in rows]
    if flags != [True] * 10 + [False] * 90:
        raise ValueError("only the first 10 apps may be in the calibration set")
    configured = json.loads(Path("config/calibration_apps.json").read_text(encoding="utf-8"))
    if configured != ids[:10]:
        raise ValueError("calibration_apps.json must contain only the first 10 app IDs")
    unresolved = [row["app_id"] for row in rows if not row["normalized_domain"].strip()]
    if unresolved != ["paygent-connect"]:
        raise ValueError("Paygent Connect must be the only unresolved normalized domain")
    for row in rows:
        normalized = row["normalized_domain"]
        if normalized and (
            "(" in normalized
            or ")" in normalized
            or "://" in normalized
            or not NORMALIZED_DOMAIN.fullmatch(normalized)
        ):
            raise ValueError(
                f"normalized_domain must contain only a hostname or hostname/path: {normalized!r}"
            )
    return {
        "apps": len(rows),
        "calibration_apps": sum(flags),
        "source_values_preserved": len(rows),
        "unresolved_normalized_domains": unresolved,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m agent.cli",
        description="Validate Composio 100 research records.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    inventory = commands.add_parser("validate-inventory", help="validate the fixed app inventory")
    inventory.add_argument("--path", type=Path, default=Path("data/apps.csv"))
    inventory.add_argument("--source", type=Path, default=Path("provided_apps.csv"))
    validate = commands.add_parser("validate-result", help="validate one research result")
    validate.add_argument("path", type=Path)
    export = commands.add_parser("export", help="export validated final results")
    export.add_argument("results", type=Path)
    export.add_argument("--output-dir", type=Path, default=Path("data/final"))
    research = commands.add_parser("research", help="run the Salesforce Phase 2A researcher")
    research.add_argument("--app-id", required=True)
    research.add_argument("--dry-run", action="store_true")
    research.add_argument(
        "--resume-latest",
        action="store_true",
        help="reuse the most recent stored Salesforce sources",
    )
    batch = commands.add_parser(
        "research-batch", help="research the calibration app set sequentially"
    )
    batch.add_argument("--calibration", action="store_true")
    batch.add_argument("--production", action="store_true")
    batch.add_argument("--start-order", type=int, default=1)
    batch.add_argument("--end-order", type=int, default=100)
    batch.add_argument("--skip-finalized", action="store_true")
    batch.add_argument("--resume", action="store_true")
    apply_review = commands.add_parser(
        "apply-human-review", help="apply completed Salesforce human decisions"
    )
    apply_review.add_argument("--app-id", required=True)
    apply_review.add_argument("--decisions", type=Path, required=True)
    return parser


def run(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "validate-inventory":
        print(json.dumps(validate_inventory(args.path, args.source), indent=2))
    elif args.command == "validate-result":
        raw = _load_json(args.path)
        result = (
            FinalAppResult.model_validate(raw)
            if "source_order" in raw
            else AppResearchResult.model_validate(raw)
        )
        print(json.dumps({"valid": True, "app_id": result.app_id}, indent=2))
    elif args.command == "export":
        payload = _load_json(args.results)
        if not isinstance(payload, list):
            raise ValueError("final-results input must be a JSON array")
        records = [FinalAppResult.model_validate(item) for item in payload]
        json_path, csv_path = export_final_results(records, args.output_dir)
        print(json.dumps({"json": str(json_path), "csv": str(csv_path)}, indent=2))
    elif args.command == "research":
        validate_inventory()
        outcome = run_research(
            args.app_id,
            dry_run=args.dry_run,
            resume_latest=args.resume_latest,
        )
        if hasattr(outcome, "model_dump_json"):
            print(outcome.model_dump_json(indent=2))
        else:
            print(json.dumps(outcome, indent=2))
    elif args.command == "research-batch":
        validate_inventory()
        summary = run_research_batch(
            calibration=args.calibration,
            skip_finalized=args.skip_finalized,
            resume=args.resume,
            production=args.production,
            start_order=args.start_order,
            end_order=args.end_order,
        )
        print(json.dumps(summary, indent=2))
    elif args.command == "apply-human-review":
        if args.app_id != "salesforce":
            raise ValueError("Phase 3 only supports --app-id salesforce")
        path = apply_human_review(args.decisions)
        print(json.dumps({"valid": True, "output": str(path)}, indent=2))
    return 0


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        raise SystemExit(run())
    except (
        ComposioUnavailable,
        CoverageError,
        MissingEnvironment,
        ValueError,
        ValidationError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
