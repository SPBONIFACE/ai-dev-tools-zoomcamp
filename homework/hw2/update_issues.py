import os
import re
import sys
import json
import urllib.request
import urllib.error

REPO = "SPBONIFACE/ai-dev-tools-zoomcamp-homework2"
TASKS_FILE = "_docs/tasks.md"

def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("\n❌ Error: GITHUB_TOKEN is not set.")
        print("Run:")
        print('  export GITHUB_TOKEN="your_personal_access_token"')
        print("  python3 update_issues.py\n")
        sys.exit(1)

    if not os.path.exists(TASKS_FILE):
        print(f"❌ Error: {TASKS_FILE} not found.")
        sys.exit(1)

    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Match sections: ## Issue #<number>: <title>
    sections = re.split(r'\n(?=##\s+Issue\s+#\d+:)', content)
    groomed_issues = {}

    for sec in sections:
        match = re.match(r'##\s+Issue\s+#(\d+):\s*(.*)', sec.strip())
        if not match:
            continue
        issue_num = int(match.group(1))
        title = match.group(2).split('\n')[0].strip()
        body_lines = sec.strip().split('\n')[1:]
        body = '\n'.join(body_lines).strip()
        groomed_issues[issue_num] = {"title": f"{issue_num}. {title}", "body": body}

    print(f"Found {len(groomed_issues)} groomed issues in {TASKS_FILE} to sync to {REPO}...")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "TableHop-Issue-Groomer",
        "Content-Type": "application/json",
    }

    for issue_num, data in groomed_issues.items():
        payload = json.dumps({"body": data["body"]}).encode("utf-8")
        url = f"https://api.github.com/repos/{REPO}/issues/{issue_num}"
        req = urllib.request.Request(url, data=payload, headers=headers, method="PATCH")

        try:
            with urllib.request.urlopen(req) as resp:
                print(f"✅ Updated GitHub Issue #{issue_num} with groomed specifications!")
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8")
            print(f"⚠️ Failed to update Issue #{issue_num}: HTTP {e.code} - {err_msg}")

    print("\n🎉 GitHub Issues synchronization complete!\n")

if __name__ == "__main__":
    main()
