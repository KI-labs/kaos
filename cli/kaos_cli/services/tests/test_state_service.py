import os
import time
from parameterized import parameterized
from configobj import ConfigObj

from unittest import TestCase

from kaos_cli.services.state_service import StateService
from kaos_cli.constants import CONFIG_PATH, KAOS_STATE_DIR


def state_service_test_inputs():
    return [
        (
            'context1', 'param1'
        ),
        (
            'context2', 'param2'
        ),
        (
            '', 'param3'
        ),
        (
            'context4', ''
        ),
        (
            '', ''
        ),
        (
            {}, 'param6'
        ),
        (
            'context7', {}
        ),
        (
            {}, {}
        ),
        (
            '', {}
        ),
        (
            {}, ''
        ),
        (
            None, 'param11'
        ),
        (
            'context11', None
        ),
        (
            None, None
        ),
        (
            {}, None
        ),
        (
            None, {}
        ),
        (
            '', None
        ),
        (
            None, ''
        ),
        (
            1, 'param18'
        ),
        (
            'context', 2
        ),
        (
            3, {}
        ),
        (
            {}, 4
        ),
        (
            5, ''
        ),
        (
            '', 6
        ),
        (
            7, None
        ),
        (
            None, 8
        ),

    ]


class TestStateService(TestCase):

    # Arrange
    TestCase.state_service = StateService()
    TestCase.switch = False

    def test_state_service_create(self):

        # Act
        TestCase.state_service.create()

        # Assert
        self.assertTrue(os.path.exists(KAOS_STATE_DIR))

    def test_state_service_is_created(self):

        # Act
        TestCase.state_service.is_created(KAOS_STATE_DIR)

        # Assert
        self.assertEqual(True, TestCase.state_service.is_created(KAOS_STATE_DIR))

    def test_state_service_list_providers(self):

        # Act
        provider_list = TestCase.state_service.list_providers()

        # Assert
        self.assertEqual([], provider_list)

    @parameterized.expand(state_service_test_inputs)
    def test_state_service_set_and_get(self, context, param):

        # Arrange
        if not isinstance(context, str):
            TestCase.switch = True
            if context is None:
                context = {}
            else:
                context = str(context)

        # Act
        TestCase.state_service.set('section', context=context)

        # Assert
        self.assertEqual(context, TestCase.state_service.config['section']['context'])

        # Act
        TestCase.state_service.get('section', 'context')

        # Assert
        self.assertEqual(context, TestCase.state_service.config['section']['context'])

    @parameterized.expand(state_service_test_inputs)
    def test_state_service_set_and_get_sections(self, context, param):

        # Arrange
        if not isinstance(param, str):
            TestCase.switch = True
            if param is None:
                param = {}
            else:
                param = str(context)

        # Act
        TestCase.state_service.set_section('section', 'subsection', param=param)

        # Assert
        self.assertEqual(param, TestCase.state_service.config['section']['subsection']['param'])

        # Act
        TestCase.state_service.get_section('section', 'subsection', 'param')

        # Assert
        self.assertEqual(TestCase.state_service.config['section']['subsection'],
                         TestCase.state_service.has_section('section', 'subsection'))

    def test_state_service_write(self):

        # Act
        TestCase.state_service.write()

        # Assert
        self.assertEqual(TestCase.state_service.config, ConfigObj(CONFIG_PATH))

    @parameterized.expand(state_service_test_inputs)
    def test_state_service_has_section(self, context, param):

        # Arrange
        TestCase.state_service.set('section', context=context)
        TestCase.state_service.set_section('section', 'subsection', param=param)

        if not TestCase.switch:
            # Act
            TestCase.state_service.has_section('section', 'subsection')

            # Assert
            self.assertEqual(TestCase.state_service.config['section']['subsection'],
                             TestCase.state_service.has_section('section', 'subsection'))

            # Act
            TestCase.state_service.remove_section('section', 'subsection')

            # Assert
            self.assertEqual("removed",
                             "removed" if 'subsection' not in TestCase.state_service.config['section'] else "not removed")

    def test_state_service_remove(self):

        # Act
        TestCase.state_service.remove('section')

        # Assert
        self.assertEqual("removed", "removed" if 'section' not in TestCase.state_service.config else "not removed")

    def test_state_service_provider_delete(self):

        # Act
        TestCase.state_service.provider_delete(CONFIG_PATH)

        # Assert
        self.assertTrue(not os.path.exists(CONFIG_PATH))














