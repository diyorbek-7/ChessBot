#!/bin/bash

set -e

RENDER_ENV_FILE="/app/.env"

# Define versions and URLs
CHROME_VERSION="124.0.6367.78"
CHROME_URL="https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/linux64/chrome-linux64.zip"
CHROMEDRIVER_URL="https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/linux64/chromedriver-linux64.zip"

# Define temporary and runtime directories
TMP_CHROME_DIR="/tmp/chrome"
TMP_CHROMEDRIVER_DIR="/tmp/chromedriver"
RUNTIME_CHROME_DIR="/app/chrome"
RUNTIME_CHROMEDRIVER_DIR="/app/chromedriver"

# Create temporary directories
mkdir -p "$TMP_CHROME_DIR"
mkdir -p "$TMP_CHROMEDRIVER_DIR"

# Download Chrome
echo "Installing Chrome for Testing $CHROME_VERSION..."
curl -L "$CHROME_URL" -o "/tmp/chrome.zip"
unzip -o "/tmp/chrome.zip" -d "$TMP_CHROME_DIR"

# Download Chromedriver
echo "Installing Chromedriver $CHROME_VERSION..."
curl -L "$CHROMEDRIVER_URL" -o "/tmp/chromedriver.zip"
unzip -o "/tmp/chromedriver.zip" -d "$TMP_CHROMEDRIVER_DIR"

# Export environment variables for runtime
echo "Exporting environment variables..."
echo "CHROME_BINARY=$RUNTIME_CHROME_DIR/chrome-linux64/chrome" >> "$RENDER_ENV_FILE"
echo "CHROMEDRIVER_BINARY=$RUNTIME_CHROMEDRIVER_DIR/chromedriver-linux64/chromedriver" >> "$RENDER_ENV_FILE"

# Verify versions
echo "Chrome version:"
"$TMP_CHROME_DIR/chrome-linux64/chrome" --version
echo "Chromedriver version:"
"$TMP_CHROMEDRIVER_DIR/chromedriver-linux64/chromedriver" --version

# Move Chrome and Chromedriver to /app for runtime
echo "Moving Chrome and Chromedriver to /app for runtime..."
mkdir -p "$RUNTIME_CHROME_DIR"
mkdir -p "$RUNTIME_CHROMEDRIVER_DIR"
mv "$TMP_CHROME_DIR/chrome-linux64" "$RUNTIME_CHROME_DIR/"
mv "$TMP_CHROMEDRIVER_DIR/chromedriver-linux64" "$RUNTIME_CHROMEDRIVER_DIR/"

echo "Chrome and Chromedriver installed successfully!"