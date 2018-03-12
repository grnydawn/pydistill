

dev-setup: FORCE
	pip install pluggy sphinx toml towncrier py

changelog: FORCE
	towncrier

html: FORCE
	python setup.py build_sphinx

FORCE:
