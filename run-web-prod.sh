(cd frontend && npm install && npm run build && cd ..) && (poetry run gunicorn --config gunicorn.config.py backend.server:app)
