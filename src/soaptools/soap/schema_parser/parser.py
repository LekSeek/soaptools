from typing import List, Dict, Union

import lxml.etree

from soaptools.exceptions import ApplicationException
from soaptools.helpers.lxml import get_full_identifier, xml_val_to_python_val
from soaptools.helpers.py import get_content_from_uri, Logger
from soaptools.soap.namespaces import XS_NAMESPACE, MS_SERIALIZATION_NAMESPACE
from soaptools.soap.schema_parser.declarations import ComplexTypeDeclaration, SimpleTypeDeclaration, \
    ElementDeclaration, RestrictionDeclaration, TypeDeclaration
from soaptools.soap.schema_parser.restriction_elements import PatternRestrictionDeclaration, \
    MaxInclusiveRestrictionDeclaration, MinInclusiveRestrictionDeclaration, EnumerationRestrictionDeclaration


class SchemaParser:
    schemas: Dict[str, lxml.etree._Element]
    resolved_namespaces: List[str]
    types_declarations: List[TypeDeclaration]

    def __init__(self, schemas):
        if not isinstance(schemas, List):
            schemas: List[lxml.etree._Element] = [schemas]

        self.schemas = {
            schema.attrib["targetNamespace"]: schema
            for schema in schemas
        }

    def get_declarations(self) -> List[TypeDeclaration]:
        self.resolved_namespaces = []
        self.types_declarations = []

        for schema in self.schemas.values():
            try:
                self.__parse_schema(schema)
            except self.AlreadyParsedException:
                continue
        return self.types_declarations

    def __import_schema(self, import_node: lxml.etree._Element) -> lxml.etree._Element:
        schema_namespace = import_node.attrib["namespace"]

        if schema_namespace in self.schemas:
            return self.schemas[schema_namespace]

        if "schemaLocation" not in import_node.attrib:
            raw_node = lxml.etree.tostring(import_node)
            raise self.ImportSchemaException(f"Node {raw_node} doesn't contain schemaLocation")

        schema_location = import_node.attrib["schemaLocation"]
        try:
            self.schemas[schema_namespace] = lxml.etree.fromstring(get_content_from_uri(schema_location).encode())
        except:
            raise self.ImportSchemaException(f"Import of {schema_location} failed. Schema not found")
        return self.schemas[schema_namespace]

    def __get_included_schema(self, include_node: lxml.etree._Element) -> lxml.etree._Element:
        # todo: add handling if was schema already included
        schema_location = include_node.attrib.get("schemaLocation")
        if not schema_location:
            raise self.ParsingException("Encountered <xs:include/> without schemaLocation")
        return lxml.etree.fromstring(get_content_from_uri(schema_location).encode())

    def __parse_schema(self, schema: lxml.etree._Element, is_include=False):
        schema_namespace = schema.attrib["targetNamespace"]
        if schema_namespace in self.resolved_namespaces:
            raise self.AlreadyParsedException()

        for node in schema.getchildren():
            # read as other namespace
            if node.tag == f"{{{XS_NAMESPACE}}}import":
                try:
                    self.__parse_schema(self.__import_schema(node))
                except self.AlreadyParsedException:
                    continue
            elif node.tag == f"{{{XS_NAMESPACE}}}include":
                self.__parse_schema(self.__get_included_schema(node), is_include=True)
            elif node.tag == f"{{{XS_NAMESPACE}}}element":
                parse_result = self.__parse_element(node, node.attrib.get("targetNamespace") or schema_namespace)
                self.types_declarations.append(parse_result)
            elif node.tag == f"{{{XS_NAMESPACE}}}simpleType":
                self.types_declarations.append(self.__parse_simple_type(node, node.attrib.get("targetNamespace") or schema_namespace))
            elif node.tag == f"{{{XS_NAMESPACE}}}complexType":
                self.types_declarations.append(self.__parse_complex_type(node, node.attrib.get("targetNamespace") or schema_namespace))
            elif node.tag == f"{{{XS_NAMESPACE}}}attribute":
                Logger.warning("<xs:attribute> is not supported yet")
            elif node.tag == f"{{{XS_NAMESPACE}}}annotation":
                continue
            else:
                raise self.ParsingException(f"Unsupported node {node.tag}")
        if not is_include:
            self.resolved_namespaces.append(schema_namespace)

    # elements parsers
    def __parse_complex_type(self, node: lxml.etree._Element, target_namespace: str) -> ComplexTypeDeclaration:
        name = node.attrib["name"]
        elements = []
        for element_node in node.findall(f"{{{XS_NAMESPACE}}}sequence/{{{XS_NAMESPACE}}}element"):
            kwargs = {
                "default": "default",
                "minOccurs": "min_occurs",
                "maxOccurs": "max_occurs",
                "nillable": "nillable"
            }
            kwargs = {
                decl_attrib: xml_val_to_python_val(element_node.attrib[node_attrib])
                for node_attrib, decl_attrib in kwargs.items() if node_attrib in element_node.attrib
            }
            elements.append(
                ElementDeclaration(
                    name=element_node.attrib["name"],
                    target_namespace=element_node.attrib.get("targetNamespace") or target_namespace,
                    type=get_full_identifier(element_node.attrib["type"], element_node.nsmap),
                    **kwargs
                )
            )

        return ComplexTypeDeclaration(name=name, target_namespace=target_namespace, elements=elements)

    def __parse_restriction(self, node: lxml.etree._Element) -> RestrictionDeclaration:
        restriction_elements = []

        enumeration_options = {}
        for restriction_element in node.getchildren():
            value = xml_val_to_python_val(restriction_element.attrib["value"])
            if restriction_element.tag == f"{{{XS_NAMESPACE}}}pattern":
                restriction_elements.append(PatternRestrictionDeclaration(pattern=value))
            elif restriction_element.tag == f"{{{XS_NAMESPACE}}}minInclusive":
                restriction_elements.append(MinInclusiveRestrictionDeclaration(min=value))
            elif restriction_element.tag == f"{{{XS_NAMESPACE}}}maxInclusive":
                restriction_elements.append(MaxInclusiveRestrictionDeclaration(max=value))
            elif restriction_element.tag == f"{{{XS_NAMESPACE}}}enumeration":
                enum_key = enum_value = value
                enum_value_node = restriction_element.find(f"{{{XS_NAMESPACE}}}annotation/{{{XS_NAMESPACE}}}appinfo/{{{MS_SERIALIZATION_NAMESPACE}}}EnumerationValue")
                if enum_value_node is not None:
                    enum_value = enum_value_node.text
                enumeration_options[enum_key] = enum_value
            else:
                raise self.ParsingException(f"Unsupported restriction: <{restriction_element.tag}>")
        if enumeration_options:
            restriction_elements.append(EnumerationRestrictionDeclaration(enumeration_options=enumeration_options))

        return RestrictionDeclaration(
            base=get_full_identifier(node.attrib["base"], node.nsmap),
            rules=restriction_elements
        )

    def __parse_simple_type(self, node: lxml.etree._Element, target_namespace: str) -> SimpleTypeDeclaration:
        name = node.attrib["name"]
        restriction_node = node.find(f"{{{XS_NAMESPACE}}}restriction")
        if restriction_node is None:
            raise self.ParsingException("<xs:restriction/> is required for <xs:simpleType>")
        return SimpleTypeDeclaration(
            name=name,
            target_namespace=target_namespace,
            restriction=self.__parse_restriction(restriction_node),
        )

    def __parse_element(self, node: lxml.etree._Element, target_namespace: str) -> Union[ElementDeclaration, ComplexTypeDeclaration]:
        name = node.attrib["name"]

        if type := node.attrib.get("type"):
            return ElementDeclaration(name=name, target_namespace=target_namespace, type=get_full_identifier(type, node.nsmap))
        elif node.find(f"{{{XS_NAMESPACE}}}complexType/{{{XS_NAMESPACE}}}sequence") is not None:
            # then we consider it as complexType not element, weird but works
            subelements = node.find(f"{{{XS_NAMESPACE}}}complexType/{{{XS_NAMESPACE}}}sequence").getchildren()
            return ComplexTypeDeclaration(
                name=name,
                target_namespace=target_namespace,
                elements=[
                    ElementDeclaration(name=subelement.attrib["name"], target_namespace="TODO", type=get_full_identifier(subelement.attrib["type"], subelement.nsmap))
                    for subelement in subelements
                ]
            )
        else:
            raise Exception()

    class ParsingException(ApplicationException):
        pass

    class AlreadyParsedException(ParsingException):
        pass

    class ImportSchemaException(ParsingException):
        pass

