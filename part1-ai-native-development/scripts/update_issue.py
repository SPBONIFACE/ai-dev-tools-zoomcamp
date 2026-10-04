#!/usr/bin/env python3
"""
Script to update a GitHub issue content (body and/or title).

Usage:
    export GITHUB_TOKEN="your_token"
    python scripts/update_issue.py --issue 4 --file path/to/groomed_issue.md
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

REPO_OWNER = "SPBONIFACE"
REPO_NAME = "ai-dev-tools-zoomcamp"


def update_issue(token, issue_number, title=None, body=None):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "AI-DevOps-Issue-Updater"
    }

    payload = {}
    if title:
        payload["title"] = title
    if body:
        payload["body"] = body

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")

    try:
        with urllib.request.urlopen(req) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            print(f"Successfully updated Issue #{issue_number}: {res_data['html_url']}")
            return True
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        print(f"HTTP Error {e.code} updating issue #{issue_number}: {err_body}")
        return False
    except Exception as e:
        print(f"Error updating issue #{issue_number}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Update GitHub issue body/title")
    parser.add_argument("--issue", type=int, required=True, help="Issue number to update")
    parser.add_argument("--title", help="New title for the issue")
    parser.add_argument("--body-file", help="Path to markdown file containing new issue body")
    parser.add_argument("--token", help="GitHub Access Token")
    args = parser.parse_args()

    token = args.token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    body = None
    if args.body_file and os.path.exists(args.body_file):
        with open(args.body_file, "r", encoding="utf-8") as f:
            body = f.read()

    if not token:
        print(f"Prepared update for Issue #{args.issue}, but GITHUB_TOKEN is not set.")
        print("To update on GitHub, set GITHUB_TOKEN and run this script.")
        return

    update_issue(token, args.issue, title=args.title, body=body)


if __name__ == "__main__":
    main()
