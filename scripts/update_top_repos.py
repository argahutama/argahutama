import os
import re
import json
import urllib.request

USERNAME = "argahutama"
TOP_N = 3
README_PATH = "README.md"
MARKER_START = "<!-- TOP_REPOS_START -->"
MARKER_END = "<!-- TOP_REPOS_END -->"

token = os.environ.get("GITHUB_TOKEN", "")

def fetch_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos?type=public&sort=stars&direction=desc&per_page=100"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    })
    with urllib.request.urlopen(req) as res:
        repos = json.loads(res.read())

    # exclude forks, keep originals only, sorted by stars
    return [r for r in repos if not r["fork"]][:TOP_N]

def build_cards(repos):
    cards = []
    for repo in repos:
        name = repo["name"]
        url = f"https://github.com/{USERNAME}/{name}"
        card = f'  <a href="{url}"><img src="https://github-readme-stats.vercel.app/api/pin/?username={USERNAME}&repo={name}&theme=algolia" alt="{name}"></a>'
        cards.append(card)

    # two cards per row
    rows = []
    for i in range(0, len(cards), 2):
        pair = cards[i:i+2]
        rows.append('<p align="center">\n' + "\n".join(pair) + "\n</p>")

    return "\n" + "\n".join(rows) + "\n"

def update_readme(content):
    with open(README_PATH, "r") as f:
        readme = f.read()

    updated = re.sub(
        rf"{re.escape(MARKER_START)}.*?{re.escape(MARKER_END)}",
        f"{MARKER_START}{content}{MARKER_END}",
        readme,
        flags=re.DOTALL,
    )

    with open(README_PATH, "w") as f:
        f.write(updated)

    print("README updated.")

if __name__ == "__main__":
    repos = fetch_repos()
    if not repos:
        print("No public repos found.")
    else:
        cards = build_cards(repos)
        update_readme(cards)
        print(f"Updated with {len(repos)} repos.")
