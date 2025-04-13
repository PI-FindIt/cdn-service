#!/bin/sh

# Copy initial data only if static directory is empty
if [ -z "$(ls -A "${STATIC_DIR:-/cdn-service/static}")" ]; then
    echo "Initializing static volume..."
    unzip -q /cdn-service/init_data.zip -d /cdn-service/static
    echo "Migration completed"
else
    echo "Static volume already contains data - skipping migration"
fi

# Start the application
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
