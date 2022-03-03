from typing import List

import lxml.etree

from soaptools.soap.namespaces import XS_NAMESPACE
from soaptools.soap.schema_parser.declarations import TypeDeclaration
from soaptools.soap.schema_parser.parser import SchemaParser


def parse_types_node(types_node: lxml.etree._Element) -> List[TypeDeclaration]:
    all_schemas_nodes = types_node.findall(f"{{{XS_NAMESPACE}}}schema")
    return SchemaParser(all_schemas_nodes).get_declarations()

