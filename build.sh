#!/usr/bin/env bash
# Render build script

set -o errexit  # Exit on error

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Build complete!"
echo "Note: Database (data.db) should be committed to git or uploaded manually"
echo "Checking if database exists..."
if [ -f "app/db/data.db" ]; then
    echo "✓ Database found at app/db/data.db"
else
    echo "⚠ WARNING: Database not found. You may need to upload it or run initialization scripts."
fi
