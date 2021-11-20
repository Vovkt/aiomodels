
install:
	python -m pip install -e .

install-dev:
	python -m pip install -e .[dev]

black:
	python -m black setup.py aiomodel tests

mypy:
	python -m mypy setup.py aiomodel

test:
	python -m unittest discover

cov:
	python -m coverage run -m unittest discover
	python -m coverage html

check: black mypy
