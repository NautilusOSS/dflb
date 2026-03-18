# Development / CI helpers. Run from repo root.

.PHONY: test test-py format format-check black black-check

test: test-py
test-py:
	python3 -m pytest tests/ -v

format: black-check format-js
format-check: black-check format-js-check

black:
	black src/
black-check:
	black --check src/

format-js:
	cd src/dashboard && npm run format 2>/dev/null || true
format-js-check:
	cd src/dashboard && npm run format:check 2>/dev/null || true
