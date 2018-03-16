#!/bin/bash -ex

echo Starting dredd
dredd --hookfiles "./tests/dredd-hooks/*hook.py" \
--server "gunicorn history.app:app \
          --bind 0.0.0.0:8000 \
          --reload -R \
          --access-logfile - \
          --log-file - \
          --env PYTHONUNBUFFERED=1 -k gevent" \
--language python docs/history.apib http://127.0.0.1:8000
