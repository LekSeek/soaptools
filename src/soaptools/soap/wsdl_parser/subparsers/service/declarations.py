import lxml.etree

from dataclasses import dataclass


@dataclass
class ServiceDeclaration:
    name: str

    @classmethod
    def from_lxml(cls, node: lxml.etree._Element):
        return cls(
            name=node.attrib["name"]
        )
