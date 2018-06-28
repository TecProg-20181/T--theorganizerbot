from github import Github

GITHUB_USER = ""
GITHUB_PASSWORD = ""
ORGANIZATION = "TecProg-20181"
REPO = "T--theorganizerbot"

def push_github_issue(issue_title):
    try:
        g = Github(GITHUB_USER, GITHUB_PASSWORD)
        repo = g.get_organization(ORGANIZATION).get_repo(REPO)
        repo.create_issue(issue_title)
    except: #github.GithubException.UnknownObjectException:
        return 0
