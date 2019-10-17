import pytest

from kaos_cli.utils.validators import validate_inputs
from kaos_cli.exceptions.exceptions import MissingArgumentError


def test_validate_input():
    with pytest.raises(MissingArgumentError):
        validate_inputs([None, None], ["a, b"])
