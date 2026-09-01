#!/bin/sh
set -e

echo "Aplicando migraciones de base de datos..."
aerich fix-migrations
aerich upgrade

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
