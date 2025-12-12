"""
Pytest-based validation tests for JSON schema files.
This test suite validates that all .json files are valid JSON and valid JSON schemas.
"""

import glob
import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import jsonschema
import pytest
from jsonschema import Draft7Validator, Draft202012Validator

REPO_ROOT = Path(__file__).parent.parent
ALL_JSON_FILES = sorted(glob.glob(str(REPO_ROOT / "**" / "*.json"), recursive=True))


class SchemaSection(StrEnum):
    PYTHON_SDK = "python-sdk"
    INFRAHUB = "infrahub"
    DEVELOP = "develop"
    VERSIONS = "versions"

    @property
    def has_schema_dir(self) -> bool:
        return self in {
            SchemaSection.PYTHON_SDK,
            SchemaSection.INFRAHUB,
            SchemaSection.VERSIONS,
        }


@dataclass
class JsonTestCase:
    file_path: Path

    @property
    def file_name(self) -> str:
        return self.file_path.name

    @property
    def version(self) -> str:
        return self.file_path.stem

    @property
    def name(self) -> str:
        return f"{self.section}/{self.schema_type}{self.version}"

    @property
    def relative_path(self) -> Path:
        return self.file_path.relative_to(REPO_ROOT)

    @property
    def relative_dir(self) -> Path:
        return self.relative_path.parent

    @property
    def section(self) -> SchemaSection:
        return SchemaSection(self.sections[0])

    @property
    def schema_type(self) -> str:
        if self.section.has_schema_dir:
            return f"{self.sections[1]}/"
        return ""

    @property
    def sections(self) -> list[str]:
        section_parts = self.relative_dir.parts
        assert section_parts[0] == "schemas", (
            "Expected JSON files to be under 'schemas/' directory"
        )
        return list(section_parts[1:])


ALL_JSON_TEST_CASES = [
    JsonTestCase(file_path=Path(json_file)) for json_file in ALL_JSON_FILES
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
