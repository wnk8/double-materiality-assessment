"""Tests for src/data_loader.py"""
import os
import pytest
from openpyxl import Workbook
from src.data_loader import load_iros
from src.exceptions import InvalidScoreError, MissingIROError

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ALL_IRO_IDS = [
    "E1-I1", "E1-I2", "E1-R1", "E1-O1",
    "E2-I1", "E2-R1", "E2-O1",
    "E3-I1", "E3-R1", "E3-O1",
    "S1-I1", "S1-I2", "S1-R1",
    "S2-I1", "S2-R1", "S2-O1",
    "G1-I1", "G1-R1", "G1-O1",
    "G2-I1", "G2-R1",
]

TOPIC_MAP = {
    "E1-I1": "E1", "E1-I2": "E1", "E1-R1": "E1", "E1-O1": "E1",
    "E2-I1": "E2", "E2-R1": "E2", "E2-O1": "E2",
    "E3-I1": "E3", "E3-R1": "E3", "E3-O1": "E3",
    "S1-I1": "S1", "S1-I2": "S1", "S1-R1": "S1",
    "S2-I1": "S2", "S2-R1": "S2", "S2-O1": "S2",
    "G1-I1": "G1", "G1-R1": "G1", "G1-O1": "G1",
    "G2-I1": "G2", "G2-R1": "G2",
}

TYPE_MAP = {
    "E1-I1": "Impact", "E1-I2": "Impact", "E1-R1": "Risk", "E1-O1": "Opportunity",
    "E2-I1": "Impact", "E2-R1": "Risk", "E2-O1": "Opportunity",
    "E3-I1": "Impact", "E3-R1": "Risk", "E3-O1": "Opportunity",
    "S1-I1": "Impact", "S1-I2": "Impact", "S1-R1": "Risk",
    "S2-I1": "Impact", "S2-R1": "Risk", "S2-O1": "Opportunity",
    "G1-I1": "Impact", "G1-R1": "Risk", "G1-O1": "Opportunity",
    "G2-I1": "Impact", "G2-R1": "Risk",
}


def _make_xlsx(tmp_path, iro_rows: list[tuple], sheet_name="IRO_Eingabe") -> str:
    """Build a minimal valid .xlsx with the given data rows and return its path."""
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    headers = [
        "IRO-ID", "ESRS-Thema", "IRO-Typ", "Beschreibung",
        "Ausmaß\n(1–5)", "Reichweite\n(1–5)", "Behebbarkeit\n(1–5)",
        "Eintritts-\nwahrsch.\n(1–5)", "Fin. Auswirkung\n(1–5)", "Zeithorizont"
    ]
    ws.append(headers)
    for row in iro_rows:
        ws.append(list(row))

    path = str(tmp_path / "test_template.xlsx")
    wb.save(path)
    return path


def _valid_rows(overrides: dict = None) -> list[tuple]:
    """Return a full set of 21 valid rows, with optional per-iro_id overrides."""
    overrides = overrides or {}
    rows = []
    for iro_id in ALL_IRO_IDS:
        default = (
            iro_id, TOPIC_MAP[iro_id], TYPE_MAP[iro_id], "Test description",
            3, 3, 3, 3, 3, "medium"
        )
        rows.append(overrides.get(iro_id, default))
    return rows


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestValidLoad:
    def test_returns_correct_count(self, tmp_path):
        path = _make_xlsx(tmp_path, _valid_rows())
        result = load_iros(path)
        assert len(result) == len(ALL_IRO_IDS)

    def test_all_iro_ids_present(self, tmp_path):
        path = _make_xlsx(tmp_path, _valid_rows())
        result = load_iros(path)
        ids = [r["iro_id"] for r in result]
        for expected_id in ALL_IRO_IDS:
            assert expected_id in ids

    def test_scores_are_integers(self, tmp_path):
        path = _make_xlsx(tmp_path, _valid_rows())
        result = load_iros(path)
        for iro in result:
            for field in ("magnitude", "scope", "irremediability", "likelihood", "fin_magnitude"):
                assert isinstance(iro[field], int)

    def test_time_horizon_normalised_to_lowercase(self, tmp_path):
        rows = _valid_rows({"E1-I1": ("E1-I1", "E1", "Impact", "Desc", 3, 3, 3, 3, 3, "Short")})
        path = _make_xlsx(tmp_path, rows)
        result = load_iros(path)
        e1i1 = next(r for r in result if r["iro_id"] == "E1-I1")
        assert e1i1["time_horizon"] == "short"


class TestFileErrors:
    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_iros(str(tmp_path / "nonexistent.xlsx"))

    def test_wrong_sheet_name_raises(self, tmp_path):
        path = _make_xlsx(tmp_path, _valid_rows(), sheet_name="WrongSheet")
        with pytest.raises(ValueError, match="IRO_Eingabe"):
            load_iros(path)


class TestScoreValidation:
    def test_score_zero_raises(self, tmp_path):
        rows = _valid_rows({"E1-I1": ("E1-I1", "E1", "Impact", "Desc", 0, 3, 3, 3, 3, "medium")})
        path = _make_xlsx(tmp_path, rows)
        with pytest.raises(InvalidScoreError) as exc_info:
            load_iros(path)
        assert exc_info.value.iro_id == "E1-I1"
        assert exc_info.value.field == "magnitude"

    def test_score_six_raises(self, tmp_path):
        rows = _valid_rows({"E2-I1": ("E2-I1", "E2", "Impact", "Desc", 3, 6, 3, 3, 3, "medium")})
        path = _make_xlsx(tmp_path, rows)
        with pytest.raises(InvalidScoreError) as exc_info:
            load_iros(path)
        assert exc_info.value.iro_id == "E2-I1"
        assert exc_info.value.field == "scope"

    def test_non_numeric_score_raises(self, tmp_path):
        rows = _valid_rows({"E1-R1": ("E1-R1", "E1", "Risk", "Desc", "hoch", 3, 3, 3, 3, "medium")})
        path = _make_xlsx(tmp_path, rows)
        with pytest.raises(InvalidScoreError):
            load_iros(path)

    def test_invalid_horizon_raises(self, tmp_path):
        rows = _valid_rows({"S1-I1": ("S1-I1", "S1", "Impact", "Desc", 3, 3, 3, 3, 3, "quarterly")})
        path = _make_xlsx(tmp_path, rows)
        with pytest.raises(InvalidScoreError) as exc_info:
            load_iros(path)
        assert exc_info.value.field == "time_horizon"


class TestMissingIRO:
    def test_missing_row_raises(self, tmp_path):
        rows = [r for r in _valid_rows() if r[0] != "G2-R1"]
        path = _make_xlsx(tmp_path, rows)
        with pytest.raises(MissingIROError) as exc_info:
            load_iros(path)
        assert exc_info.value.iro_id == "G2-R1"
