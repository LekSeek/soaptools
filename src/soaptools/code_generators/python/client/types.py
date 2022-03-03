import lxml.etree
from typing import Type, Dict
from soaptools.code_generators.python.definitions.types import AnyType


class Part:
    def __init__(self, type: Type[AnyType]):
        self.type = type


class Message:
    def __init__(self, parameters):
        # there should be every kwarg per <wsdl:part> BUT
        # looks like there is some convention that every <wsdl:message> contains only <wsdl:part name="parameters">
        # even if its not mentioned in SOAP specification, or its just ASP.NET thing

        # if code generator will generate more other than parameters kwarg, then modify this class
        self.parameters = parameters

    def get_request_arguments(self) -> Dict:
        return self.parameters.xml_value

    @classmethod
    def from_lxml(cls, node: lxml.etree._Element):
        # same here, looks like there is <part name="parameters"> convention kept everywhere
        return cls(
            parameters=cls.parameters.type.from_lxml_node(node.getroottree().find(f"//{cls.parameters.type.identifier}"))
        )

