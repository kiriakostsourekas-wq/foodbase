from dataclasses import dataclass
from pathlib import Path

from foodbase.intake.importer import (
    ImportStats,
    IntakeImporter,
    load_intake_profiles,
    normalize_host,
)


@dataclass
class ScalarResult:
    value: int | None

    def scalar_one_or_none(self) -> int | None:
        return self.value

    def scalar_one(self) -> int:
        assert self.value is not None
        return self.value


class MatchSession:
    def __init__(self, *, host_match: int | None = None) -> None:
        self.host_match = host_match

    def execute(self, statement, params):  # type: ignore[no-untyped-def]
        sql = str(statement)
        if "where website_host = :website_host" in sql:
            return ScalarResult(self.host_match)
        return ScalarResult(None)


class RecordingSession:
    def __init__(self) -> None:
        self.ingestion_runs = 0
        self.committed = False

    def execute(self, statement, params):  # type: ignore[no-untyped-def]
        sql = str(statement)
        if "insert into ingestion_runs" in sql:
            self.ingestion_runs += 1
        return ScalarResult(1)

    def commit(self) -> None:
        self.committed = True


def test_match_prefers_website_host_before_slug() -> None:
    profile = load_intake_profiles(
        Path("data/pilots/olive-oil-pilot.intake.json")
    )[0]
    importer = IntakeImporter(MatchSession(host_match=42))

    match = importer._match_organization(profile)

    assert match.organization_id == 42
    assert match.rule == "website_host"


def test_import_profiles_updates_when_existing_host_match_found(monkeypatch) -> None:
    session = RecordingSession()
    importer = IntakeImporter(session)  # type: ignore[arg-type]
    profile = load_intake_profiles(Path("data/pilots/olive-oil-pilot.intake.json"))[0]

    monkeypatch.setattr(
        importer,
        "_import_profile",
        lambda incoming_profile: (1, False, "website_host"),
    )

    stats = importer.import_profiles([profile])

    assert isinstance(stats, ImportStats)
    assert stats.created == 0
    assert stats.updated == 1
    assert stats.matched_by_rule == {"website_host": 1}
    assert session.ingestion_runs == 1
    assert session.committed is True


def test_normalize_host_strips_www_prefix() -> None:
    assert normalize_host("https://www.example.com/path") == "example.com"
