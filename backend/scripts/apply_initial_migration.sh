#!/bin/bash

# 提醒：你可能需要给这个脚本添加执行权限
# chmod +x backend/scripts/apply_initial_migration.sh

echo "Navigating to backend directory..."
cd "$(dirname "$0")/../../backend" || exit

echo "Generating initial Alembic revision..."
alembic revision --autogenerate -m "Initial database schema"

if [ $? -ne 0 ]; then
  echo "Error generating Alembic revision. Please check the output above."
  exit 1
fi

echo "Applying database migrations..."
alembic upgrade head

if [ $? -ne 0 ]; then
  echo "Error applying database migrations. Please check the output above."
  exit 1
fi

echo "Initial database migration applied successfully."