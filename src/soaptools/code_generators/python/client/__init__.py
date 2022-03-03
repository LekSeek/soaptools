from typing import Dict, TypeVar, Type

import zeep
import zeep.proxy
import zeep.wsdl.bindings.soap
import zeep.exceptions
import lxml.etree
import ast
import functools

from soaptools.code_generators.python.client.types import Message
from soaptools.code_generators.python.definitions.generator import TypesCodeGenerator
from soaptools.soap.wsdl_parser.declarations import WsdlDeclaration
from soaptools.soap.wsdl_parser.subparsers.message.declarations import MessageDeclaration

T = TypeVar('T')


def new_process_reply(self, envelope):
    # envelope_qname = lxml.etree.QName(self.nsmap["soap-env"], "Envelope")
    # if envelope.tag != envelope_qname:
    #     raise zeep.exceptions.XMLSyntaxError(
    #         (
    #                 "The XML returned by the server does not contain a valid "
    #                 + "{%s}Envelope root element. The root element found is %s "
    #         )
    #         % (envelope_qname.namespace, envelope.tag)
    #     )

    if self.output:
        return envelope


class SoapClient(zeep.Client):
    """
    At this time its just Facade for zeep client, with typing and stuff
    """

    def __init__(self, *args, **kwargs):
        super(SoapClient, self).__init__(*args, **kwargs)
        for def_key, definition in self.wsdl._definitions.items():
            for binding_key, binding in definition.bindings.items():
                for key, operation in binding._operations.items():
                    operation.process_reply = lambda envelope: new_process_reply(operation, envelope)

    def _execute_action(self, action_name: str, input_object: Message, output_class: Type[T]) -> T:
        response = getattr(self.service, action_name)(**input_object.get_request_arguments())
        return output_class.from_lxml(response)


