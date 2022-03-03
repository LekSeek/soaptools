import lxml.etree
from .declarations import WsdlDeclaration
from ...helpers.py import get_content_from_uri


def get_wsdl_declaration(wsdl_location: str) -> WsdlDeclaration:
    input_file_content = get_content_from_uri(wsdl_location)
    wsdl_tree = lxml.etree.fromstring(input_file_content.encode()).getroottree()

    return WsdlDeclaration.from_lxml(wsdl_tree, wsdl_location)
