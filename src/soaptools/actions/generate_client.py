import ast
import os
from argparse import Namespace

from soaptools.actions.action import Action
from soaptools.helpers.py import Logger, format_code
from ..code_generators.python.client import ClientGenerator
from ..soap.wsdl_parser.parser import get_wsdl_declaration


class GenerateClientAction(Action):
    name = "generate-client"
    help = "generate SOAP client based on passed wsdl"

    @classmethod
    def add_arguments_to_action_parser(cls, action_parser):
        action_parser.add_argument("input_filepath", type=str, help="Filepath or URL to WSDL")
        action_parser.add_argument("output_folder_name", type=str, help="output folder name")

    @classmethod
    def execute(cls, arguments: Namespace):
        input_file_path = arguments.input_filepath
        output_folder_name = arguments.output_folder_name

        Logger.info("Parsing wsdl")
        wsdl_declaration = get_wsdl_declaration(input_file_path)

        Logger.info("Generating python code")

        # 1. check messages
        # 2. generate only necessary types (filter out from wsdl_declaration.types ?)
        # 3. generate client
        modules = ClientGenerator.generate_client_from_wsdl_declaration(wsdl_declaration)

        try:
            os.mkdir(output_folder_name)
        except FileExistsError:
            pass

        open(output_folder_name + "\\" + "__init__.py", mode="w").write("")
        for module_name, module_ast in modules.items():
            open(output_folder_name + "\\" + module_name + ".py", mode="w").write(format_code(ast.unparse(module_ast)))

