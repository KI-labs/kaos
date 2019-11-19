# kaos Contribution Guidelines

Contributions are welcome, and they are greatly appreciated!

Please follow the kaos [Contributor Code of Conduct](CODE_OF_CONDUCT.md) for all your interactions.

# Types of Contributions

Please note that an [issue](https://github.com/KI-labs/kaos/issues) is **required** for all kaos contributions. The following is a list of the different types of contributions:

- _To help keep kaos running smoothly_
    - [Report Bugs](https://github.com/KI-labs/kaos/issues)
    - [Fix Bugs](https://github.com/KI-labs/kaos/issues)

- _To help improve existing kaos functionality_
    - [Change Request](https://github.com/KI-labs/kaos/issues)
    - [Implement Changes](https://github.com/KI-labs/kaos/issues)


- _To help increase kaos functionality_
    - [Feature Request](https://github.com/KI-labs/kaos/issues)
    - [Implement Features](https://github.com/KI-labs/kaos/issues)

# Development Environment

> kaos consists of an easy-to-use **user interface**, a multi-environment machine learning **backend** and a cloud agnostic **infrastructure**.

##
### Prerequisites

kaos is rather lightweight but **requires** the following (and on your `PATH`):

- [pipenv](https://docs.pipenv.org/en/latest/install/#installing-pipenv)
- [docker](https://docs.docker.com/install/)
- [Terraform](https://www.terraform.io/downloads.html)
- [Graphviz](https://www.graphviz.org/download/) (Contains `dot`)

##
### Installation

The recommended **development** installation of kaos is done automatically within a virtual environment using [pipenv](https://docs.pipenv.org/en/latest/install/#installing-pipenv). Note that the `--dev` option is required for installing the backend and integration tests.

```bash
$ git clone https://github.com/KI-labs/kaos.git
$ pipenv install --dev && pipenv shell
```
If a new dependency is added to the setup, then the existing pipenv can be updated by simply running
```bash
$ pipenv update
```

A successful installation will yield the following when inspecting all requirements within pipenv.

```bash
$ pipenv graph

kaos==1.0.0
  - ...
  - kaos-model [required: ==1.0.0, installed: 1.0.0]
  - ...
kaos-backend==1.0.0
  - ...
kaos-integration-tests==1.0.0
  - ...

```

##
### Further Information

Additional information is described independently for each layer in kaos.

- [user interface](../cli/README.md)
- [backend](../backend/README.md)
- [infrastructure](../infrastructure/README.md)
