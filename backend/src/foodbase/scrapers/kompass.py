from __future__ import annotations

import cloudscraper
from bs4 import BeautifulSoup

from foodbase.scrapers.models import SourceRecord
from foodbase.scrapers.utils import (
    DEFAULT_HEADERS,
    attr_value_as_str,
    compact_text,
    infer_tags,
    split_product_text,
)

KOMPASS_URL = "https://gr.kompass.com/s/agriculture-food/01/"


class KompassScraper:
    source_site = "kompass"

    def __init__(self, page_limit: int = 1, delay_seconds: float = 0.2) -> None:
        self.page_limit = page_limit
        self.scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False},
            delay=delay_seconds,
        )
        self.scraper.headers.update(DEFAULT_HEADERS)

    def scrape(self) -> list[SourceRecord]:
        records: list[SourceRecord] = []

        for page_number in range(1, self.page_limit + 1):
            page_url = KOMPASS_URL if page_number == 1 else f"{KOMPASS_URL}?page={page_number}"
            response = self.scraper.get(page_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            company_anchors = soup.select("a[href*='/c/']")
            if not company_anchors:
                raise RuntimeError(
                    "Kompass returned no company anchors; likely blocked by anti-bot."
                )

            seen_urls: set[str] = set()
            for anchor in company_anchors:
                detail_url = attr_value_as_str(anchor.get("href"))
                company_name = compact_text(anchor.get_text(" ", strip=True))
                if not detail_url or not company_name or detail_url in seen_urls:
                    continue
                seen_urls.add(detail_url)

                card_text = compact_text(
                    anchor.parent.get_text(" ", strip=True) if anchor.parent else None
                )
                record = SourceRecord(
                    source_site=self.source_site,
                    source_sections=["agriculture_food"],
                    listing_url=page_url,
                    detail_url=detail_url,
                    company_name=company_name,
                    category="agriculture_food",
                    description=card_text,
                    products_or_services=split_product_text(card_text),
                    raw={"listing_excerpt": card_text},
                )
                infer_tags(record)
                records.append(record)

        return records
