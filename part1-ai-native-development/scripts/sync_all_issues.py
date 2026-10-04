#!/usr/bin/env python3
"""
Script to update all GitHub issues (#4 through #13) with their groomed markdown files.

Usage:
    export GITHUB_TOKEN="your_token_here"
    python scripts/sync_all_issues.py
"""

import os
import sys

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.update_issue import update_issue


def main():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if len(sys.argv) > 1 and not token:
        token = sys.argv[1]

    if not token:
        print("Error: GITHUB_TOKEN environment variable is not set.")
        print("Please set GITHUB_TOKEN and try again:")
        print("  export GITHUB_TOKEN=\"your_token_here\"")
        print("  .venv/bin/python scripts/sync_all_issues.py")
        sys.exit(1)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    groomed_dir = os.path.join(project_root, "_docs", "groomed_issues")

    print(f"Syncing groomed issues #4 through #13 to GitHub...\n")

    success_count = 0
    for i in range(4, 14):
        file_name = f"issue_{i:02d}.md"
        file_path = os.path.join(groomed_dir, file_name)

        if not os.path.exists(file_path):
            print(f"Skipping Issue #{i}: {file_path} does not exist.")
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            body = f.read()

        if update_issue(token, i, body=body):
            success_count += 1

    print(f"\nSuccessfully updated {success_count}/10 issues on GitHub!")


if __name__ == "__main__":
    main()
