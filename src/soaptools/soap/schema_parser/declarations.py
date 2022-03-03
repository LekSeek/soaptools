from typing import List
from soaptools.soap.schema_parser.restriction_elements import RestrictionDeclaration


class Declaration:
    name: str
    target_namespace: str

    def __init__(self, name: str, target_namespace: str):
        self.name = name
        self.target_namespace = target_namespace

    @property
    def identifier(self):
        return f"{{{self.target_namespace}}}{self.name}"


class TypeDeclaration(Declaration):
    pass


class SimpleTypeDeclaration(TypeDeclaration):
    restriction: RestrictionDeclaration

    def __init__(self, name: str, target_namespace: str, restriction: RestrictionDeclaration):
        super().__init__(name, target_namespace)
        self.restriction = restriction


class ElementDeclaration(Declaration):
    type: str
    default: str
    min_occurs: int
    max_occurs: int
    nillable: bool

    def __init__(
        self,
        name: str,
        target_namespace: str,
        type: str = None,
        default: str = None,
        min_occurs: int = 1,
        max_occurs: int = 1,
        nillable: bool = False,
            ):
        super().__init__(name, target_namespace)
        self.name = name
        self.target_namespace = target_namespace
        self.type = type
        self.default = default
        self.min_occurs = min_occurs
        self.max_occurs = max_occurs
        self.nillable = nillable


class ComplexTypeDeclaration(TypeDeclaration):
    elements: List[ElementDeclaration]

    def __init__(self, name: str, target_namespace: str, elements: List[ElementDeclaration]):
        super().__init__(name, target_namespace)
        self.elements = elements
