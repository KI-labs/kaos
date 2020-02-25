import os
from parameterized import parameterized

from unittest import TestCase

from kaos_cli.services.terraform_service import TerraformService
from kaos_cli.services.terraform_service import Command
from kaos_cli.utils.helpers import verbose_run
from kaos_cli.constants import KAOS_STATE_DIR


def test_inputs_append_data():

    """Returns different combinations of test input data/parameters that are used in the unit tests
    :parameter:

    :return: list
    a list of tuples consisting of different set of parameter combinations
    Ex: [(command1), ([command1, command2]), ([command1, command2, command3])..]

    """

    return [
        (
            [],
        ),
        (
            ['echo <---first_echo_command--->'],
        ),
        (
            ['echo <---first_echo_command--->', 'echo <--- executing the second echo command --->'],
        ),
        (
            ['echo <--- executing the first echo command --->', 'echo <--- executing the second echo command --->',
             'echo <--- executing the third echo command --->'],
        ),
    ]


def test_inputs_execute_data():

    """Returns different combinations of test input data/parameters that are used in the unit tests
    :parameter:

    :return: list
    a list of tuples consisting of different parameter combinations
    Ex: [(command1), ([command1, command2]), ([command1, command2, command3])..]

    """
    return [
        (
            ['echo <---first_echo_command--->', 'echo <--- executing the second echo command --->'],
        ),
        (
            ['echo <--- executing the first echo command --->', 'echo <--- executing the second echo command --->',
             'echo <--- executing the third echo command --->'],
        ),
    ]


