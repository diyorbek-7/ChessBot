#!/bin/bash
set -e  # Exit on any error

# Install basic tools if not present
if ! command -v apt-get &> /dev/null; then
    echo "apt-get not found, installing..."
    apk add --no-cache bash curl wget unzip || {
        echo "Failed to install basic tools"
        exit 1
    }
fi

# Update package lists and install dependencies
apt-get update || {
    echo "Failed to update package lists"
    exit 1
}
apt-get install -y wget unzip libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 || {
    echo "Failed to install dependencies"
    exit 1
}

# Install curl if not present (needed for Chromedriver version lookup)
if ! command -v curl &> /dev/null; then
    apt-get install -y curl || {
        echo "Failed to install curl"
        exit 1
    }
fi

# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb || {
    echo "Failed to download Chrome"
    exit 1
}
apt-get install -y ./google-chrome-stable_current_amd64.deb || {
    echo "Failed to install Chrome"
    exit 1
}
rm google-chrome-stable_current_amd64.deb

# Get the Chrome version
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+') || {
    echo "Failed to get Chrome version"
    exit 1
}
echo "Chrome version: $CHROME_VERSION"

# Download and install the matching Chromedriver version
CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}) || {
    echo "Failed to get Chromedriver version"
    exit 1
}
wget -N https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip || {
    echo "Failed to download Chromedriver"
    exit 1
}
unzip chromedriver_linux64.zip || {
    echo "Failed to unzip Chromedriver"
    exit 1
}
mv chromedriver /usr/local/bin/ || {
    echo "Failed to move Chromedriver"
    exit 1
}
chmod +x /usr/local/bin/chromedriver
rm chromedriver_linux64.zip

# Verify installations
google-chrome --version || {
    echo "Chrome installation failed"
    exit 1
}
chromedriver --version || {
    echo "Chromedriver installation failed"
    exit 1
}