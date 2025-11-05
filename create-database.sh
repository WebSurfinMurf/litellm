#!/bin/bash
set -e

PROJECT_NAME="litellm"
DB_NAME="${PROJECT_NAME}_db"
DB_USER="${PROJECT_NAME}_user"
DB_PASSWORD='LiteLLMPass2025'
SECRETS_FILE="$HOME/projects/secrets/${PROJECT_NAME}.env"

# Generate the new virtual key
NEW_VIRTUAL_KEY="sk-$(openssl rand -hex 32)"

# Stop any active connections to the database
echo "Stopping litellm container to release database connections..."
docker stop litellm 2>/dev/null || true

# Run the psql commands
echo "Recreating database and user..."
PGPASSWORD='Pass123qp' psql -h localhost -p 5432 -U admin -d postgres << EOF
-- Drop if exists (for clean setup)
DROP DATABASE IF EXISTS ${DB_NAME};
DROP USER IF EXISTS ${DB_USER};

-- Create user and database
CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';
CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};

-- Connect to new database for extensions
\c ${DB_NAME}
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOF

# Create the secrets file cleanly
echo "Creating new secrets file at ${SECRETS_FILE}..."
# Overwrite the file with the header
echo "# Database Configuration" > "${SECRETS_FILE}"
# Append the rest of the variables
echo "DB_HOST=postgres" >> "${SECRETS_FILE}"
echo "DB_PORT=5432" >> "${SECRETS_FILE}"
echo "DB_NAME=${DB_NAME}" >> "${SECRETS_FILE}"
echo "DB_USER=${DB_USER}" >> "${SECRETS_FILE}"
echo "DB_PASSWORD=${DB_PASSWORD}" >> "${SECRETS_FILE}"
echo "DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}" >> "${SECRETS_FILE}"
echo "" >> "${SECRETS_FILE}"
echo "# New, correctly formatted virtual key" >> "${SECRETS_FILE}"
echo "LITELLM_VIRTUAL_KEY_TEST=${NEW_VIRTUAL_KEY}" >> "${SECRETS_FILE}"
echo "" >> "${SECRETS_FILE}"
echo "# You must re-add your other keys like LITELLM_MASTER_KEY and ANTHROPIC_API_KEY to this file" >> "${SECRETS_FILE}"

chmod 600 "${SECRETS_FILE}"

echo "✅ Database ${DB_NAME} created"
echo "✅ User ${DB_USER} created"
echo "✅ Credentials saved to ${SECRETS_FILE}"
echo ""
echo "Your new virtual key is: ${NEW_VIRTUAL_KEY}"
echo ""
echo "IMPORTANT: The secrets file has been overwritten."
echo "You must re-add your LITELLM_MASTER_KEY and ANTHROPIC_API_KEY to it."
echo ""
echo "Next steps:"
echo "1. Edit ${SECRETS_FILE} to add your other keys."
echo "2. Run 'docker compose up -d' in the litellm directory."