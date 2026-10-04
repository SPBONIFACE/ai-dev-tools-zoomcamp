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
        print("  python3 create_issues.py\n")
        sys.exit(1)

    if not os.path.exists(TASKS_FILE):
        print(f"❌ Error: {TASKS_FILE} not found.")
        sys.exit(1)

    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by task header (## <number>.)
    sections = re.split(r'\n(?=##\s+\d+\.)', content)
    tasks = []

    for sec in sections:
        if not sec.strip().startswith("##"):
            continue
        lines = [line.strip() for line in sec.strip().split("\n") if line.strip()]
        header = lines[0].replace("##", "").strip()
        body = "\n\n".join(lines[1:])
        tasks.append({"title": header, "body": body})

    print(f"Found {len(tasks)} tasks in {TASKS_FILE} to upload to {REPO}...")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "TableHop-Issue-Creator",
        "Content-Type": "application/json",
    }

    url = f"https://api.github.com/repos/{REPO}/issues"

    for task in tasks:
        payload = json.dumps({"title": task["title"], "body": task["body"]}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                print(f"✅ Created Issue #{data['number']}: {task['title']}")
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8")
            print(f"❌ Failed to create '{task['title']}': HTTP {e.code} - {err_msg}")
            sys.exit(1)

    print("\n🎉 All tasks successfully moved into GitHub Issues!\n")

if __name__ == "__main__":
    main()
