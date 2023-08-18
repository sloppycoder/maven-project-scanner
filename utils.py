import os
from typing import Iterator

from git import InvalidGitRepositoryError, Repo


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
