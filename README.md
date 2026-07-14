# Charmed OpenSearch K8s Operator

[![CharmHub Badge](https://charmhub.io/opensearch-k8s/badge.svg)](https://charmhub.io/opensearch-k8s)
[![Release](https://github.com/canonical/opensearch-k8s-operator/actions/workflows/release.yaml/badge.svg?branch=2/edge)](https://github.com/canonical/opensearch-k8s-operator/actions/workflows/release.yaml)
[![Tests](https://github.com/canonical/opensearch-k8s-operator/actions/workflows/ci.yaml/badge.svg?branch=2/edge)](https://github.com/canonical/opensearch-k8s-operator/actions/workflows/ci.yaml)

## Description

The Charmed OpenSearch K8s Operator deploys and operates [OpenSearch](https://opensearch.org/) — a distributed search and analytics engine — on Kubernetes clusters using the [Juju](https://juju.is/) orchestration engine.

This operator provides an OpenSearch cluster, with automated cluster formation and role assignment, TLS certificate management, secure credential handling, backups and restores to S3/Azure/GCS object storage, in-place upgrades, and integration with the [Canonical Observability Stack](https://charmhub.io/topics/canonical-observability-stack). It packages the OpenSearch workload (Ubuntu-based) together with the charm logic that manages its lifecycle.

## Usage

Bootstrap a Kubernetes environment with [Juju](https://canonical.com/juju/docs/juju-cli/3.6/tutorial/#tutorial) (3.6 or later) and create a model:

```shell
juju add-model opensearch
```

Deploy the charm together with a TLS certificates provider (required to bootstrap the cluster), then relate them:

```shell
juju deploy self-signed-certificates
juju deploy opensearch-k8s --channel 2/edge
juju integrate opensearch-k8s self-signed-certificates
```

To retrieve the internal `admin` password and CA chain once the unit is active:

```shell
juju run opensearch-k8s/leader get-password
```

The `admin` credentials are for internal charm use. Applications should obtain their own credentials through the `opensearch-client` relation (for example via the [data-integrator](https://charmhub.io/data-integrator) charm) rather than using the admin account.

To remove the deployment, along with the persisted data:

```shell
juju destroy-model opensearch --destroy-storage
```

Warning: `--destroy-storage` will delete all data persisted by OpenSearch.

## Documentation

The full documentation for Charmed OpenSearch is available on [Charmhub / Discourse](https://discourse.charmhub.io/t/charmed-opensearch-documentation/9729).

Configuration options are documented in [`config.yaml`](./config.yaml) and charm actions in [`actions.yaml`](./actions.yaml). Common actions include `get-password`/`set-password`, `set-tls-private-key`, `create-backup`/`list-backups`/`restore`, and the upgrade orchestration actions (`pre-upgrade-check`, `resume-upgrade`, `force-upgrade`).

## Integrations

This charm supports several integrations (see [`metadata.yaml`](./metadata.yaml) for the full list). Notable ones include:

- **`opensearch-client`** (`opensearch_client` interface) — the recommended way for client applications to obtain access and credentials.
- **`certificates`** (`tls-certificates` interface) — a TLS certificates provider, required to bootstrap the cluster.
- **`s3-credentials` / `azure-credentials` / `gcs-credentials`** — object storage backends for backups and restores.
- **`peer-cluster` / `peer-cluster-orchestrator`** (`peer_cluster` interface) — orchestrate large, multi-application (main + failover) deployments.
- **`metrics-endpoint`, `grafana-dashboard`, `logging`** — observability via Prometheus, Grafana and Loki.
- **`oauth` / `jwt-configuration`** — external identity integration.

## OCI Images

This charm uses a pinned, tested version of the [`opensearch`](https://github.com/canonical/opensearch-rock) OCI image published to `ghcr.io/canonical/opensearch`. The exact image (currently OpenSearch 2.19.5 on Ubuntu 24.04) is referenced from [`metadata.yaml`](./metadata.yaml) under `resources.opensearch-image`.

## Security

Security issues in the Charmed OpenSearch K8s Operator can be reported through [private GitHub Security Advisories](https://github.com/canonical/opensearch-k8s-operator/security/advisories/new). Please do not file public issues for security vulnerabilities.

## Contributing

Please see the [Juju SDK documentation](https://juju.is/docs/sdk) for guidelines on developing enhancements to this charm, and read [CONTRIBUTING.md](https://github.com/canonical/opensearch-k8s-operator/blob/2/edge/CONTRIBUTING.md) for developer guidance. This project uses the Canonical Contributor License Agreement; the [CLA check](./.github/workflows/cla_checker.yaml) runs on every pull request.

## License

The Charmed OpenSearch K8s Operator is free software, distributed under the Apache Software License, version 2.0. See [LICENSE](./LICENSE) for more information.

OpenSearch is a trademark of the OpenSearch Project, a Series of LF Projects, LLC. See the [OpenSearch trademark and brand policy](https://opensearch.org/trademark-brand-policy/) for details.
