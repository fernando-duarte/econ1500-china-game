#!/bin/bash
# Script to generate requirements.lock files from requirements.txt files

# Exit on error
set -e

echo "=== Generating Python requirements.lock files ==="

# Function to generate lock file for a specific directory
generate_lock_file() {
  local dir=$1
  local req_file="${dir}/requirements.txt"
  local lock_file="${dir}/requirements.lock"

  if [ ! -f "$req_file" ]; then
    echo "❌ Error: $req_file does not exist"
    return 1
  fi

  echo "📦 Generating lock file for $dir"

  # Create a temporary virtual environment
  python3 -m venv "${dir}/.temp_venv"

  # Activate the virtual environment
  source "${dir}/.temp_venv/bin/activate"

  # Install dependencies from requirements.txt
  python3 -m pip install --upgrade pip
  python3 -m pip install -r "$req_file"

  # Generate pinned dependencies
  python3 -m pip freeze > "$lock_file"

  # Clean up
  deactivate
  rm -rf "${dir}/.temp_venv"

  echo "✅ Successfully generated $lock_file"
}

# Generate lock files for all Python components
generate_lock_file "model"
generate_lock_file "china-growth-game/economic-model"

echo "=== All requirements.lock files generated successfully ==="
