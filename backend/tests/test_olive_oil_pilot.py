from foodbase.intake.olive_oil_pilot import build_pilot_records


def test_build_pilot_records_generates_twenty_olive_oil_profiles() -> None:
    records = build_pilot_records()

    assert len(records) == 20
    assert all(record["offerings"][0]["product_category_slug"] == "olive-oil" for record in records)
    assert all(record["company"]["headquarters_region"] for record in records)
