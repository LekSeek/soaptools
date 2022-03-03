from helpers.utils import SoapToolsTestCase
from helpers.wsdl_locations import TEXT_CASING_WSDL


class GenerateClientTestCase(SoapToolsTestCase):

    def test_bindings_from_wsdl(self):
        self.execute_action(f"generate-client {TEXT_CASING_WSDL} {self.output_location}")
