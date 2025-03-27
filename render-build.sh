#!/bin/bash

# Set versions
CHROME_VERSION="123.0.6312.122"
CHROMEDRIVER_VERSION="123.0.6312.122"

# Install Chrome
echo "Installing Chrome..."
wget -O /tmp/chrome.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_VERSION}/linux64/chrome-linux64.zip"
unzip /tmp/chrome.zip -d /tmp/chrome/
CHROME_BINARY="/tmp/chrome/chrome-linux64/chrome"

# Install Chromedriver
echo "Installing Chromedriver..."
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /tmp/chromedriver/
CHROMEDRIVER_BINARY="/tmp/chromedriver/chromedriver"

# Verify installations
if [ ! -f "$CHROME_BINARY" ]; then
    echo "Error: Chrome binary not found at $CHROME_BINARY"
    exit 1
fi

if [ ! -f "$CHROMEDRIVER_BINARY" ]; then
    echo "Error: Chromedriver not found at $CHROMEDRIVER_BINARY"
    exit 1
fi

# Export paths
echo "Exporting paths..."
echo "CHROME_BINARY=${CHROME_BINARY}" >> $RENDER_ENV_FILE
echo "CHROMEDRIVER_BINARY=${CHROMEDRIVER_BINARY}" >> $RENDER_ENV_FILE

echo "Build completed successfully!"