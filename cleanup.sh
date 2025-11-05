#!/bin/bash
set -e

echo "--- Starting LiteLLM Cleanup ---"

# --- 1. Stop and Remove Docker Containers ---
echo "Stopping and removing 'litellm' container..."
if [ "$(docker ps -q -f name=litellm)" ]; then
    docker compose down
    echo "'litellm' container and associated network stopped and removed."
else
    echo "'litellm' container not found. Skipping."
fi

# --- 2. Drop PostgreSQL Database and User ---
echo "Connecting to PostgreSQL to drop database and user..."
PGPASSWORD='Pass123qp' psql -h localhost -p 5432 -U admin -d postgres << EOF
-- Terminate any active connections to the database before dropping it
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'litellm_db';

-- Drop the database and user
DROP DATABASE IF EXISTS litellm_db;
DROP USER IF EXISTS litellm_user;
EOF
echo "Database 'litellm_db' and user 'litellm_user' dropped."

# --- 3. Clean up other assets (optional) ---
# The secrets file is left untouched intentionally.
# If you want to remove it, uncomment the line below.
# echo "Removing secrets file..."
# rm -f $HOME/projects/secrets/litellm.env

echo "--- LiteLLM Cleanup Complete ---"
