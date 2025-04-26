#!/bin/bash

read -sp "Enter your GitHub Personal Access Token: " TOKEN
echo ""

GITHUB_USERNAME="sarkarj"
REPO_NAME="URLRepo"
REMOTE="https://$GITHUB_USERNAME:$TOKEN@github.com/$GITHUB_USERNAME/$REPO_NAME.git"

echo "[+] Initializing Git repository..."
git init

echo "[+] Setting Git config..."
git config user.name "$GITHUB_USERNAME"
git config user.email "$GITHUB_USERNAME@users.noreply.github.com"


echo "[+] Adding files to Git (excluding .env)..."
git add .
git commit -m "Initial clean commit" || echo "[i] Nothing to commit."

echo "[+] Setting remote and pushing..."
git branch -M main
git remote remove origin 2>/dev/null
git remote add origin "$REMOTE"
git push -u origin main --force

echo "[✔] Code pushed successfully (without .env)!"
