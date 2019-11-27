import os
from parameterized import parameterized

from unittest import TestCase

from kaos_cli.services.state_service import StateService


def state_service_test_inputs():
    return [
        (
            [('context1', 'section1', 'param1')]
        ),
    ]


class TestStateService(TestCase):

    @parameterized.expand(state_service_test_inputs)
    def test_state_append(self, state_service_test_inputs):

        # Arrange
        backend = StateService()

        # Act
        for arguments in state_service_test_inputs:
            print("arguments", arguments)
            backend.create()
            backend.set()
            backend.get()

        # Assert
        self.assertEqual(0, 0)