class TestTerraformService(TestCase):

    @parameterized.expand(test_inputs_append_data)
    def test_command_append(self, command_append_data):

        # Arrange
        command = Command()

        # Act
        for cmd in command_append_data:
            command.append(cmd)

        # Assert
        self.assertEqual(command.history, command_append_data)

    @parameterized.expand(test_inputs_execute_data)
    def test_command_execute(self, command_execute_data):

        # Arrange
        command = Command()

        # Act
        for cmd in command_execute_data:
                command.append(cmd)

        exitcode, out, err = command.execute()

        # Assert
        self.assertEqual(exitcode, 0)

    @parameterized.expand(test_inputs_append_data)
    def test_command_clear(self, command_append_data):

        # Arrange
        command = Command()

        # Act
        for cmd in command_append_data:
            command.append(cmd)

        command.clear()

        # Assert
        self.assertEqual(command.history, [])

    @parameterized.expand(test_inputs_execute_data)
    def test_command_verbose_true(self, command_execute_data):

        # Arrange
        command = Command()
        verbose = True

        # Act
        for cmd in command_execute_data:
                command.set_verbose(verbose)

                # Assert
                self.assertIsInstance(command.run_cmd, type(command.run_cmd))
                self.assertEqual(command.run_cmd.func, verbose_run)
                self.assertEqual(command.run_cmd.args[0], True)

    @parameterized.expand(test_inputs_execute_data)
    def test_command_verbose_false(self, command_execute_data):

        # Arrange
        command = Command()
        verbose = False

        # Act
        for cmd in command_execute_data:
                command.set_verbose(verbose)

                # Assert
                self.assertIsInstance(command.run_cmd, type(command.run_cmd))
                self.assertEqual(command.run_cmd.func, verbose_run)
                self.assertEqual(command.run_cmd.args[0], False)

    @parameterized.expand(test_inputs_execute_data)
    def test_tf_service_set_verbose_True(self, command_execute_data):

        # Arrange
        verbose = True
        command = Command()

        # Act
        for cmd in command_execute_data:
            command.append(cmd)

        tf_service = TerraformService(cmd=command)
        tf_service.set_verbose(verbose)

        # Assert
        self.assertIsInstance(tf_service.set_verbose, type(tf_service.set_verbose))
        self.assertIsInstance(tf_service.cmd.set_verbose, type(tf_service.cmd.set_verbose))
        self.assertEqual(tf_service.cmd.run_cmd.func, verbose_run)
        self.assertEqual(tf_service.cmd.run_cmd.args[0], True)

    @parameterized.expand(test_inputs_execute_data)
    def test_tf_service_set_verbose_False(self, command_execute_data):

        # Arrange
        verbose = False
        command = Command()

        # Act
        for cmd in command_execute_data:
            command.append(cmd)

        tf_service = TerraformService(cmd=command)
        tf_service.set_verbose(verbose)

        # Assert
        self.assertIsInstance(tf_service.set_verbose, type(tf_service.set_verbose))
        self.assertIsInstance(tf_service.cmd.set_verbose, type(tf_service.cmd.set_verbose))
        self.assertEqual(tf_service.cmd.run_cmd.func, verbose_run)
        self.assertEqual(tf_service.cmd.run_cmd.args[0], False)

    def test_tf_service_init(self):

        # Arrange
        command = Command()
        tf_service = TerraformService(cmd=command)

        dir_path = KAOS_STATE_DIR
        derived_path = os.path.join(os.getcwd(), KAOS_STATE_DIR)
        command_history = [f"terraform init {derived_path} "]

        # Act
        tf_service.init(dir_path)

        # Assert
        self.assertEqual(tf_service.cmd.history, command_history)

    def test_tf_service_new_workspace(self):

        # Arrange
        command = Command()
        tf_service = TerraformService(cmd=command)

        env = 'prod'
        directory = os.path.join(os.getcwd(), KAOS_STATE_DIR)
        command_history = [f"terraform workspace new {env} {directory}"]

        # Act
        tf_service.new_workspace(directory, env)

        # Assert
        self.assertEqual(tf_service.cmd.history, command_history)

    def test_tf_service_select_workspace(self):

        # Arrange
        command = Command()
        tf_service = TerraformService(cmd=command)

        env = 'prod'
        directory = os.path.join(os.getcwd(), KAOS_STATE_DIR)
        command_history = [f"terraform workspace select {env} {directory}"]

        # Act
        tf_service.select_workspace(directory, env)

        # Assert
        self.assertEqual(tf_service.cmd.history, command_history)

    def test_tf_service_plan(self):

        # Arrange
        command = Command()
        tf_service = TerraformService(cmd=command)

        env = 'prod'
        directory = os.path.join(os.getcwd(), KAOS_STATE_DIR)
        command_history = [f"terraform workspace select {env} {directory}"]

        # Act
        tf_service.select_workspace(directory, env)

        # Assert
        self.assertEqual(tf_service.cmd.history, command_history)

    def test_tf_service_apply(self):

        # Arrange
        command = Command()
        tf_service = TerraformService(cmd=command)

        extra_vars = 'prod'
        directory = os.path.join(os.getcwd(), KAOS_STATE_DIR)
        command_history = [f"terraform apply --var-file={directory}/terraform.tfvars {extra_vars} "
                           f"--auto-approve {directory}"]

        # Act
        tf_service.apply(directory, extra_vars)

        # Assert
        self.assertEqual(tf_service.cmd.history, command_history)

    def test_tf_service_destroy(self):

        # Arrange
        command = Command()
        tf_service = TerraformService(cmd=command)

        extra_vars = 'prod'
        directory = os.path.join(os.getcwd(), KAOS_STATE_DIR)
        command_history = [f"terraform destroy --var-file={directory}/terraform.tfvars {extra_vars} --auto-approve "
                           f"{directory}"]

        # Act
        tf_service.destroy(directory, extra_vars)

        # Assert
        self.assertEqual(tf_service.cmd.history, command_history)

    def test_tf_service_destroy(self):

        # Arrange
        command = Command()
        tf_service = TerraformService(cmd=command)

        extra_vars = 'prod'
        directory = os.path.join(os.getcwd(), KAOS_STATE_DIR)
        command_history = [f"terraform destroy --var-file={directory}/terraform.tfvars {extra_vars} --auto-approve "
                           f"{directory}"]

        # Act
        tf_service.destroy(directory, extra_vars)

        # Assert
        self.assertEqual(tf_service.cmd.history, command_history)

    @parameterized.expand(test_inputs_execute_data)
    def test_tf_service_execute(self, command_execute_data):

        # Arrange
        command = Command()

        # Act
        for cmd in command_execute_data:
            command.append(cmd)
            tf_service = TerraformService(cmd=command)
            exitcode, out, err = tf_service.execute()

            # Assert
            self.assertEqual(exitcode, 0)

    def test_tf_service_cd_dir(self):

        # Arrange
        command = Command()
        tf_service = TerraformService(cmd=command)

        directory = os.path.join(os.getcwd(), KAOS_STATE_DIR)
        command_history = [f"cd {directory}"]

        # Act
        tf_service.cd_dir(directory)

        # Assert
        self.assertEqual(tf_service.cmd.history, command_history)

















