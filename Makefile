
install:
	python -m pip install -r requirements.txt

black:
	python -m black main.py

mypy:
	python -m mypy main.py

check: black mypy
