import json, pathlib
from jsonschema import validate, ValidationError

SCHEMA_PATH = pathlib.Path("prompts/seven_panel_schema.json")

def parse_and_validate(raw: str) -> list[dict]:
    try:
        data = json.loads(raw)
    except Exception as e:
        raise ValueError(f"LLM returned non-JSON: {e}")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        validate(data, schema)
    except ValidationError as e:
        raise ValueError(f"Schema validation failed: {e.message}")
    return data