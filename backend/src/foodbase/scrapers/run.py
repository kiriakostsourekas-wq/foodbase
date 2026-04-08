from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from foodbase.scrapers.greekexporters import GreekExportersScraper
from foodbase.scrapers.kompass import KompassScraper
from foodbase.scrapers.madeingreece import MadeInGreeceScraper
from foodbase.scrapers.models import SourceRecord
from foodbase.scrapers.utils import HtmlFetcher, merge_records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape supplier discovery sources for Foodbase.")
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=["madeingreece", "greekexporters", "kompass"],
        default=["madeingreece", "greekexporters", "kompass"],
        help="Sources to scrape.",
    )
    parser.add_argument(
        "--greekexporters-page-limit",
        type=int,
        default=1,
        help="Number of pages to scrape per Greek Exporters category.",
    )
    parser.add_argument(
        "--kompass-page-limit",
        type=int,
        default=1,
        help="Number of Kompass pages to attempt.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/scrapes/greek-food-sources.json"),
        help="Output file path.",
    )
    return parser.parse_args()


def run() -> int:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    fetcher = HtmlFetcher()
    records: list[SourceRecord] = []
    failures: list[dict[str, str]] = []

    scraper_factories: dict[str, Callable[[], Any]] = {
        "madeingreece": lambda: MadeInGreeceScraper(fetcher),
        "greekexporters": lambda: GreekExportersScraper(
            fetcher,
            page_limit=args.greekexporters_page_limit,
        ),
        "kompass": lambda: KompassScraper(page_limit=args.kompass_page_limit),
    }

    try:
        for source_name in args.sources:
            scraper = scraper_factories[source_name]()
            try:
                source_records = scraper.scrape()
                records.extend(source_records)
            except Exception as exc:  # noqa: BLE001
                failures.append(
                    {
                        "source": source_name,
                        "error": str(exc),
                    }
                )
    finally:
        fetcher.close()

    merged_records = merge_records(records)
    payload = {
        "meta": {
            "generated_at": datetime.now(UTC).isoformat(),
            "record_count": len(records),
            "merged_record_count": len(merged_records),
            "failures": failures,
        },
        "source_records": [record.to_dict() for record in records],
        "merged_records": merged_records,
    }

    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote {len(records)} source records to {args.output}")
    if failures:
        print(f"Encountered {len(failures)} source failures.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
