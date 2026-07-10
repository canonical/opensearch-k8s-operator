# Contributing

## Overview

This document outlines the processes and practices recommended for contributing enhancements to the Charmed OpenSearch K8s Operator.

- Generally, before developing enhancements to this charm, you should consider [opening an issue](https://github.com/canonical/opensearch-k8s-operator/issues) explaining your use case.
- If you would like to chat with us about your use cases or proposed implementation, you can reach us at the [Canonical Matrix public channel](https://matrix.to/#/#charmhub-data-platform:ubuntu.com) or on [Discourse](https://discourse.charmhub.io/).
- Familiarising yourself with the [Charmed Operator Framework](https://canonical.com/juju/docs/ops/latest/) library will help you a lot when working on new features or bug fixes.
- All enhancements require review before being merged. Code review typically examines code quality, test coverage, and user experience for Juju administrators of this charm.
- Please help us out in ensuring easy to review branches by rebasing your pull request branch onto the `2/edge` branch. This also avoids merge commits and creates a linear Git commit history.

## Developing

Install `tox`, `poetry`, and `charmcraft` (see the [charmcraft installation guide](https://juju.is/docs/sdk/install-charmcraft)):

```shell
pipx install tox
pipx install poetry
sudo snap install charmcraft --classic
```

Create a development environment:

```shell
poetry install
```

### Testing environments

This charm targets Kubernetes. A local Kubernetes substrate (MicroK8s) and Juju controller can be provisioned with [concierge](https://github.com/canonical/concierge); the exact configuration used by CI is in [`concierge-microk8s.yaml`](./concierge-microk8s.yaml) and [`spread.yaml`](./spread.yaml).

```shell
sudo snap install --classic concierge
concierge prepare -c concierge-microk8s.yaml
```

## Build charm

Build the charm with:

```shell
charmcraft pack
```

### Testing

```shell
tox run -e format          # update your code according to linting rules
tox run -e lint            # code style checks (flake8, codespell, shellcheck)
tox run -e integration     # integration tests
```

## Deploy

Create a model and (optionally) tune its update-status interval:

```shell
juju add-model dev
juju model-config logging-config="<root>=INFO;unit=DEBUG"
juju model-config update-status-hook-interval=1m
```

Deploy the freshly built charm with a TLS relation:

```shell
juju deploy self-signed-certificates --channel=latest/stable --show-log --verbose
juju config \
    self-signed-certificates \
    ca-common-name="CN_CA" \
    certificate-validity=365 \
    root-ca-validity=365
juju deploy ./opensearch-k8s_ubuntu@24.04-amd64.charm \
    --resource opensearch-image=ghcr.io/canonical/opensearch:2.19.5-24.04_edge \
    --show-log --verbose
juju integrate self-signed-certificates opensearch-k8s
```

Note: The `self-signed-certificates` charm is convenient for development but is not recommended for production clusters; see the [TLS Certificates documentation](https://charmhub.io/topics/security-with-x-509-certificates) for production-ready configurations.

## Canonical Contributor Agreement

Canonical welcomes contributions to the Charmed OpenSearch K8s Operator. Please check out our [contributor agreement](https://ubuntu.com/legal/contributors) if you're interested in contributing to the solution. The [CLA check](./.github/workflows/cla_checker.yaml) runs on every pull request.
