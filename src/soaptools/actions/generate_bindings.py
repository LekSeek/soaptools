import ast
from argparse import Namespace
import lxml.etree

from soaptools.actions.action import Action
from soaptools.code_generators.python.definitions.generator import TypesCodeGenerator
from soaptools.helpers.py import get_content_from_uri, Logger, format_code
from soaptools.soap.schema_parser.parser import SchemaParser
from ..soap.wsdl_parser.parser import get_wsdl_declaration


class GenerateBindingsAction(Action):
    name = "generate-bindings"
    help = "generate python classes from .xsd or wsdl URL or filesystem path"

    @classmethod
    def add_arguments_to_action_parser(cls, action_parser):
        action_parser.add_argument("--from-wsdl", help="generate bindings from wsdl", action="store_true")
        action_parser.add_argument("--from-xsd", help="generate bindings from xsd", action="store_true")
        action_parser.add_argument("input_filepath", type=str, help="Filepath or URL to input file")
        action_parser.add_argument("output_filepath", type=str, help="Path to output file")

    @classmethod
    def execute(cls, arguments: Namespace):
        input_file_path = arguments.input_filepath
        output_file_path = arguments.output_filepath

        Logger.info(f"Fetching file from {input_file_path}")

        if not arguments.from_wsdl and not arguments.from_xsd:
            raise Exception("--from-wsdl or --from-xsd required")

        Logger.info(f"Parsing {input_file_path}")
        if arguments.from_wsdl:
            types_declarations = get_wsdl_declaration(input_file_path).types
        elif arguments.from_xsd:
            input_file_content = get_content_from_uri(input_file_path)
            xsd = lxml.etree.fromstring(input_file_content.encode())
            types_declarations = SchemaParser(xsd).get_declarations()

        Logger.info("Generating python code")
        code = format_code(ast.unparse(TypesCodeGenerator(types_declarations).generate()))

        Logger.info(f"Writing to {output_file_path}")
        try:
            open(output_file_path, mode="w").write(code)
        except Exception:
            print(f"Write to {output_file_path} failed. Is this valid filepath?")
