import json, os
SPEC = json.load(open(os.environ.get("SPEC", "spec.json")))
BEATS = SPEC["beats"]
HEADER = SPEC["header"]
