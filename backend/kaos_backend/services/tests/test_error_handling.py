import pytest

from kaos_backend.util.error_handling import recover


class MyFancyException(Exception):
    pass


class MyFancierException(Exception):
    pass


def test_recover_no_recover(mocker):
    m = mocker.Mock()

    def f():
        pass

    recover(f, [], m)
    m.assert_not_called()


def test_recover_with_recover(mocker):
    m = mocker.Mock()

    def f():
        raise MyFancyException

    recover(f, [MyFancyException], m)
    m.assert_called_once()


def test_recover_not_catched(mocker):
    m = mocker.Mock()

    def f():
        raise MyFancyException

    with pytest.raises(MyFancyException):
        recover(f, [], m)
    m.assert_not_called()


def test_recover_exception_in_recover_f():
    def f():
        raise MyFancyException

    def recover_f():
        raise MyFancierException

    with pytest.raises(MyFancierException):
        recover(f, [MyFancyException], recover_f)
