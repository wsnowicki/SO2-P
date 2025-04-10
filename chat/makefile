.PHONY: server client lint format run-all

# Run the server
server:
	python chat/server.py --ip 0.0.0.0 --port 9000 --db chat.db --loglevel INFO

# Run the client
client:
	python chat/client.py --ip 127.0.0.1 --port 9000 --loglevel INFO

# Lint Python files with flake8
lint:
	flake8 chat

# Format code with black
format:
	black chat

