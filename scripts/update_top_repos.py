import os
import re
import json
import urllib.request

USERNAME = "argahutama"
MIN_STARS = 10
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

GRAPHQL_QUERY = """
query($username: String!) {
  user(login: $username) {
    repositoriesContributedTo(
      first: 100
      contributionTypes: [COMMIT, PULL_REQUEST]
      includeUserRepositories: false
    ) {
      nodes {
        nameWithOwner
        url
        description
        stargazerCount
        isPrivate
        primaryLanguage {
          name
        }
      }
    }
  }
}
"""

token = os.environ.get("GITHUB_TOKEN", "")

def fetch_contributed_repos():
    payload = json.dumps({
        "query": GRAPHQL_QUERY,
        "variables": {"username": USERNAME}
    }).encode()

    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
    )

    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read())

    nodes = data["data"]["user"]["repositoriesContributedTo"]["nodes"]

    repos = [
        r for r in nodes
        if not r["isPrivate"] and r["stargazerCount"] > MIN_STARS
    ]

    return sorted(repos, key=lambda r: r["stargazerCount"], reverse=True)

def lang_badge(language):
    if not language:
        return ""
    color = LANGUAGE_COLORS.get(language, "555555")
    label = language.replace(" ", "%20").replace("+", "%2B").replace("#", "%23")
    return f'<img src="https://img.shields.io/badge/{label}-{color}?style=flat-square&logoColor=white" alt="{language}">'

def star_badge(count):
    return f'<img src="https://img.shields.io/badge/★%20{count}-FFC83D?style=flat-square&logoColor=black" alt="stars">'

def build_cards(repos):
    rows = []
    pairs = [repos[i:i+2] for i in range(0, len(repos), 2)]

    for pair in pairs:
        cells = []
        for repo in pair:
            name = repo["nameWithOwner"]
            url = repo["url"]
            description = repo.get("description") or ""
            stars = repo["stargazerCount"]
            language = repo["primaryLanguage"]["name"] if repo.get("primaryLanguage") else ""
            badges = " ".join(filter(None, [star_badge(stars), lang_badge(language)]))
            desc_line = f"<br><sub>{description}</sub>" if description else ""

            cell = f'<td align="center" width="50%" valign="top"><a href="{url}"><b>{name}</b></a>{desc_line}<br><br>{badges}</td>'
            cells.append(cell)

        if len(cells) == 1:
            cells.append('<td width="50%"></td>')

        rows.append("<tr>" + "".join(cells) + "</tr>")

    table = '<p align="center"><table width="100%">' + "".join(rows) + "</table></p>"
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
    repos = fetch_contributed_repos()
    if not repos:
        print("No qualifying contributions found.")
    else:
        cards = build_cards(repos)
        update_readme(cards)
        print(f"Updated with {len(repos)} repos.")
