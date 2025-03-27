#!/bin/bash

# Use a verified Chrome for Testing version that matches Chromedriver
CHROME_VERSION="124.0.6367.78"  # Tested working version
CHROMEDRIVER_VERSION="124.0.6367.78"

# Install system dependencies
apt-get update
apt-get install -y wget unzip

# Install Chrome for Testing
echo "Installing Chrome for Testing ${CHROME_VERSION}..."
mkdir -p /tmp/chrome
wget -nv -O /tmp/chrome.zip \
  "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_VERSION}/linux64/chrome-linux64.zip"
unzip -q /tmp/chrome.zip -d /tmp/chrome/
CHROME_BINARY="/tmp/chrome/chrome-linux64/chrome"

# Install matching Chromedriver
echo "Installing Chromedriver ${CHROMEDRIVER_VERSION}..."
mkdir -p /tmp/chromedriver
wget -nv -O /tmp/chromedriver.zip \
  "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip"
unzip -q /tmp/chromedriver.zip -d /tmp/chromedriver/
CHROMEDRIVER_BINARY="/tmp/chromedriver/chromedriver-linux64/chromedriver"

# Verify installations
if [ ! -f "$CHROME_BINARY" ]; then
  echo "Error: Chrome binary not found at $CHROME_BINARY"
  exit 1
fi

if [ ! -f "$CHROMEDRIVER_BINARY" ]; then
  echo "Error: Chromedriver not found at $CHROMEDRIVER_BINARY"
  exit 1
fi

# Set permissions
chmod +x "$CHROME_BINARY"
chmod +x "$CHROMEDRIVER_BINARY"

# Export paths to Render environment
echo "Exporting environment variables..."
echo "CHROME_BINARY=$CHROME_BINARY" >> $RENDER_ENV_FILE
echo "CHROMEDRIVER_BINARY=$CHROMEDRIVER_BINARY" >> $RENDER_ENV_FILE

# Verify versions
echo "Chrome version:"
$CHROME_BINARY --version
echo "Chromedriver version:"
$CHROMEDRIVER_BINARY --version

echo "Chrome and Chromedriver installed successfully!"