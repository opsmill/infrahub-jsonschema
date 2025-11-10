"""
Pytest-based validation tests for JSON schema files.
This test suite validates that all .json files are valid JSON and valid JSON schemas.
"""

import glob
import json
from dataclasses import dataclass
from pathlib import Path

import jsonschema
import pytest
from jsonschema import Draft7Validator, Draft202012Validator

REPO_ROOT = Path(__file__).parent.parent
ALL_JSON_FILES = sorted(glob.glob(str(REPO_ROOT / "**" / "*.json"), recursive=True))


@dataclass
class JsonTestCase:
    name: str
    file_path: Path


ALL_JSON_TEST_CASES = [
    JsonTestCase(name=json_file, file_path=Path(json_file))
    for json_file in ALL_JSON_FILES
]


@pytest.mark.parametrize(
    "test_case",
    [pytest.param(tc, id=tc.name) for tc in ALL_JSON_TEST_CASES],
)
def test_collect_and_validate_all_json_files(test_case: JsonTestCase) -> None:
    """Collect and validate all JSON files at once for better reporting."""

    with open(test_case.file_path, "r", encoding="utf-8") as f:
        json.load(f)


@pytest.mark.parametrize(
    "test_case",
    [pytest.param(tc, id=tc.name) for tc in ALL_JSON_TEST_CASES],
)
def test_collect_and_validate_all_json_schema_files(test_case: JsonTestCase) -> None:
    """Collect and validate all JSON files at once for better reporting."""

    with open(test_case.file_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    # Try to create a validator - this will fail if it's not a valid schema
    # First try Draft 2020-12, then fall back to Draft 7
    try:
        Draft202012Validator.check_schema(schema)
    except jsonschema.SchemaError:
        Draft7Validator.check_schema(schema)
