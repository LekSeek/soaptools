import copy
from typing import List

from soaptools.soap.schema_parser.declarations import TypeDeclaration


class CodeGenerator:
    def __init__(self, declarations: List[TypeDeclaration]):
        self.declarations = copy.deepcopy(declarations)

    def generate(self):
        raise NotImplementedError()

    class TypeNotFoundException(Exception):
        pass