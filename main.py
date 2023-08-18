from utils import enumerate_local_repos, is_maven_project


def build_and_scan(repo_path: str) -> None:
    repo_type = "maven" if is_maven_project(repo_path) else "other"
    print(f"Found {repo_type} repo at {repo_path}")
    pass


def main(base_path: str) -> None:
    repo_lst = list(enumerate_local_repos(base_path))
    repo_lst.sort()
    for repo_path in repo_lst:
        build_and_scan(repo_path)


if __name__ == "__main__":
    main("~/Projects/git/vino9org")
