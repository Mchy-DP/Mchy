import json


def json_dump(object: dict) -> str:
    return json.dumps(object, indent=2)
