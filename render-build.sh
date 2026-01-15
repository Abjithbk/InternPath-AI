#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install Python Dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 2. Install the Browser (Crucial Step!)
# This downloads Chromium so Playwright can use it.
playwright install chromium