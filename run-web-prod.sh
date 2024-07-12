(cd frontend && npm install && npm run build && cd ..) && (poetry run gunicorn --config backend/gunicorn.config.py backend.server:app)
