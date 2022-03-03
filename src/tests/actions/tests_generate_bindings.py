from helpers.utils import SoapToolsTestCase
from helpers.wsdl_locations import TEXT_CASING_WSDL


class GenerateBindingsTestCase(SoapToolsTestCase):

    def test_bindings_from_wsdl(self):
        self.execute_action(f"generate-bindings --from-wsdl {TEXT_CASING_WSDL} {self.output_location}")

    def test_from_xsd(self):
        schema_location = self.get_fixture_path(["xsds", "minimal.xsd"])
        self.execute_action(f"generate-bindings --from-xsd {schema_location} {self.output_location}")

