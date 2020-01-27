import pytest
from unittest import mock
from socket import error

from kaos_cli.utils.validators import validate_inputs, validate_unused_port, validate_index
from kaos_cli.exceptions.exceptions import MissingArgumentError


def test_validate_input():
    with pytest.raises(MissingArgumentError):
        validate_inputs([None, None], ["a, b"])


@mock.patch('socket.socket')
def test_validate_unused_port_returns_true_when_port_is_unused(socket_mock):
    # Arrange
    host_arg = 'random_host_string1'
    port_arg = 8328119231
    mocked_socket_obj = mock.MagicMock()
    mocked_socket_obj.bind.return_value = None
    socket_mock.return_value.__enter__.return_value = mocked_socket_obj

    # Act
    is_available = validate_unused_port(host=host_arg, port=port_arg)

    # Assert
    assert is_available is True
    mocked_socket_obj.bind.assert_called_once_with((host_arg, port_arg))


@mock.patch('socket.socket')
def test_validate_unused_port_returns_false_when_port_is_already_in_use(socket_mock):
    # Arrange
    host_arg = 'random_host_string2'
    port_arg = 9328119232
    mocked_socket_obj = mock.MagicMock()
    mocked_socket_obj.bind.side_effect = error()
    socket_mock.return_value.__enter__.return_value = mocked_socket_obj

    # Act
    is_available = validate_unused_port(host=host_arg, port=port_arg)

    # Assert
    assert is_available is False
    mocked_socket_obj.bind.assert_called_once_with((host_arg, port_arg))


def test_validate_index_does_not_exist():

    bad_examples = [(3, 4, 'template'), (3, 3, 'serve'), (3, -1, 'train')]
    good_examples = [(3, 0, 'template'), (3, 1, 'serve'), (3, 2, 'train')]

    for n, ind, command in bad_examples:
        with pytest.raises(IndexError, match=f"Index {ind} does not exist... Run `kaos {command} list` again"):
            validate_index(n=n, ind=ind, command=command)

    for n, ind, command in good_examples:
        validate_index(n=n, ind=ind, command=command)
