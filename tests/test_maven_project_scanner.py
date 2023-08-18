from utils import ensure_sonar_project_tags, tags_from_repo_path


def test_tags_from_repo_path():
    assert tags_from_repo_path("home/user/sss/gitlab/securitybankph/shared/bbx/accenture/bbx-base-pom.git") == {
        "layer": "fe",
        "repo": "bbx-base-pom",
    }
    assert tags_from_repo_path("home/user/sss/gitlab/securitybankph/rtd/bbx/bff/accounts-service.git") == {
        "layer": "bff",
        "repo": "accounts-service",
    }
    assert tags_from_repo_path("/home/lee/sbc/gitlab/securitybankph/rtd/bbx/bff/local-payment-service-chart.git") == {
        "layer": "bff",
        "repo": "local-payment-service-chart",
    }


def test_ensure_sonar_project_tags():
    assert ensure_sonar_project_tags("cs-limit-service", {"proj": "bbx", "layer": "cs", "repo": "limit-service"})
