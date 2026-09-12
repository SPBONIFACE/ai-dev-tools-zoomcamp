#!/usr/bin/env python3
"""
Script to create GitHub issues for tasks in backlog.md for SPBONIFACE/ai-dev-tools-zoomcamp.

Usage:
    export GITHUB_TOKEN="your_personal_access_token"
    python scripts/create_github_issues.py

Or pass token directly:
    python scripts/create_github_issues.py --token "your_personal_access_token"
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error

REPO_OWNER = "SPBONIFACE"
REPO_NAME = "ai-dev-tools-zoomcamp"
BACKLOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backlog.md")


def parse_backlog(filepath):
    if not os.path.exists(filepath):
        print(f"Error: Backlog file not found at {filepath}")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    sprints = content.split("## Sprint ")
    tasks = []

    for sprint_block in sprints[1:]:
        lines = sprint_block.strip().split("\n")
        sprint_name = "Sprint " + lines[0].strip()
        
        current_task = None
        for line in lines[1:]:
            task_match = re.match(r'^-\s+\[([ xX])\]\s+\*\*(TASK-\d+:\s+.*?)\*\*', line)
            if task_match:
                is_completed = task_match.group(1).lower() == 'x'
                task_title = task_match.group(2)
                current_task = {
                    "sprint": sprint_name,
                    "title": f"[{sprint_name.split(':')[0]}] {task_title}",
                    "is_completed": is_completed,
                    "body_lines": [f"**Sprint**: {sprint_name}\n**Status in Backlog**: {'Completed' if is_completed else 'Pending'}\n\n**Details**:"]
                }
                tasks.append(current_task)
            elif current_task and line.strip().startswith("- "):
                sub_detail = line.strip()[2:]
                current_task["body_lines"].append(f"- {sub_detail}")

    for t in tasks:
        t["body"] = "\n".join(t["body_lines"])

    return tasks


def create_github_issue(token, repo_owner, repo_name, task):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "AI-DevOps-Issue-Creator"
    }

    payload = {
        "title": task["title"],
        "body": task["body"],
        "labels": [task["sprint"].split(":")[0].strip().lower().replace(" ", "-")]
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            issue_number = res_data["number"]
            issue_url = res_data["html_url"]
            print(f"Created Issue #{issue_number}: {task['title']} -> {issue_url}")
            
            # If completed in backlog, close the issue
            if task["is_completed"]:
                close_issue(token, repo_owner, repo_name, issue_number)
                
            return issue_number
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        print(f"HTTP Error {e.code} creating issue '{task['title']}': {err_body}")
        return None
    except Exception as e:
        print(f"Error creating issue '{task['title']}': {e}")
        return None


def close_issue(token, repo_owner, repo_name, issue_number):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "AI-DevOps-Issue-Creator"
    }

    payload = {"state": "closed"}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")

    try:
        with urllib.request.urlopen(req) as resp:
            print(f"  Closed Issue #{issue_number} (marked complete in backlog)")
    except Exception as e:
        print(f"  Failed to close Issue #{issue_number}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Create GitHub issues from backlog.md")
    parser.add_argument("--token", help="GitHub Personal Access Token (or set GITHUB_TOKEN env var)")
    args = parser.parse_args()

    token = args.token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("Error: GitHub access token is required.")
        print("Please set GITHUB_TOKEN environment variable or pass --token <YOUR_TOKEN>.")
        print("\nTo generate a token with 'repo' scope:")
        print("  GitHub -> Settings -> Developer settings -> Personal access tokens -> Tokens (classic)")
        sys.exit(1)

    tasks = parse_backlog(BACKLOG_PATH)
    print(f"Found {len(tasks)} tasks in backlog.md. Creating issues on {REPO_OWNER}/{REPO_NAME}...\n")

    created = 0
    for task in tasks:
        res = create_github_issue(token, REPO_OWNER, REPO_NAME, task)
        if res:
            created += 1

    print(f"\nSuccessfully processed {created}/{len(tasks)} issues!")


if __name__ == "__main__":
    main()
