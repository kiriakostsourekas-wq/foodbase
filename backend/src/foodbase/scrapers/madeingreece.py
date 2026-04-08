from __future__ import annotations

from bs4 import BeautifulSoup

from foodbase.scrapers.models import SourceRecord
from foodbase.scrapers.utils import (
    HtmlFetcher,
    attr_value_as_str,
    compact_text,
    infer_tags,
    normalize_url,
)

MADE_IN_GREECE_URL = "https://madeingreece.com/food-companies/"


class MadeInGreeceScraper:
    source_site = "madeingreece"

    def __init__(self, fetcher: HtmlFetcher) -> None:
        self.fetcher = fetcher

    def scrape(self) -> list[SourceRecord]:
        html = self.fetcher.get(MADE_IN_GREECE_URL)
        soup = BeautifulSoup(html, "lxml")
        table = soup.select_one("#pinkasall")
        if table is None:
            raise RuntimeError("Could not find company table on madeingreece.")

        records: list[SourceRecord] = []
        for row in table.select("tbody tr"):
            cells = row.select("td")
            if len(cells) < 8:
                continue

            website_anchor = cells[4].select_one("a")
            email_anchor = cells[7].select_one("a[href^='mailto:']")
            company_name = compact_text(cells[0].get_text(" ", strip=True)) or "Unknown company"
            brand_name = compact_text(cells[1].get_text(" ", strip=True))
            category = compact_text(cells[2].get_text(" ", strip=True))
            subcategory = compact_text(cells[3].get_text(" ", strip=True))
            website_href = (
                attr_value_as_str(website_anchor.get("href")) if website_anchor else None
            )
            email_href = (
                attr_value_as_str(email_anchor.get("href")) if email_anchor else None
            )
            email = compact_text(email_href.removeprefix("mailto:") if email_href else None)

            record = SourceRecord(
                source_site=self.source_site,
                source_sections=[subcategory or "Food"],
                listing_url=MADE_IN_GREECE_URL,
                detail_url=None,
                company_name=company_name,
                brand_name=brand_name,
                website_url=normalize_url(MADE_IN_GREECE_URL, website_href),
                phone=compact_text(cells[5].get_text(" ", strip=True)),
                email=email,
                location=compact_text(cells[6].get_text(" ", strip=True)),
                category=category,
                subcategory=subcategory,
                description=None,
                products_or_services=[],
                raw={
                    "company": company_name,
                    "brand": brand_name,
                    "category": category,
                    "subcategory": subcategory,
                },
            )
            infer_tags(record)
            records.append(record)

        return records
