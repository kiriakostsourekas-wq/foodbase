from __future__ import annotations

from bs4 import BeautifulSoup
from bs4.element import Tag

from foodbase.scrapers.models import SourceRecord
from foodbase.scrapers.utils import (
    HtmlFetcher,
    attr_value_as_str,
    compact_text,
    infer_tags,
    normalize_list,
    normalize_url,
    split_product_text,
    tag_text,
)

BASE_URL = "http://www.greekexporters.gr/"

FOOD_CATEGORY_URLS = {
    "agricultural_food_beverages": "http://www.greekexporters.gr/1/categories/agricultural-food--beverages.html",
    "food_products": "http://www.greekexporters.gr/28/categories/.html",
    "bakery_confectionery": "http://www.greekexporters.gr/130/categories/bakery--confectionery.html",
    "dairy_cheese": "http://www.greekexporters.gr/109/categories/dairy--cheese-products.html",
    "olive_oil_olives_pickles": "http://www.greekexporters.gr/108/categories/olive-oil-olives-pickles.html",
    "organic_health_foods": "http://www.greekexporters.gr/149/categories/organic--health-foods.html",
    "fish_seafood": "http://www.greekexporters.gr/111/categories/fish--seafood.html",
    "flour_legume_rice_pasta": "http://www.greekexporters.gr/193/categories/flour-legume-rice-pasta.html",
    "frozen_preparations": "http://www.greekexporters.gr/143/categories/frozen--preparations.html",
    "fruits_vegetables": "http://www.greekexporters.gr/110/categories/fruits--vegetables.html",
    "herbs_spices_nuts_snacks": "http://www.greekexporters.gr/148/categories/herbs-spices-nuts-snacks.html",
    "honey_royal_jelly": "http://www.greekexporters.gr/134/categories/honey--royal-jelly.html",
    "meat_poultry_fine_products": "http://www.greekexporters.gr/129/categories/meat--poultry-fine-products.html",
    "superfoods_nutrition_products": "http://www.greekexporters.gr/168/categories/superfoods-nutrition-products.html",
}


class GreekExportersScraper:
    source_site = "greekexporters"

    def __init__(self, fetcher: HtmlFetcher, page_limit: int = 1) -> None:
        self.fetcher = fetcher
        self.page_limit = page_limit

    def scrape(self) -> list[SourceRecord]:
        records_by_detail_url: dict[str, SourceRecord] = {}

        for section_name, category_url in FOOD_CATEGORY_URLS.items():
            for page_number in range(1, self.page_limit + 1):
                page_url = category_url if page_number == 1 else f"{category_url}/{page_number}"
                html = self.fetcher.get(page_url)
                soup = BeautifulSoup(html, "lxml")

                for result in soup.select("div.resDet"):
                    title_anchor = result.select_one("h3.resTitle a")
                    if title_anchor is None:
                        continue

                    detail_url = normalize_url(
                        BASE_URL,
                        attr_value_as_str(title_anchor.get("href")),
                    )
                    if detail_url is None:
                        continue

                    description = tag_text(result.select_one("p.resCont"))

                    if detail_url not in records_by_detail_url:
                        record = self._scrape_detail_page(
                            detail_url=detail_url,
                            listing_url=page_url,
                            company_name=compact_text(title_anchor.get_text(" ", strip=True))
                            or "Unknown company",
                            category=section_name,
                            category_description=description,
                        )
                        records_by_detail_url[detail_url] = record

                    existing = records_by_detail_url[detail_url]
                    existing.source_sections = sorted(
                        set(existing.source_sections).union({section_name})
                    )
                    if description:
                        existing.products_or_services = sorted(
                            set(existing.products_or_services).union(split_product_text(description))
                        )
                        if not existing.description:
                            existing.description = description
                    infer_tags(existing)

        return sorted(records_by_detail_url.values(), key=lambda item: item.company_name)

    def _scrape_detail_page(
        self,
        *,
        detail_url: str,
        listing_url: str,
        company_name: str,
        category: str,
        category_description: str | None,
    ) -> SourceRecord:
        html = self.fetcher.get(detail_url)
        soup = BeautifulSoup(html, "lxml")

        address_block = soup.select_one("#address")
        contact_block = soup.select_one("#contact")
        profile_box = self._get_box_content(soup, "COMPANY PROFILE")
        products_box = self._get_box_content(soup, "PRODUCTS / SERVICES")
        business_opportunities_box = self._get_box_content(soup, "BUSINESS OPPORTUNITIES")

        website_url = None
        phone = None
        fax = None
        if contact_block:
            website_anchor = contact_block.select_one("a#curl")
            website_url = normalize_url(
                BASE_URL,
                attr_value_as_str(website_anchor.get("href")) if website_anchor else None,
            )
            for info_box in contact_block.select("div.box3"):
                label = tag_text(info_box.select_one("div.lefttitle3"))
                value = tag_text(info_box.select_one("div.boxcontent3"))
                if label == "telephone:":
                    phone = value
                if label == "fax:":
                    fax = value

        address = None
        location = None
        if address_block:
            address_lines = normalize_list(
                compact_text(line)
                for line in address_block.stripped_strings
                if compact_text(line) and compact_text(line) != company_name
            )
            if address_lines:
                address = ", ".join(address_lines)
                location = address_lines[-2] if len(address_lines) >= 2 else address_lines[-1]

        notes: list[str] = []
        if business_opportunities_box:
            opportunities_text = compact_text(business_opportunities_box.get_text(" ", strip=True))
            if opportunities_text:
                notes.append(opportunities_text)

        record = SourceRecord(
            source_site=self.source_site,
            source_sections=[category],
            listing_url=listing_url,
            detail_url=detail_url,
            company_name=company_name,
            website_url=website_url,
            phone=phone,
            fax=fax,
            location=location,
            address=address,
            category=None,
            description=compact_text(
                tag_text(products_box) if products_box else category_description
            ),
            products_or_services=split_product_text(
                tag_text(products_box) if products_box else category_description
            ),
            notes=notes,
            raw={
                "directory_section": category,
                "directory_description": category_description,
                "profile_text": tag_text(profile_box),
                "products_text": tag_text(products_box),
                "business_opportunities_text": notes[0] if notes else None,
            },
        )
        infer_tags(record)
        return record

    @staticmethod
    def _get_box_content(soup: BeautifulSoup, title: str) -> Tag | None:
        for box in soup.select("div.box"):
            title_node = box.select_one("div.lefttitle")
            if title_node and compact_text(title_node.get_text(" ", strip=True)) == title:
                return box.select_one("div.boxcontent")
        return None