class ClientGenerator:
    @classmethod
    def generate_client_from_wsdl_declaration(cls, wsdl_declaration: WsdlDeclaration) -> Dict[str, ast.Module]:
        modules_map = {}
        messages_mapping = cls.__get_messages_classes_mapping(wsdl_declaration)
        all_messages = functools.reduce(
            lambda acc, curr: acc + list(curr.values()),
            list(messages_mapping.values()),
            []
        )

        types_to_generate = []
        for message in all_messages:
            for assignment in filter(lambda elem: isinstance(elem, ast.Assign), message.body):
                assignment: ast.Assign
                type_identifier = next(filter(lambda keyword: keyword.arg == "type", assignment.value.keywords)).value.id
                types_to_generate.append(next(filter(lambda declaration: declaration.identifier == type_identifier, wsdl_declaration.types)))

        types_generator = TypesCodeGenerator(wsdl_declaration.types, types_to_generate)
        modules_map["types"] = types_generator.generate()

        types_names_to_import = []
        for message in all_messages:
            for assignment in filter(lambda elem: isinstance(elem, ast.Assign), message.body):
                assignment: ast.Assign
                type_identifier = next(filter(lambda keyword: keyword.arg == "type", assignment.value.keywords)).value.id
                type_name = types_generator.generated_types_registry.get_type_by_identifier(type_identifier)["name"]
                types_names_to_import.append(type_name)
                next(filter(lambda keyword: keyword.arg == "type", assignment.value.keywords)).value = ast.Name(type_name)

                # add types to constructor
                constructor_def = next(filter(lambda elem: isinstance(elem, ast.FunctionDef) and elem.name == "__init__",  message.body))
                next(filter(lambda arg: arg.arg == assignment.targets[0].id, constructor_def.args.args)).annotation = ast.Name(type_name)

        modules_map["messages"] = ast.Module(
            body=[
                ast.ImportFrom(
                    module="soaptools.code_generators.python.client.types",
                    names=[ast.alias(name="Message"), ast.alias(name="Part")],
                    level=0
                ),
                ast.ImportFrom(
                    module=".types",
                    names=[ast.alias(name=type_name) for type_name in types_names_to_import],
                    level=0
                ),
            ] + all_messages,
            type_ignores=[]
        )

        modules_map["client"] = ast.Module(
            body=[
                ast.ImportFrom(
                    module=".messages",
                    names=[ast.alias(name="*")],
                    level=0
                ),
                ast.ImportFrom(
                    module="soaptools.code_generators.python.client",
                    names=[ast.alias(name="SoapClient")],
                    level=0
                ),
                cls.__get_client_class_ast(wsdl_declaration, messages_mapping)
            ],
            type_ignores=[]
        )

        return modules_map

    @classmethod
    def __get_messages_classes_mapping(cls, wsdl_declaration: WsdlDeclaration) -> dict[
        str, dict[str, MessageDeclaration]]:
        operations_mapping: Dict[str] = {}

        for operation in wsdl_declaration.port_type.operations:
            input_message: MessageDeclaration = next(
                filter(lambda message: message.name == operation.input.message.split("}")[-1],
                       wsdl_declaration.messages))
            output_message: MessageDeclaration = next(
                filter(lambda message: message.name == operation.output.message.split("}")[-1],
                       wsdl_declaration.messages))
            operations_mapping[operation.name] = {"input_message": input_message, "output_message": output_message}

            for input_output in ["input_message", "output_message"]:
                message = operations_mapping[operation.name][input_output]
                operations_mapping[operation.name][input_output] = ast.ClassDef(
                    name=message.name,
                    bases=[ast.Name("Message")],
                    body=[
                        ast.Assign(
                            targets=[ast.Name(part.name)],
                            value=ast.Call(
                                func=ast.Name("Part"),
                                args=[],
                                keywords=[ast.keyword(arg="type", value=ast.Name(part.type or part.element))]
                            ),
                            lineno=0
                        )
                        for part in message.parts
                    ] + [
                        ast.FunctionDef(
                            name="__init__",
                            args=ast.arguments(
                                args=[ast.arg("self")] + [ast.arg(part.name) for part in message.parts],
                                posonlyargs=[],
                                kwonlyargs=[],
                                defaults=[],
                            ),
                            body=[
                                ast.Call(
                                    func=ast.Name("super().__init__"),
                                    args=[],
                                    keywords=[ast.keyword(arg=part.name, value=ast.Name(part.name)) for part in message.parts]
                                )
                            ],
                            decorator_list=[],
                            lineno=0,
                        ),
                    ],
                    decorator_list=[],
                    keywords=[]
                )
        return operations_mapping

    @classmethod
    def __get_client_class_ast(cls, wsdl_declaration: WsdlDeclaration,
                               messages_classes_mapping: Dict[str, Dict[str, ast.ClassDef]]) -> ast.ClassDef:
        actions_defs = []
        for operation in wsdl_declaration.port_type.operations:
            output_object_type = messages_classes_mapping[operation.name]["output_message"].name
            actions_defs.append(
                ast.FunctionDef(
                    name=operation.name,
                    args=ast.arguments(
                        args=[
                            ast.arg("self"),
                            ast.arg("input",
                                    annotation=ast.Name(messages_classes_mapping[operation.name]["input_message"].name))
                        ],
                        posonlyargs=[],
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[],
                    ),
                    body=[
                        ast.Return(
                            ast.Call(
                                func=ast.Name("self._execute_action"),
                                args=[],
                                keywords=[
                                    ast.keyword(arg="action_name", value=ast.Constant(operation.name)),
                                    ast.keyword(arg="input_object", value=ast.Name("input")),
                                    ast.keyword(arg="output_class", value=ast.Name(output_object_type)),
                                ]
                            )
                        ),
                    ],
                    returns=ast.Name(output_object_type),
                    decorator_list=[],
                    lineno=0,
                )
            )
        constructor = ast.FunctionDef(
            name="__init__",
            args=ast.arguments(
                args=[
                    ast.arg("self"),
                    ast.arg("wsdl"),
                    ast.arg("wsse"),
                    ast.arg("transport"),
                    ast.arg("service_name"),
                    ast.arg("port_name"),
                    ast.arg("plugins"),
                    ast.arg("settings"),
                ],
                posonlyargs=[],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[None, ast.Constant(wsdl_declaration.wsdl_url)] + [ast.Constant(value=None) for _ in range(6)],
            ),
            body=[
                ast.Call(
                    func=ast.Name("super().__init__"),
                    args=[],
                    keywords=[
                        ast.keyword(arg="wsdl", value=ast.Name("wsdl")),
                        ast.keyword(arg="wsse", value=ast.Name("wsse")),
                        ast.keyword(arg="transport", value=ast.Name("transport")),
                        ast.keyword(arg="service_name", value=ast.Name("service_name")),
                        ast.keyword(arg="port_name", value=ast.Name("port_name")),
                        ast.keyword(arg="plugins", value=ast.Name("plugins")),
                        ast.keyword(arg="settings", value=ast.Name("settings")),
                    ]
                )
            ],
            decorator_list=[],
            lineno=0,
        )

        return ast.ClassDef(
            name=wsdl_declaration.service.name + "Client",
            bases=[ast.Name("SoapClient")],
            body=[
                constructor,
                actions_defs
            ],
            decorator_list=[],
            keywords=[],
        )
