import pytest


def pytest_addoption(parser):
    parser.addoption("--k8s-port", action="store")


@pytest.fixture
def params(request):
    k8s_port = request.config.getoption("--k8s-port")
    return {"k8s_port": k8s_port}
