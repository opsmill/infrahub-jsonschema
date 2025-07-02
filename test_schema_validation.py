#!/usr/bin/env python3
"""
Pytest-based validation tests for JSON schema files and .infrahub.yml configuration files.
This test suite validates that:
1. All .json files are valid JSON and valid JSON schemas
2. All .infrahub.yml files are valid YAML and conform to the repository config schema
"""

import json
import glob
import os
from pathlib import Path
from typing import List, Tuple, Dict, Any

import pytest
import jsonschema
from jsonschema import Draft7Validator, Draft202012Validator
import yaml


class TestSchemaValidation:
    """Test class for validating JSON schemas and YAML configuration files."""

    @pytest.fixture(scope="class")
    def repo_root(self):
        """Get the repository root directory."""
        return Path(__file__).parent

    @pytest.fixture(scope="class")
    def json_files(self, repo_root):
        """Get all JSON files in the repository."""
        os.chdir(repo_root)
        return sorted(glob.glob("**/*.json", recursive=True))

    @pytest.fixture(scope="class")
    def infrahub_yml_files(self, repo_root):
        """Get all .infrahub.yml files in the repository."""
        os.chdir(repo_root)
        files = []
        files.extend(glob.glob("**/.infrahub.yml", recursive=True))
        files.extend(glob.glob("**/infrahub.yml", recursive=True))
        files.extend(glob.glob("**/*.infrahub.yml", recursive=True))
        return sorted(files)

    @pytest.fixture(scope="class")
    def repository_config_schema_path(self, repo_root):
        """Find the latest repository config schema file."""
        os.chdir(repo_root)
        schema_dir = "schemas/python-sdk/repository-config"
        if not os.path.exists(schema_dir):
            return None
        
        # Look for develop.json first, then latest.json, then the highest version
        develop_path = os.path.join(schema_dir, "develop.json")
        if os.path.exists(develop_path):
            return develop_path
        
        latest_path = os.path.join(schema_dir, "latest.json")
        if os.path.exists(latest_path):
            return latest_path
        
        # Find the highest version number
        version_files = glob.glob(os.path.join(schema_dir, "*.json"))
        if version_files:
            return sorted(version_files)[-1]  # Last in alphabetical order should be highest version
        
        return None

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

    def validate_yaml_file(self, file_path: str) -> Tuple[bool, str, Dict[Any, Any]]:
        """Validate that a file contains valid YAML and return the parsed content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            return True, "", content
        except yaml.YAMLError as e:
            return False, f"Invalid YAML: {e}", {}
        except Exception as e:
            return False, f"Error reading file: {e}", {}

    def validate_infrahub_yml_against_schema(self, yml_content: Dict[Any, Any], schema_path: str) -> Tuple[bool, str]:
        """Validate .infrahub.yml content against the repository config schema."""
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            validator = Draft202012Validator(schema)
            if not validator.is_valid(yml_content):
                errors = list(validator.iter_errors(yml_content))
                error_messages = [f"  - {error.message} at {'.'.join(str(x) for x in error.absolute_path)}" for error in errors]
                return False, f"Schema validation failed:\n" + "\n".join(error_messages)
            
            return True, ""
        except Exception as e:
            return False, f"Error validating against schema: {e}"

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

    def test_collect_and_validate_all_infrahub_yml_files(self, infrahub_yml_files, repository_config_schema_path):
        """Collect and validate all .infrahub.yml files at once for better reporting."""
        if not infrahub_yml_files:
            pytest.skip("No .infrahub.yml files found to validate")
        
        errors = []
        
        for yml_file in infrahub_yml_files:
            # Test YAML syntax
            is_valid_yaml, yaml_error, yml_content = self.validate_yaml_file(yml_file)
            if not is_valid_yaml:
                errors.append(f"❌ {yml_file}: {yaml_error}")
                continue
            
            # Test schema compliance if schema is available
            if repository_config_schema_path:
                is_valid_schema, schema_error = self.validate_infrahub_yml_against_schema(yml_content, repository_config_schema_path)
                if not is_valid_schema:
                    errors.append(f"❌ {yml_file}: {schema_error}")
        
        if errors:
            error_msg = f"Found {len(errors)} YAML validation errors:\n" + "\n".join(errors)
            pytest.fail(error_msg)
        
        schema_msg = f" (validated against {repository_config_schema_path})" if repository_config_schema_path else " (syntax only)"
        print(f"✅ All {len(infrahub_yml_files)} .infrahub.yml files passed validation{schema_msg}!")