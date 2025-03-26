#!/bin/bash
# Update package lists
sudo apt-get update
# Install required tools
sudo apt-get install -y wget unzip
# Add Google's Chrome repository key
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
# Add Chrome repository
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
# Update package lists again
sudo apt-get update
# Install Chrome
sudo apt-get install -y google-chrome-stable
# Get installed Chrome version
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
# Download matching Chromedriver version
wget -N https://chromedriver.storage.googleapis.com/$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION})/chromedriver_linux64.zip
# Unzip and move Chromedriver to a system path
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver