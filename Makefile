
install:
	python -m pip install -e .

install-dev:
	python -m pip install -e .[dev]

black:
	python -m black setup.py aiomodels tests

mypy:
	python -m mypy setup.py aiomodels

test:
	python -m coverage run -m unittest discover

cov:
	python -m coverage html

check: black mypy test cov
