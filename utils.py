import os
import re
import shlex
import subprocess
import sys
from typing import Iterator

import requests
from git import InvalidGitRepositoryError, Repo

sonar_url = "http://localhost:9000/sonarqube"
sonar_analysis_token = "sqa_986a47d4af1ab9767f6f656b8ac90f41ca580f89"
sonar_api_token = "Yc8rMcvzhcUtNri"
# sonar_analysis_token = os.environ.get("SONAR_ANALYSIS_TOKEN")
# actually the password, for some reason cannot create api token
# sonar_api_token = os.environ.get("SONAR_API_TOKEN")


def sonar_options() -> str:
    return f"-Dsonar.host.url={sonar_url} -Dsonar.token={sonar_analysis_token}"


def ensure_sonar_project_tags(project_key: str, tags: dict[str, str]):
    new_tags = [f"{key}#{value}" for key, value in sorted(tags.items())]
    response = requests.post(
        f"{sonar_url}/api/project_tags/set",
        auth=("admin", sonar_api_token),
        data={
            "project": project_key,
            "tags": ",".join(new_tags),
        },
    )

    if response.ok:
        return True

    print(f"*** Got {response.status_code} when trying to update tags for {project_key}")
    return False


def run(command: str, dry_run: bool) -> int:
    cwd = os.getcwd()
    print(f"pwd={cwd}\n{command}")

    if dry_run:
        return True

    ret = subprocess.call(shlex.split(command), timeout=300.00)
    if ret == 0:
        return True
    else:
        print(f"*** return code {ret}", file=sys.stderr)
        return False


def tags_from_repo_path(repo_path: str) -> dict[str, str]:
    parts = ["other", "other"]
    if "securitybankph/rtd/bbx/" in repo_path:
        parts = repo_path.split("securitybankph/rtd/bbx/")[1].split("/")
    elif "securitybankph/shared/bbx/" in repo_path:
        parts = repo_path.split("/securitybankph/shared/bbx/")[1].split("/")

    if len(parts) >= 2:
        layer = parts[0]
        if layer == "accenture":
            layer = "fe"
        repo = re.sub(r"\.git$", "", parts[-1])
    else:
        # e.g. parts = ['dsl.git']
        layer = "other"
        repo = re.sub(r"\.git$", "", parts[0])

    return {"proj": "sbc-bbx", "layer": layer, "repo": repo}


def is_git_repo(path: str) -> bool:
    try:
        repo = Repo(path)
        repo.head.commit
        return True
    except InvalidGitRepositoryError:
        # this exception happens when the path is not a Git repo
        return False
    except ValueError:
        # this exception happens when a repo is empty
        return False


def is_maven_project(path: str) -> bool:
    return os.path.exists(path + "/pom.xml")


def enumerate_local_repos(base_dir: str) -> Iterator[str]:
    for root, dirs, _ in os.walk(os.path.expanduser(base_dir), topdown=True):
        if ".git" in dirs:
            dirs.remove(".git")

        for dd in dirs:
            abs_path = os.path.abspath(root + "/" + dd)
            if is_git_repo(abs_path):
                yield abs_path
