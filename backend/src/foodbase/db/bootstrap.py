import argparse
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from foodbase.db.health import check_database_health
from foodbase.db.reference_data import (
    CERTIFICATIONS,
    GREEK_REGIONS,
    OLIVE_OIL_GIS,
    PRODUCT_CATEGORIES,
)
from foodbase.db.session import get_engine, get_session_factory

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = REPO_ROOT / "db" / "schema.sql"


def apply_schema(schema_path: Path = SCHEMA_PATH) -> None:
    raw_connection = get_engine().raw_connection()
    try:
        with schema_path.open("r", encoding="utf-8") as handle:
            sql_text = handle.read()

        cursor = raw_connection.cursor()
        try:
            cursor.execute(sql_text)
        finally:
            cursor.close()

        raw_connection.commit()
    finally:
        raw_connection.close()


def seed_reference_data() -> None:
    session_factory = get_session_factory()
    with session_factory() as session:
        _seed_regions(session)
        _seed_product_categories(session)
        _seed_certifications(session)
        _seed_olive_oil_gis(session)
        session.commit()


def _seed_regions(session: Session) -> None:
    statement = text(
        """
        insert into geographic_regions (
          country_code,
          slug,
          name,
          region_level,
          center_latitude,
          center_longitude
        )
        values (
          :country_code,
          :slug,
          :name,
          :region_level,
          :center_latitude,
          :center_longitude
        )
        on conflict (slug) do update
        set
          name = excluded.name,
          region_level = excluded.region_level,
          center_latitude = excluded.center_latitude,
          center_longitude = excluded.center_longitude
        """
    )
    for region in GREEK_REGIONS:
        session.execute(statement, region)


def _seed_product_categories(session: Session) -> None:
    insert_statement = text(
        """
        insert into product_categories (parent_id, slug, name, category_type)
        values (
          (
            select id from product_categories
            where slug = :parent_slug
          ),
          :slug,
          :name,
          :category_type
        )
        on conflict (slug) do update
        set
          parent_id = excluded.parent_id,
          name = excluded.name,
          category_type = excluded.category_type
        """
    )
    for category in PRODUCT_CATEGORIES:
        session.execute(insert_statement, category)


def _seed_certifications(session: Session) -> None:
    statement = text(
        """
        insert into certifications (name, certification_type, issuing_body)
        values (:name, :certification_type, :issuing_body)
        on conflict (name) do update
        set
          certification_type = excluded.certification_type,
          issuing_body = excluded.issuing_body
        """
    )
    for certification in CERTIFICATIONS:
        session.execute(statement, certification)


def _seed_olive_oil_gis(session: Session) -> None:
    statement = text(
        """
        insert into geographical_indications (
          name,
          designation_type,
          product_category,
          source_registry,
          registry_url,
          specification_url
        )
        values (
          :name,
          :designation_type,
          :product_category,
          :source_registry,
          :registry_url,
          :specification_url
        )
        on conflict (country_code, name, designation_type) do update
        set
          product_category = excluded.product_category,
          source_registry = excluded.source_registry,
          registry_url = excluded.registry_url,
          specification_url = excluded.specification_url
        """
    )
    for gi_definition in OLIVE_OIL_GIS:
        session.execute(statement, gi_definition)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply the Foodbase schema and seed reference data."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only test the database connection and do not mutate the database.",
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Apply db/schema.sql without seeding reference data.",
    )
    args = parser.parse_args()

    is_healthy, error_message = check_database_health()
    if not is_healthy:
        raise SystemExit(error_message or "Database connection failed.")

    if args.check:
        print("database: ok")
        return

    apply_schema()
    if not args.schema_only:
        seed_reference_data()

    print("database: ok")
    print("schema: applied")
    if args.schema_only:
        print("reference_data: skipped")
    else:
        print("reference_data: seeded")


if __name__ == "__main__":
    main()
