import os
import re
import json
import urllib.request

USERNAME = "argahutama"
TOP_N = 6
README_PATH = "README.md"
MARKER_START = "<!-- TOP_REPOS_START -->"
MARKER_END = "<!-- TOP_REPOS_END -->"

LANGUAGE_COLORS = {
    "Kotlin": "7F52FF",
    "Dart": "0175C2",
    "Java": "b07219",
    "Swift": "F05138",
    "Objective-C": "438eff",
    "Python": "3572A5",
    "JavaScript": "f1e05a",
    "TypeScript": "3178c6",
    "Go": "00ADD8",
    "Rust": "dea584",
    "Ruby": "701516",
    "PHP": "4F5D95",
    "C": "555555",
    "C++": "f34b7d",
    "C#": "178600",
    "Shell": "89e051",
    "Groovy": "e69f56",
    "Scala": "c22d40",
    "Lua": "000080",
    "R": "198CE7",
    "HTML": "e34c26",
    "CSS": "563d7c",
    "SCSS": "c6538c",
    "Vue": "41b883",
    "Svelte": "ff3e00",
}

token = os.environ.get("GITHUB_TOKEN", "")

def fetch_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos?type=public&sort=stars&direction=desc&per_page=100"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    })
    with urllib.request.urlopen(req) as res:
        repos = json.loads(res.read())

    return [r for r in repos if not r["fork"]][:TOP_N]

def lang_badge(language):
    if not language:
        return ""
    color = LANGUAGE_COLORS.get(language, "555555")
    label = language.replace(" ", "%20").replace("+", "%2B").replace("#", "%23")
    return f'<img src="https://img.shields.io/badge/{label}-{color}?style=flat-square&logoColor=white" alt="{language}">'

def build_cards(repos):
    rows = []
    pairs = [repos[i:i+2] for i in range(0, len(repos), 2)]

    for pair in pairs:
        cells = []
        for repo in pair:
            name = repo["name"]
            url = repo["html_url"]
            description = repo.get("description") or ""
            stars = repo.get("stargazers_count", 0)
            language = repo.get("language", "")
            badge = lang_badge(language)

            cell = f"""<td width="50%" valign="top">
  <h4><a href="{url}">{name}</a></h4>
  <p>{description}</p>
  <p>⭐ {stars} &nbsp; {badge}</p>
</td>"""
            cells.append(cell)

        # pad with empty cell if odd number
        if len(cells) == 1:
            cells.append('<td width="50%"></td>')

        rows.append("<tr>\n" + "\n".join(cells) + "\n</tr>")

    table = '<table width="100%">\n' + "\n".join(rows) + "\n</table>"
    return "\n" + table + "\n"

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
