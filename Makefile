
test: FORCE
	python setup.py test

build: FORCE
	python setup.py build

develop: FORCE
	python setup.py develop

dev-setup: FORCE
	pip install pluggy sphinx toml towncrier py

changelog: FORCE
	towncrier

html: FORCE
	python setup.py build_sphinx

FORCE:
