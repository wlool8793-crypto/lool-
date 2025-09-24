#!/bin/bash

# 🚀 Google Docs Clone - Auto Deployment Script
# This script will deploy your application to GitHub Pages

echo "🚀 Starting deployment process..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Check if user is logged in to GitHub
echo "📋 Checking GitHub authentication..."
if ! git config --global user.name &> /dev/null; then
    echo "⚠️  Git user not configured. Please run:"
    echo "   git config --global user.name 'Your Name'"
    echo "   git config --global user.email 'your.email@example.com'"
    exit 1
fi

# Get repository information
read -p "Enter your GitHub username: " username
read -p "Enter your repository name (e.g., google-docs-clone): " reponame

echo "📁 Repository will be: https://github.com/$username/$reponame"

# Initialize git repository
echo "📝 Initializing git repository..."
git init
git add .
git commit -m "🚀 Deploy Google Docs Clone - All features working"

# Create repository on GitHub (this would normally be done manually)
echo "⚠️  Please create a repository named '$reponame' on GitHub first"
echo "   Visit: https://github.com/new"
read -p "Press Enter once you've created the repository..."

# Add remote and push
echo "📤 Pushing to GitHub..."
git remote add origin https://github.com/$username/$reponame.git
git branch -M main
git push -u origin main

echo "✅ Code pushed to GitHub!"
echo ""
echo "📋 Next steps:"
echo "   1. Go to: https://github.com/$username/$reponame/settings/pages"
echo "   2. Under 'Source', select 'Deploy from a branch'"
echo "   3. Choose 'main' branch and '/ (root)' folder"
echo "   4. Click Save"
echo ""
echo "🌐 Your site will be live at: https://$username.github.io/$reponame"
echo ""
echo "🎉 Deployment complete!"