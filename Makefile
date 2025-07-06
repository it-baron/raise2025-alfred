run-voice-worker:
	python3 main.py dev

run-voice-worker-console:
	python3 main.py console

typecheck:
	python3 -m mypy agents/ main.py --ignore-missing-imports --no-strict-optional --explicit-package-bases

check-imports:
	python3 -c "import ast, os; [print(f'Checking {f}') for f in os.listdir('agents') if f.endswith('.py')]" || echo "Install unimport: pip install unimport"

freeze:
	pip freeze > requirements.txt