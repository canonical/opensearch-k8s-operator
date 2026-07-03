# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.
import os
from logging import getLogger
from pathlib import Path
from typing import Literal, TypeAlias

import pytest
import yaml
from _pytest.config.argparsing import Parser
from pytest_operator.plugin import OpsTest

Substrate: TypeAlias = Literal["vm", "k8s"]

logger = getLogger(__name__)


def pytest_addoption(parser: Parser):
    parser.addoption(
        "--substrate",
        action="store",
        help="Substrate to test, either vm or k8s",
        choices=("vm", "k8s"),
        default="k8s",
    )


CONFIG = yaml.safe_load(Path("./config.yaml").read_text())
ACTIONS = yaml.safe_load(Path("./actions.yaml").read_text())

METADATA = yaml.safe_load(Path("./metadata.yaml").read_text())


APP_NAME = METADATA["name"]

SERIES = "jammy"
UNIT_IDS = [0, 1, 2]
IDLE_PERIOD = 75


CONFIG_OPTS = {"profile": "testing"}
PRODUCTION_CONFIG_OPTS = {"profile": "production"}
CLIENT_CHARM = "client-charm"
TLS_CERTIFICATES_APP_NAME = "self-signed-certificates"
TLS_STABLE_CHANNEL = "1/stable"


def get_unit_ids(substrate: str) -> list[int]:
    """Return the unit ids supported by the test topology for a substrate."""
    # TODO: Expand K8s integration topology to multi-unit and remove this special-case.
    return [0] if substrate == "k8s" else UNIT_IDS


MODEL_CONFIG = {
    "logging-config": "<root>=INFO;unit=DEBUG",
    "update-status-hook-interval": "5m",
    "cloudinit-userdata": """postruncmd:
        - [ 'sysctl', '-w', 'vm.max_map_count=262144' ]
        - [ 'sysctl', '-w', 'fs.file-max=1048576' ]
        - [ 'sysctl', '-w', 'vm.swappiness=0' ]
        - [ 'sysctl', '-w', 'net.ipv4.tcp_retries2=5' ]
    """,
}


@pytest.fixture
def ubuntu_base() -> str:
    """Charm base version to use for testing."""
    return os.environ["CHARM_UBUNTU_BASE"]


@pytest.fixture
def series(ubuntu_base) -> str:
    """Workaround: python-libjuju does not support deploy base="ubuntu@22.04"; use series"""
    if ubuntu_base == "22.04":
        return "jammy"
    elif ubuntu_base == "24.04":
        return "noble"
    else:
        raise NotImplementedError


@pytest.fixture
def charm(ubuntu_base: str) -> str:
    """The OpenSearch charm path, to deploy charms, according to the substrate."""
    return f"./opensearch-k8s_ubuntu@{ubuntu_base}-amd64.charm"


@pytest.fixture
def charm_resources() -> dict[str, str]:
    """Resources to pass to `juju deploy` for the OpenSearch charm.

    Juju does not reliably auto-populate OCI image resources for locally packed charms in all
    environments. For the K8s substrate, explicitly provide the `opensearch-image` resource so the
    controller can fetch the image. The K8s workload image is published independently from the
    charm base variants, so we always use the upstream image declared in metadata.
    """
    upstream = (METADATA.get("resources") or {}).get("opensearch-image", {}).get("upstream-source")
    if not upstream:
        raise RuntimeError(
            "K8s test charm metadata is missing resources.opensearch-image.upstream-source"
        )

    return {"opensearch-image": upstream}


@pytest.fixture(autouse=True)
async def deploy_client_charm(ops_test: OpsTest):
    """Deploy the client charm."""
    if CLIENT_CHARM not in ops_test.model.applications:
        await ops_test.model.deploy(
            "./tests/dummy-client-charm/dummy-client-charm_amd64.charm",
            CLIENT_CHARM,
        )
        await ops_test.model.wait_for_idle(apps=[CLIENT_CHARM])


@pytest.fixture(scope="session")
def substrate(request) -> Substrate:
    """The substrate that we are testing."""
    if (option := request.config.option.substrate) != "k8s":
        raise ValueError(
            f"Unsupported substrate {option!r}: this is the k8s charm, only 'k8s' is supported"
        )
    return option
