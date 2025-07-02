#!/usr/bin/env python3
"""
Validation script for JSON schema files and .infrahub.yml configuration files.
This script validates that:
1. All .json files are valid JSON and valid JSON schemas
2. All .infrahub.yml files are valid YAML and conform to the repository config schema
"""

import json
import sys
import glob
import os
from pathlib import Path
from typing import List, Tuple, Dict, Any

try:
    import jsonschema
    from jsonschema import Draft7Validator, Draft202012Validator
except ImportError:
    print("jsonschema package not found. Please install it with: pip install jsonschema")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("PyYAML package not found. Please install it with: pip install PyYAML")
    sys.exit(1)


def validate_json_file(file_path: str) -> Tuple[bool, str]:
    """Validate that a file contains valid JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True, ""
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"


def validate_json_schema(file_path: str) -> Tuple[bool, str]:
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


def validate_yaml_file(file_path: str) -> Tuple[bool, str, Dict[Any, Any]]:
    """Validate that a file contains valid YAML and return the parsed content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
        return True, "", content
    except yaml.YAMLError as e:
        return False, f"Invalid YAML: {e}", {}
    except Exception as e:
        return False, f"Error reading file: {e}", {}


def validate_infrahub_yml_against_schema(yml_content: Dict[Any, Any], schema_path: str) -> Tuple[bool, str]:
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


def find_latest_repository_config_schema() -> str:
    """Find the latest repository config schema file."""
    schema_dir = "schemas/python-sdk/repository-config"
    if not os.path.exists(schema_dir):
        return ""
    
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
    
    return ""


def main():
    """Main validation function."""
    repo_root = Path(__file__).parent
    os.chdir(repo_root)
    
    errors = []
    
    print("🔍 Validating JSON schema files...")
    
    # Find all JSON files
    json_files = glob.glob("**/*.json", recursive=True)
    
    for json_file in sorted(json_files):
        print(f"  Checking {json_file}...")
        
        # First validate it's valid JSON
        is_valid_json, json_error = validate_json_file(json_file)
        if not is_valid_json:
            errors.append(f"❌ {json_file}: {json_error}")
            continue
        
        # Then validate it's a valid JSON schema
        is_valid_schema, schema_error = validate_json_schema(json_file)
        if not is_valid_schema:
            errors.append(f"❌ {json_file}: {schema_error}")
        else:
            print(f"    ✅ Valid JSON schema")
    
    print(f"\n🔍 Validating .infrahub.yml files...")
    
    # Find all .infrahub.yml files
    infrahub_yml_files = []
    infrahub_yml_files.extend(glob.glob("**/.infrahub.yml", recursive=True))
    infrahub_yml_files.extend(glob.glob("**/infrahub.yml", recursive=True))
    infrahub_yml_files.extend(glob.glob("**/*.infrahub.yml", recursive=True))
    
    if not infrahub_yml_files:
        print("  No .infrahub.yml files found to validate")
    else:
        # Find the repository config schema
        repo_config_schema = find_latest_repository_config_schema()
        if not repo_config_schema:
            print("  ⚠️  Warning: Could not find repository config schema to validate .infrahub.yml files")
        else:
            print(f"  Using schema: {repo_config_schema}")
        
        for yml_file in sorted(infrahub_yml_files):
            print(f"  Checking {yml_file}...")
            
            # Validate YAML syntax
            is_valid_yaml, yaml_error, yml_content = validate_yaml_file(yml_file)
            if not is_valid_yaml:
                errors.append(f"❌ {yml_file}: {yaml_error}")
                continue
            
            # Validate against schema if available
            if repo_config_schema:
                is_valid_against_schema, schema_error = validate_infrahub_yml_against_schema(yml_content, repo_config_schema)
                if not is_valid_against_schema:
                    errors.append(f"❌ {yml_file}: {schema_error}")
                else:
                    print(f"    ✅ Valid against repository config schema")
            else:
                print(f"    ✅ Valid YAML (schema validation skipped)")
    
    # Report results
    print(f"\n📊 Validation Summary:")
    print(f"  JSON files checked: {len(json_files)}")
    print(f"  .infrahub.yml files checked: {len(infrahub_yml_files)}")
    
    if errors:
        print(f"\n❌ Found {len(errors)} validation errors:")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print(f"\n✅ All files passed validation!")
        sys.exit(0)


if __name__ == "__main__":
    main()