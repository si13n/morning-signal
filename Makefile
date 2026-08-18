.PHONY: test generate render serve validate

test:
	python3 -m pytest

generate:
	python3 scripts/generate_digest.py
	python3 scripts/render.py

render:
	python3 scripts/render.py

validate:
	python3 scripts/validate.py

serve:
	python3 -m http.server 8000
