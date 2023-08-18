import os
import sys
import tempfile

from dotenv import load_dotenv
from git import Repo

from utils import (
    ensure_sonar_project_tags,
    enumerate_local_repos,
    is_maven_project,
    run,
    sonar_options,
    tags_from_repo_path,
)

load_dotenv()

DRY_RUN = False
build_cmd = "mvn --batch-mode clean install"
sonar_cmd = f"mvn org.sonarsource.scanner.maven:sonar-maven-plugin:sonar {sonar_options()} -Dsonar.projectKey="


def build_and_scan(repo_path: str, tags):
    # print(f"build_and_scan: tags = {tags}")
    project_key = f"{tags['layer']}-{tags['repo']}"

    if tags["layer"] != "bff":
        return

    if is_maven_project(repo_path):
        try:
            pwd = os.getcwd()
            os.chdir(repo_path)
            print(f"sonar_cmd = {sonar_cmd + project_key}")
            if run(build_cmd, DRY_RUN) and run(sonar_cmd + project_key, DRY_RUN):
                ensure_sonar_project_tags(project_key, tags)
                print(f"==== Successfully scanned {repo_path} ====")
        finally:
            os.chdir(pwd)


def process_repo(repo_path: str):
    repo = Repo(repo_path)

    with tempfile.TemporaryDirectory(dir=os.path.expanduser("~/tmp")) as tmp_dir:
        cloned_repo = repo.clone(tmp_dir)

        # checkout the work branch
        if "develop" in cloned_repo.branches:
            cloned_repo.heads.develop.checkout()
        elif "main" in cloned_repo.branches:
            cloned_repo.heads.main.checkout()
        elif "master" in cloned_repo.branches:
            cloned_repo.heads.master.checkout()

        tags = tags_from_repo_path(repo_path)
        build_and_scan(tmp_dir, tags)


def main(base_path: str):
    repo_lst = list(enumerate_local_repos(base_path))
    repo_lst.sort()
    for repo_path in repo_lst:
        if repo_path.endswith("-chart.git"):
            continue

        process_repo(repo_path)


if __name__ == "__main__":
    base_path = "~/sbc/gitlab/securitybankph"
    if len(sys.argv) > 1:
        base_path = sys.argv[1]

    main(base_path)
