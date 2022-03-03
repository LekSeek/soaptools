import lxml.etree
from dataclasses import dataclass
from typing import List

from soaptools.soap.schema_parser.declarations import TypeDeclaration
from soaptools.soap.namespaces import WSDL_NAMESPACE
from .subparsers.message.declarations import MessageDeclaration
from .subparsers.port_type.declarations import PortTypeDeclaration
from .subparsers.service.declarations import ServiceDeclaration
from .subparsers.types.parser import parse_types_node


@dataclass
class WsdlDeclaration:
    wsdl_url: str
    types: List[TypeDeclaration]
    port_type: PortTypeDeclaration
    messages: List[MessageDeclaration]
    service: ServiceDeclaration

    @classmethod
    def from_lxml(cls, node: lxml.etree._Element, wsdl_url: str) -> "WsdlDeclaration":
        return cls(
            wsdl_url=wsdl_url,
            messages=[MessageDeclaration.from_lxml(message) for message in node.findall(f"{{{WSDL_NAMESPACE}}}message")],
            port_type=PortTypeDeclaration.from_lxml(node.find(f"{{{WSDL_NAMESPACE}}}portType")),
            types=parse_types_node(node.find(f"{{{WSDL_NAMESPACE}}}types")),
            service=ServiceDeclaration.from_lxml(node.find(f"{{{WSDL_NAMESPACE}}}service"))
        )




