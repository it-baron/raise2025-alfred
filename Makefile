PROJECT_DIR=/Users/alexeus/raise2025/alfred

coral-server-local:
	cd coral-server && ./gradlew run

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

docker-alfred-assistant-build:
	docker build -t alfred-assistant ./agents/alfred

docker-alfred-assistant-push:
	docker tag alfred-assistant ams.vultrcr.com/alfred/alfred-assistant:latest
	docker push ams.vultrcr.com/alfred/alfred-assistant:latest

docker-alfred-assistant-run:
	docker run --name alfred-assistant -p 8000:8000 alfred-assistant

docker-coral-server-build:
	docker build -t coral-server ./coral-server

docker-coral-server-push:
	docker tag coral-server ams.vultrcr.com/alfred/coral-server:latest
	docker push ams.vultrcr.com/alfred/coral-server:latest

docker-coral-studio-build:
	docker build -t coral-studio ./coral-studio

docker-coral-studio-push:
	docker tag ghcr.io/coral-protocol/coral-studio ams.vultrcr.com/alfred/coral-studio:latest
	docker push ams.vultrcr.com/alfred/coral-studio:latest

