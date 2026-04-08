from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from foodbase.scrapers.models import SourceRecord
from foodbase.scrapers.utils import merge_records

DEFAULT_INPUTS = [
    Path("data/scrapes/madeingreece.json"),
    Path("data/scrapes/greekexporters.json"),
    Path("data/scrapes/kompass.json"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Combine Foodbase scrape outputs into one merged dataset."
    )
    parser.add_argument(
        "--inputs",
        nargs="+",
        type=Path,
        default=DEFAULT_INPUTS,
        help="Input scrape JSON files produced by foodbase.scrapers.run.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/scrapes/greek-food-sources.combined.json"),
        help="Output file path.",
    )
    return parser.parse_args()


def count_values(records: list[dict[str, Any]], field_name: str) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for record in records:
        value = record.get(field_name)
        if isinstance(value, list):
            counter.update(item for item in value if isinstance(item, str))
        elif isinstance(value, str):
            counter.update([value])
    return dict(counter.most_common())


def build_combined_payload(input_paths: list[Path]) -> dict[str, Any]:
    source_records: list[SourceRecord] = []
    input_summaries: list[dict[str, Any]] = []
    file_failures: list[dict[str, str]] = []
    upstream_failures: list[dict[str, str]] = []

    for path in input_paths:
        if not path.exists():
            file_failures.append({"path": str(path), "error": "File does not exist."})
            continue

        payload = json.loads(path.read_text(encoding="utf-8"))
        record_items = payload.get("source_records", [])
        records = [
            SourceRecord.from_dict(item)
            for item in record_items
            if isinstance(item, dict)
        ]
        source_records.extend(records)

        meta = payload.get("meta", {})
        failures = meta.get("failures", [])
        if isinstance(failures, list):
            upstream_failures.extend(
                failure for failure in failures if isinstance(failure, dict)
            )

        input_summaries.append(
            {
                "path": str(path),
                "record_count": len(records),
                "upstream_failures": failures if isinstance(failures, list) else [],
            }
        )

    merged_records = merge_records(source_records)
    source_counts = Counter(record.source_site for record in source_records)

    return {
        "meta": {
            "generated_at": datetime.now(UTC).isoformat(),
            "input_files": [str(path) for path in input_paths],
            "source_record_count": len(source_records),
            "merged_record_count": len(merged_records),
            "source_counts": dict(source_counts.most_common()),
            "input_summaries": input_summaries,
            "upstream_failures": upstream_failures,
            "file_failures": file_failures,
        },
        "analytics": {
            "organization_type_counts": count_values(
                merged_records,
                "organization_type_guess",
            ),
            "sector_guess_counts": count_values(merged_records, "sector_guesses"),
            "stage_coverage_counts": count_values(
                merged_records,
                "stage_coverage_guess",
            ),
            "capability_counts": count_values(
                merged_records,
                "capability_guesses",
            ),
            "certification_counts": count_values(
                merged_records,
                "certification_guesses",
            ),
        },
        "source_records": [record.to_dict() for record in source_records],
        "merged_records": merged_records,
    }


def run() -> int:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    payload = build_combined_payload(args.inputs)
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(
        "Wrote "
        f"{payload['meta']['source_record_count']} source records and "
        f"{payload['meta']['merged_record_count']} merged records "
        f"to {args.output}"
    )
    return 1 if payload["meta"]["file_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(run())
