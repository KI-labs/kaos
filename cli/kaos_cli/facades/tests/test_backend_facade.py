import os
import unittest
import mock
from parameterized import parameterized
from unittest import TestCase, skip

from kaos_cli.facades.backend_facade import BackendFacade
from kaos_cli.services.terraform_service import TerraformService
from kaos_cli.services.state_service import StateService
from kaos_cli.services.terraform_service import Command
from kaos_cli.constants import CONFIG_PATH, ACTIVE, DEFAULT, CONTEXTS, KAOS_STATE_DIR

common = ('backend', 'url', 'token', 'infrastructure', 'kubeconfig', 'user')


def backend_facade_test_inputs():

    return [
        ('DOCKER',) + common,
        ('GCP',) + common,
        ('AWS',) + common,
        ('Remote1',) + common,
    ]


class TestBackendFacade(TestCase):

    @staticmethod
    def derive_context(cloud):
        env_list = ['', 'dev', 'stage', 'prod']
        for env in env_list:
            return cloud + '_' + env

    def manipulate_context_list(self, context_list):
        self.state_service.set(CONTEXTS, environments=context_list)

    def arrange_test_fixtures(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        # Instantiation
        self.state_service = StateService()
        self.command = Command()
        self.tf_service = TerraformService(cmd=self.command)

        # Arrange
        # Initialization
        self.state_service.set(ACTIVE, environment=environment)
        self.state_service.set(CONTEXTS, environments=environment)
        self.state_service.set(DEFAULT, user=user)
        self.state_service.set(environment)
        self.state_service.set_section(environment, backend, url=url, token=token)
        self.state_service.set_section(environment, infra, kubeconfig=kubeconfig)
        self.facade = BackendFacade(self.state_service, self.tf_service)

    @parameterized.expand(backend_facade_test_inputs)
    def test_method_get_active_context(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)

        test_inputs_active_contexts = [None, '', environment]

        for env in test_inputs_active_contexts:
            self.state_service.set(ACTIVE, environment=env)

            # Act
            active_context = self.facade.get_active_context()

            # Assert
            self.assertEqual(active_context, self.facade.state_service.get(ACTIVE, 'environment'))

    @parameterized.expand(backend_facade_test_inputs)
    def test_property_active_context(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)

        # Act
        active_context_property = self.facade.active_context

        # Assert
        self.assertEqual(active_context_property, environment)

    @parameterized.expand(backend_facade_test_inputs)
    def test_property_url(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)

        # Act
        url_property = self.facade.url

        # Assert
        self.assertEqual(url_property, url)

    @parameterized.expand(backend_facade_test_inputs)
    def test_property_user(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)

        # Act
        user_property = self.facade.user

        # Assert
        self.assertEqual(user_property, user)

    @parameterized.expand(backend_facade_test_inputs)
    def test_property_token(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)

        # Act
        token_property = self.facade.token

        # Assert
        self.assertEqual(token_property, token)

    @parameterized.expand(backend_facade_test_inputs)
    def test_property_kubeconfig(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)

        # Act
        kubeconfig_property = self.facade.kubeconfig

        # Assert
        self.assertEqual(kubeconfig_property, kubeconfig)

    @skip("Skipping test for init method")
    @parameterized.expand(backend_facade_test_inputs)
    def test_method_init(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)

        # Act
        ## TODO: Rectify the following assertions after fixing the dir_build path for init() after merging PR #95
        # self.facade.init(url, token)

        # Assert
        self.assertEqual(0, 0)
        self.assertEqual(1, 1)

    @parameterized.expand(backend_facade_test_inputs)
    def test_method_list(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)

        # Act
        list_result = self.facade.list()
        context = list_result[0]['context']

        # Assert
        self.assertEqual(context, environment)

        # Arrange (modify the contexts list)
        test_inputs = [None, ['DOCKER', 'GCP', 'AWS']]
        for test_input in test_inputs:
            self.state_service.set(CONTEXTS, environments=test_input)

            # Act
            list_result = self.facade.list()

            if len(list_result) > 0:
                context = [x['context'] for x in list_result]
            else:
                context = list_result
                test_input = []

            # Assert
            print("context", context)
            self.assertEqual(context, test_input)

    @parameterized.expand(backend_facade_test_inputs)
    def test_method_get_active_context(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)

        # Act
        active_context = self.facade.get_active_context()

        # Assert
        self.assertEqual(active_context, environment)

    @parameterized.expand(backend_facade_test_inputs)
    def test_method_get_context_info(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)
        index = 0
        cloud_env = self.derive_context(environment)

        # Act
        context_info = self.facade.get_context_info(cloud_env, index)
        provider = context_info['provider']

        # Assert
        self.assertEqual(provider, environment)

    @parameterized.expand(backend_facade_test_inputs)
    def test_method_get_context_by_index(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)
        index = 0

        cloud_env = self.derive_context(environment)

        context_info = self.facade.get_context_info(cloud_env, index)

        # Act
        context = self.facade.get_context_by_index([context_info], index)

        # Assert
        self.assertEqual(context, cloud_env)

    @parameterized.expand(backend_facade_test_inputs)
    def test_method_jsonify_context_list(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)

        cloud_env = self.derive_context(environment)

        # Act
        context_info = self.facade.jsonify_context_list(cloud_env)
        provider = context_info[0]['provider']

        # Assert
        self.assertEqual(provider, environment)

    @parameterized.expand(backend_facade_test_inputs)
    def test_method_set_context_by_context(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)

        self.facade.state_service.create()
        with open(CONFIG_PATH, 'wb') as f:
            f.close()

        # Act
        is_set = self.facade.set_context_by_context(environment)

        # Assert
        self.assertTrue(is_set)

        # Act
        is_set = self.facade.set_context_by_context('invalid_environment')

        # Assert
        self.assertFalse(is_set)

    @parameterized.expand(backend_facade_test_inputs)
    def test_method_set_context_by_index(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)

        valid_index = 0
        invalid_index = 1

        # Act
        is_set, current_context = self.facade.set_context_by_index(valid_index)

        # Assert
        self.assertTrue(is_set)
        self.assertEqual(current_context, environment)

        # Act
        is_set, current_context = self.facade.set_context_by_index(invalid_index)

        # Assert
        self.assertFalse(is_set)
        self.assertIsNone(current_context)

    @parameterized.expand(backend_facade_test_inputs)
    def test_method_set_context_list(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)

        # Act
        self.facade._set_context_list(environment)
        list_result = self.facade.list()
        contexts = [x['provider'] for x in list_result]

        # Assert
        self.assertIn(environment, contexts)

    @parameterized.expand(backend_facade_test_inputs)
    def test_method_unset_context_list(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)

        # Act
        self.facade._unset_context_list(environment)
        list_result = self.facade.list()
        contexts = [x['provider'] for x in list_result]

        # Assert
        self.assertNotIn(environment, contexts)

    @parameterized.expand(backend_facade_test_inputs)
    def test_method_set_active_context(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)

        # Act
        self.facade._set_active_context(environment)
        active_context = self.facade.state_service.get(ACTIVE, 'environment')

        # Assert
        self.assertEqual(active_context, environment)

    @parameterized.expand(backend_facade_test_inputs)
    def test_method_remove_section(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)

        # Act
        self.facade._remove_section(environment)
        config = self.facade.state_service.config

        # Assert
        self.assertNotIn(environment, config)

    @parameterized.expand(backend_facade_test_inputs)
    def test_method_remove_section(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)

        # Act
        self.facade._remove_section(environment)
        config = self.facade.state_service.config

        # Assert
        self.assertNotIn(environment, config)

    @parameterized.expand(backend_facade_test_inputs)
    def test_method_deactivate_context(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        self.arrange_test_fixtures(environment, backend, url, token, infra, kubeconfig, user)

        self.facade.state_service.create()
        with open(CONFIG_PATH, 'wb') as f:
            f.close()

        # Act
        self.facade._deactivate_context()
        active_context = self.facade.state_service.get(ACTIVE, 'environment')

        # Assert
        self.assertIsNone(active_context)


class TestBackendFacadeMocked(unittest.TestCase):

    def arrange_test_fixtures(self, environment, backend, url, token, infra, kubeconfig, user):
        # Arrange
        # Instantiation
        self.state_service = StateService()
        self.command = Command()
        self.tf_service = TerraformService(cmd=self.command)

        # Arrange
        # Initialization
        self.state_service.set(ACTIVE, environment=environment)
        self.state_service.set(CONTEXTS, environments=environment)
        self.state_service.set(DEFAULT, user=user)
        self.state_service.set(environment)
        self.state_service.set_section(environment, backend, url=url, token=token)
        self.state_service.set_section(environment, infra, kubeconfig=kubeconfig)
        self.facade = BackendFacade(self.state_service, self.tf_service)

    @mock.patch('shutil.rmtree')
    def test_method_remove_build_files(self, rm_mock):
            # Arrange
            environment = "DOCKER"

            ## common = ('backend', 'url', 'token', 'infrastructure', 'kubeconfig', 'user')
            self.arrange_test_fixtures(environment, common[0], common[1], common[2], common[3], common[4], common[5])
            test_path = os.path.join(KAOS_STATE_DIR, 'test')
            rm_mock.return_value = 'REMOVED'

            # Act
            self.facade._remove_build_files(test_path)

            # Assert
            rm_mock.assert_called_with(test_path, ignore_errors=True)
            self.assertEqual(rm_mock.return_value, 'REMOVED')
