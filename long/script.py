import json, os
_S = json.load(open(os.environ.get("LSPEC", "long_spec.json")))
TITLE = _S["title"]; SLIDES = _S["slides"]; THUMB = _S.get("thumb", {})
