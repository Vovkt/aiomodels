
install:
	python -m pip install -e .

install-dev:
	python -m pip install -e .[dev]

black:
	python -m black setup.py aiomodel

mypy:
	python -m mypy setup.py aiomodel

check: black mypy
