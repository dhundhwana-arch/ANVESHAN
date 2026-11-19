#!/usr/bin/env bash
# Push ANVESHAN v1 files cleanly to https://github.com/dhundhwana-arch/ANVESHAN
# Usage (Termux or Linux/macOS):
#   unzip ANVESHAN_v1_repo.zip -d anveshan_v1
#   cd anveshan_v1 && bash push_to_github.sh
set -euo pipefail

REPO_URL="https://github.com/dhundhwana-arch/ANVESHAN.git"
BRANCH="feat/anveshan-v1-core"

echo "Setting remote origin to ${REPO_URL}..."
git remote remove origin 2>/dev/null || true
git remote add origin "${REPO_URL}"
git fetch origin main || true
echo "Ready to push branch '${BRANCH}' to GitHub (will prompt for your GitHub token/credentials if not cached):"
git push -u origin "${BRANCH}"
echo "Done! Open a Pull Request on GitHub from '${BRANCH}' into 'main'."
