#!/bin/bash

# Set Python path to include the current directory
export PYTHONPATH="${PYTHONPATH}:/home/site/wwwroot"

# Install dependencies (if needed)
pip install -r requirements.txt

# Wait for Postgres to be available (tries for ~60s)
echo "Waiting for database to become available..."
TRIES=0
MAX_TRIES=30
until python - <<'PY' 2>/dev/null
import os,sys
from sqlalchemy import create_engine
url = os.environ.get('SQLALCHEMY_DATABASE_URL') or os.environ.get('DATABASE_URL')
if not url:
	print('no_db_url')
	sys.exit(2)
try:
	create_engine(url).connect()
	print('ok')
	sys.exit(0)
except Exception as e:
	print('notready', e)
	sys.exit(1)
PY
do
	TRIES=$((TRIES+1))
	if [ $TRIES -ge $MAX_TRIES ]; then
		echo "Database did not become available after $((MAX_TRIES*2)) seconds. Proceeding anyway."
		break
	fi
	sleep 2
done

# Ensure Alembic migrations folder exists
mkdir -p alembic/versions

# Autogenerate migrations only when AUTO_MIGRATE is explicitly enabled (dev only).
AUTO_MIGRATE_NORMALIZED=$(printf '%s' "${AUTO_MIGRATE:-false}" | tr '[:upper:]' '[:lower:]')
if [ "${AUTO_MIGRATE_NORMALIZED}" = "true" ]; then
	REVISION_FILES=$(find alembic/versions -maxdepth 1 -name '*.py' -type f 2>/dev/null)
	if [ -z "${REVISION_FILES}" ]; then
		echo "No Alembic revisions found — creating initial revision"
		python -m alembic revision --autogenerate -m "initial" || true
	else
		echo "AUTO_MIGRATE=true — checking for model changes and creating autogenerate revision if needed"
		python -m alembic revision --autogenerate -m "autogen $(date -u +%Y%m%d%H%M%S)" || true
		LATEST_FILE=$(find alembic/versions -maxdepth 1 -name '*.py' -type f -printf '%T@ %f\n' 2>/dev/null | sort -nr | head -n1 | cut -d' ' -f2-)
		if [ -z "${LATEST_FILE}" ]; then
			LATEST_FILE=$(ls -t alembic/versions/*.py 2>/dev/null | head -n1)
			LATEST_FILE=${LATEST_FILE##*/}
		fi
		if [ -n "${LATEST_FILE}" ]; then
			if ! grep -q "op\." "alembic/versions/${LATEST_FILE}"; then
				echo "No DB-op changes detected in ${LATEST_FILE} — removing no-op revision"
				rm -f "alembic/versions/${LATEST_FILE}"
			else
				echo "Autogenerate created ${LATEST_FILE} with changes"
			fi
		fi
	fi
else
	echo "AUTO_MIGRATE disabled — skipping autogenerate step"
fi

# Apply migrations to the database
echo "Applying Alembic migrations (upgrade head)"
python -m alembic upgrade head

# Run the application: use multiple workers for production
APP_PORT="${APP_PORT:-3090}"
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b "0.0.0.0:${APP_PORT}" main:app

