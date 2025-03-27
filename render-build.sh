#!/bin/bash
set -e  # Exit on any error

# Install basic tools (wget, unzip) if not present
if ! command -v wget &> /dev/null || ! command -v unzip &> /dev/null; then
    echo "Installing basic tools (wget, unzip)..."
    apk add --no-cache wget unzip || {
        echo "Failed to install basic tools"
        exit 1
    }
fi

# Install curl if not present (needed for Chromedriver version lookup)
if ! command -v curl &> /dev/null; then
    echo "Installing curl..."
    apk add --no-cache curl || {
        echo "Failed to install curl"
        exit 1
    }
fi

# Create directories for Chrome and Chromedriver in /app (writable directory)
mkdir -p /app/chrome
mkdir -p /app/chromedriver

# Download and install Chrome (headless version)
echo "Downloading Chrome..."
wget -O /tmp/chrome-linux64.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/123.0.6312.122/linux64/chrome-linux64.zip || {
    echo "Failed to download Chrome"
    exit 1
}
unzip /tmp/chrome-linux64.zip -d /app/chrome || {
    echo "Failed to unzip Chrome"
    exit 1
}
rm /tmp/chrome-linux64.zip

# Set Chrome binary path
CHROME_BINARY="/app/chrome/chrome-linux64/chrome"
chmod +x $CHROME_BINARY

# Get the Chrome version
CHROME_VERSION=$($CHROME_BINARY --version | grep -oP '\d+\.\d+\.\d+\.\d+') || {
    echo "Failed to get Chrome version"
    exit 1
}
echo "Chrome version: $CHROME_VERSION"

# Download and install the matching Chromedriver version
echo "Downloading Chromedriver..."
CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%.*}) || {
    echo "Failed to get Chromedriver version"
    exit 1
}
wget -O /tmp/chromedriver-linux64.zip https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver-linux64.zip || {
    echo "Failed to download Chromedriver"
    exit 1
}
unzip /tmp/chromedriver-linux64.zip -d /app/chromedriver || {
    echo "Failed to unzip Chromedriver"
    exit 1
}
rm /tmp/chromedriver-linux64.zip

# Set Chromedriver binary path
CHROMEDRIVER_BINARY="/app/chromedriver/chromedriver-linux64/chromedriver"
chmod +x $CHROMEDRIVER_BINARY

# Verify installations
$CHROME_BINARY --version || {
    echo "Chrome installation failed"
    exit 1
}
$CHROMEDRIVER_BINARY --version || {
    echo "Chromedriver installation failed"
    exit 1
}

# Export paths for the runtime environment
echo "Exporting Chrome and Chromedriver paths..."
echo "CHROME_BINARY=$CHROME_BINARY" >> $RENDER_ENV_FILE
echo "CHROMEDRIVER_BINARY=$CHROMEDRIVER_BINARY" >> $RENDER_ENV_FILE