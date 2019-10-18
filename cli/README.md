# kaos

The command line interface (CLI) aims to **simplify usage of the underlying core of kaos**.

##
### Testing

Standardized testing of the CLI consists of [pytest](https://docs.pytest.org/en/latest/) and [tox](https://tox.readthedocs.io/en/latest/). All significant functionality must come with test coverage. Please run tox within an isolated Docker environment using the supplied make file.

```bash
make test-unit-docker
```
