#!/usr/bin/env python3
"""
Pytest-based validation tests for JSON schema files.
This test suite validates that all .json files are valid JSON and valid JSON schemas.
"""

import json
import glob
import os
from pathlib import Path
from typing import Tuple

import pytest
import jsonschema
from jsonschema import Draft7Validator, Draft202012Validator


class TestSchemaValidation:
    """Test class for validating JSON schemas."""

    @pytest.fixture(scope="class")
    def repo_root(self):
        """Get the repository root directory."""
        return Path(__file__).parent.parent

    @pytest.fixture(scope="class")
    def json_files(self, repo_root):
        """Get all JSON files in the repository."""
        os.chdir(repo_root)
        return sorted(glob.glob("**/*.json", recursive=True))

    def validate_json_file(self, file_path: str) -> Tuple[bool, str]:
        """Validate that a file contains valid JSON."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True, ""
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"
        except Exception as e:
            return False, f"Error reading file: {e}"

    def validate_json_schema(self, file_path: str) -> Tuple[bool, str]:
        """Validate that a JSON file is a valid JSON schema."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            # Try to create a validator - this will fail if it's not a valid schema
            # First try Draft 2020-12, then fall back to Draft 7
            try:
                Draft202012Validator.check_schema(schema)
            except jsonschema.SchemaError:
                try:
                    Draft7Validator.check_schema(schema)
                except jsonschema.SchemaError as e:
                    return False, f"Invalid JSON schema: {e}"
            
            return True, ""
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"
        except Exception as e:
            return False, f"Error validating schema: {e}"

    def test_collect_and_validate_all_json_files(self, json_files):
        """Collect and validate all JSON files at once for better reporting."""
        if not json_files:
            pytest.skip("No JSON files found to validate")
        
        errors = []
        
        for json_file in json_files:
            # Test JSON syntax
            is_valid_json, json_error = self.validate_json_file(json_file)
            if not is_valid_json:
                errors.append(f"❌ {json_file}: {json_error}")
                continue
            
            # Test JSON schema validity
            is_valid_schema, schema_error = self.validate_json_schema(json_file)
            if not is_valid_schema:
                errors.append(f"❌ {json_file}: {schema_error}")
        
        if errors:
            error_msg = f"Found {len(errors)} JSON validation errors:\n" + "\n".join(errors)
            pytest.fail(error_msg)
        
        print(f"✅ All {len(json_files)} JSON files passed validation!")