from typing import List
import lxml.etree

from soaptools.helpers.lxml import get_full_identifier
from soaptools.soap.namespaces import WSDL_NAMESPACE
from soaptools.soap.wsdl_parser.exceptions import ParsingException


class PartDeclaration:
    name: str
    type: str = None
    element: str = None

    def __init__(self, name: str, type: str = None, element: str = None):
        self.name = name

        if type and element:
            raise ValueError("<wsdl:part/> attributes type and element are mutually exclusive")
        self.type = type
        self.element = element

    @classmethod
    def from_lxml(cls, node: lxml.etree._Element) -> "PartDeclaration":
        element = None
        if element := node.attrib.get("element"):
            element = get_full_identifier(element, node.nsmap)

        type = None
        if type := node.attrib.get("type"):
            type = get_full_identifier(type, node.nsmap)

        return cls(
            name=node.attrib["name"],
            element=element,
            type=type
        )


class MessageDeclaration:
    name: str
    parts: List[PartDeclaration]

    def __init__(self, name: str, parts: List[PartDeclaration]):
        self.name = name

        if len(parts) == 0:
            raise ParsingException("Parts are required")

        self.parts = parts

    @classmethod
    def from_lxml(cls, node: lxml.etree._Element) -> "MessageDeclaration":
        return cls(
            name=node.attrib["name"],
            parts=[PartDeclaration.from_lxml(part) for part in node.findall(f"{{{WSDL_NAMESPACE}}}part")]
        )
