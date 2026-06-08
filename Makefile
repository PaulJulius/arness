.PHONY: test validate

test: validate

validate:
	python3 tools/validate_arness.py
