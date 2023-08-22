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

jqa_config = """
jqassistant:
  skip: false

  plugins:
    - group-id: org.jqassistant.plugin
      artifact-id: jqassistant-spring-plugin
      version: 2.0.0
      type: jar

  store:
    uri: bolt://localhost
    remote:
      username: neo4j
      password: password


  scan:
    reset: false
    continue-on-error: true

"""


def run_jqassistant(repo_path: str):
    if os.environ.get("SKIP_JQA", "N") == "Y":
        return True

    with open(f"{repo_path}/.jqassistant.yml", "w") as f:
        f.write(jqa_config)

    jqa_cmd = "mvn com.buschmais.jqassistant:jqassistant-maven-plugin:2.0.6"
    return run(f"{jqa_cmd}:scan") and run(f"{jqa_cmd}:analyze")


def mvn_build_and_scan(repo_path: str, sonar_opts: str):
    build_cmd = "mvn --batch-mode clean install"
    sonar_cmd = "mvn org.sonarsource.scanner.maven:sonar-maven-plugin:3.9.1.2184:sonar "
    try:
        pwd = os.getcwd()
        os.chdir(repo_path)
        return run(build_cmd) and run(sonar_cmd + sonar_opts) and run_jqassistant(repo_path)
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

        if not is_maven_project(cloned_repo.working_dir):
            return

        tags = tags_from_repo_path(repo_path)
        project_key = f"{tags['layer']}-{tags['repo']}"

        if tags["layer"] not in ["cs", "bff", "cds"]:
            return

        # uncomment to test with 1 repo only
        # if tags["repo"] != "limit-service":
        #     return

        sonar_opts = sonar_options(repo_path, project_key)
        print(f"sonar_opts={sonar_opts}")
        mvn_build_and_scan(tmp_dir, sonar_opts)
        ensure_sonar_project_tags(project_key, tags)


def main(base_path: str):
    repo_lst = list(enumerate_local_repos(base_path))
    repo_lst.sort()
    for repo_path in repo_lst:
        if repo_path.endswith("-chart.git"):
            continue

        process_repo(repo_path)


if __name__ == "__main__":
    base_path = "/home/git/securitybankph"
    if len(sys.argv) > 1:
        base_path = sys.argv[1]

    # print(os.environ)
    main(base_path)
