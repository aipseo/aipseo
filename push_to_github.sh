#!/bin/bash
set -e

echo "Preparing to push aipseo-cli to GitHub..."

# Check if GITHUB_TOKEN is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is not set."
    echo "Please set the GITHUB_TOKEN environment variable."
    exit 1
fi

# Configure git
git config --global user.name "AIPSEO Bot"
git config --global user.email "bot@aipseo.com"

# Create a temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Clone the repository with token authentication
REPO_URL="https://$GITHUB_TOKEN@github.com/aipseo/aipseo-cli.git"
git clone "$REPO_URL" . || git init

# If this is a fresh repository, create an initial commit
if [ ! -f "README.md" ]; then
    echo "# AIPSEO CLI" > README.md
    git add README.md
    git commit -m "Initial commit"
    
    # Set up the remote repository if it's a fresh init
    git remote add origin "$REPO_URL"
fi

# Copy files from the source directory
cp -r /home/runner/workspace/aipseo-cli/* .

# Add all files to git
git add .

# Commit the changes
git commit -m "Update aipseo-cli to v0.1.0" || echo "No changes to commit"

# Create tag
git tag -a "v0.1.0" -m "Version 0.1.0"

# Push to GitHub
git push -u origin main --tags

echo "Successfully pushed aipseo-cli v0.1.0 to GitHub!"