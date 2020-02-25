import os
import unittest
import mock
from parameterized import parameterized_class
from configobj import ConfigObj

from unittest import TestCase

from kaos_cli.services.state_service import StateService
from kaos_cli.constants import CONFIG_PATH, KAOS_STATE_DIR


def state_service_test_inputs():

    """Returns different combinations of test input data/parameters that are used in the unit tests
    :parameter:

    :return: list
    a list of tuples consisting of different parameter combinations
    Ex: [(context1, param1), (context2, param2)..]

    """
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


@parameterized_class(('context', 'param'), state_service_test_inputs())
class TestStateService(TestCase):

    def instantiate_service(self):
        # Arrange
        self.state_service = StateService()

    def test_state_service_create(self):
        # Arrange
        self.instantiate_service()

        # Act
        self.state_service.create()

        # Assert
        self.assertTrue(os.path.exists(KAOS_STATE_DIR))

    def test_state_service_is_created(self):
        # Arrange
        self.instantiate_service()

        # Act
        is_created = self.state_service.is_created(KAOS_STATE_DIR)

        # Assert
        self.assertEqual(True, is_created)

    def test_state_service_list_providers(self):
        # Arrange
        self.instantiate_service()

        # Act
        provider_list = self.state_service.list_providers()

        # Assert
        self.assertEqual([], provider_list)

    def test_state_service_set(self):
        # Arrange
        self.instantiate_service()

        # Arrange
        if not isinstance(self.context, str):
            if self.context is None:
                self.context = {}
            else:
                self.context = str(self.context)

        # Act
        self.state_service.set('section', context=self.context)

        # Assert
        self.assertEqual(self.context, self.state_service.config['section']['context'])

    def test_state_service_get(self):
        # Arrange
        self.instantiate_service()

        if not isinstance(self.context, str):
            if self.context is None:
                self.context = {}
            else:
                self.context = str(self.context)

        self.state_service.set('section', context=self.context)

        # Act
        self.state_service.get('section', 'context')

        # Assert
        self.assertEqual(self.context, self.state_service.config['section']['context'])

    def test_state_service_set_sections(self):
        # Arrange
        self.instantiate_service()
        self.state_service.set('section', context=self.context)

        if not isinstance(self.param, str):
            if self.param is None:
                self.param = {}
            else:
                self.param = str(self.context)

        # Act
        self.state_service.set_section('section', 'subsection', param=self.param)

        # Assert
        self.assertEqual(self.param, self.state_service.config['section']['subsection']['param'])

    def test_state_service_get_sections(self):
        # Arrange
        self.instantiate_service()
        self.state_service.set('section', context=self.context)

        if not isinstance(self.param, str):
            if self.param is None:
                self.param = {}
            else:
                self.param = str(self.context)

        self.state_service.set_section('section', 'subsection', param=self.param)

        # Act
        self.state_service.get_section('section', 'subsection', 'param')

        # Assert
        self.assertEqual(self.state_service.config['section']['subsection'],
                         self.state_service.has_section('section', 'subsection'))

    def test_state_service_write(self):
        # Arrange
        self.instantiate_service()

        # Act
        self.state_service.write()

        # Assert
        self.assertEqual(self.state_service.config, ConfigObj(CONFIG_PATH))

    def test_state_service_has_section(self):
        # Arrange
        self.instantiate_service()

        self.state_service.set('section', context=self.context)
        self.state_service.set_section('section', 'subsection', param=self.param)

        # Act
        self.state_service.has_section('section', 'subsection')

        # Assert
        self.assertEqual(self.state_service.config['section']['subsection'],
                         self.state_service.has_section('section', 'subsection'))

    def test_state_service_remove(self):
        # Arrange
        self.instantiate_service()
        self.state_service.set('section', context=self.context)

        # Act
        self.state_service.remove('section')

        # Assert
        self.assertEqual("removed", "removed" if 'section' not in self.state_service.config else "not removed")

    def test_state_service_remove_section(self):
        # Arrange
        self.instantiate_service()
        self.state_service.set('section', context=self.context)
        self.state_service.set_section('section', 'subsection', param=self.param)

        # Act
        self.state_service.remove_section('section', 'subsection')

        is_removed = 'subsection' not in self.state_service.config['section']

        self.assertTrue(is_removed)


class TestStateServiceMocked(unittest.TestCase):

    def instantiate_service(self):
        # Arrange
        self.state_service = StateService()

    @mock.patch('shutil.rmtree')
    def test_method_remove_build_files(self, rm_mock):
            # Arrange
            self.instantiate_service()
            test_path = os.path.join(KAOS_STATE_DIR, 'test')
            rm_mock.return_value = 'REMOVED'

            # Act
            self.state_service.full_delete(test_path)

            # Assert
            rm_mock.assert_called_with(test_path, ignore_errors=True)
            self.assertEqual(rm_mock.return_value, 'REMOVED')

