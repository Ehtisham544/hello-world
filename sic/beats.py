import json, os
SPEC = json.load(open(os.environ.get("SPEC", "spec.json")))
BEATS = SPEC["beats"]
HEADER = SPEC["header"]
from styles import STYLES
STYLE = STYLES[int(SPEC.get("style", 0)) % len(STYLES)]
