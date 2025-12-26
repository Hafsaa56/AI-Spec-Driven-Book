#!/bin/bash

# Script to validate the Docusaurus build process
echo "Validating Docusaurus build..."

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2)
NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)

if [ "$NODE_MAJOR" -lt 18 ]; then
    echo "Error: Node.js version 18+ is required. Current version: $NODE_VERSION"
    exit 1
fi

echo "Node.js version $NODE_VERSION is valid"

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed"
    exit 1
fi

echo "npm is available"

# Install dependencies
echo "Installing dependencies..."
npm install

# Try to build the site
echo "Building the site..."
npm run build

if [ $? -eq 0 ]; then
    echo "Build validation: SUCCESS"
    echo "The Docusaurus site builds successfully"
    exit 0
else
    echo "Build validation: FAILED"
    exit 1
fi