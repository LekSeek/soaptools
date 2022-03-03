import os
import pathlib
import shutil
from typing import List
from unittest import TestCase
from soaptools.cli import execute_command_from_args


class SoapToolsTestCase(TestCase):
    output_location = pathlib.Path(__file__).parent.resolve() / "_redfdasfdssults"

    def execute_action(self, command):
        return execute_command_from_args([part for part in command.split(" ") if part])

    def get_fixture_path(self, path: List[str]) -> str:
        root = pathlib.Path(__file__).parent
        for elem in ["..", "fixtures"] + path:
            root /= elem
        return str(root.resolve())

    def tearDown(self) -> None:
        # try:
        #     shutil.rmtree(self.output_location)
        # except FileNotFoundError:
        #     pass
        # except NotADirectoryError:
        #     try:
        #         os.remove(self.output_location)
        #     except FileNotFoundError:
        #         pass
        pass

