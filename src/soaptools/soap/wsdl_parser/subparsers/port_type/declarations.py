from dataclasses import dataclass
from typing import List
import lxml.etree

from soaptools.helpers.lxml import get_full_identifier
from soaptools.soap.namespaces import WSDL_NAMESPACE


@dataclass
class InputDeclaration:
    message: str

    @classmethod
    def from_lxml(cls, node: lxml.etree._Element) -> "InputDeclaration":
        return cls(
            message=get_full_identifier(node.attrib["message"], node.nsmap),
        )


@dataclass
class OutputDeclaration:
    message: str

    @classmethod
    def from_lxml(cls, node: lxml.etree._Element) -> "OutputDeclaration":
        return cls(
            message=get_full_identifier(node.attrib["message"], node.nsmap),
        )


@dataclass
class OperationDeclaration:
    name: str
    input: InputDeclaration
    output: OutputDeclaration

    @classmethod
    def from_lxml(cls, node: lxml.etree._Element) -> "OperationDeclaration":
        return cls(
            name=node.attrib["name"],
            input=InputDeclaration.from_lxml(node.find(f"{{{WSDL_NAMESPACE}}}input")),
            output=OutputDeclaration.from_lxml(node.find(f"{{{WSDL_NAMESPACE}}}output"))
        )


@dataclass
class PortTypeDeclaration:
    operations: List[OperationDeclaration]

    @classmethod
    def from_lxml(cls, node: lxml.etree._Element) -> "PortTypeDeclaration":
        return cls(
            operations=[OperationDeclaration.from_lxml(operation_node) for operation_node in node.findall(f"{{{WSDL_NAMESPACE}}}operation")]
        )

