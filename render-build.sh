#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install Python Dependencies
pip install -r requirements.txt

# 2. Force Install Chromium via Python Module
# This ensures it uses the correct library we just installed
echo "⬇️ Installing Patchright Chromium..."
python -m patchright install chromium

echo "✅ Build Complete"