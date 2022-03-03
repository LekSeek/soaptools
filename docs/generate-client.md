# Generate client
## 1. Usage  
```bash
  python -msoaptools generate-client <wsdl_url> <output_foler_name>
```
Will generate 3 files: client.py, messages.py and types.py in output_folder_name

Example result:

client.py
```python
from .messages import *
from soaptools.code_generators.python.client import SoapClient


class TextCasingClient(SoapClient):
    def __init__(
        self,
        wsdl="https://www.dataaccess.com/webservicesserver/TextCasing.wso?WSDL",
        wsse=None,
        transport=None,
        service_name=None,
        port_name=None,
        plugins=None,
        settings=None,
    ):
        super().__init__( # <-- do here what you want, its passed to zeep client during instantiation
            wsdl=wsdl,
            wsse=wsse,
            transport=transport,
            service_name=service_name,
            port_name=port_name,
            plugins=plugins,
            settings=settings,
        )
    """
    THOSE are available actions with required request and response types 
    """
    def TitleCaseWordsWithToken(
        self, input: TitleCaseWordsWithTokenSoapRequest
    ) -> TitleCaseWordsWithTokenSoapResponse:
        return self._execute_action(
            action_name="TitleCaseWordsWithToken",
            input_object=input,
            output_class=TitleCaseWordsWithTokenSoapResponse,
        )

    def InvertStringCase(
        self, input: InvertStringCaseSoapRequest
    ) -> InvertStringCaseSoapResponse:
        return self._execute_action(
            action_name="InvertStringCase",
            input_object=input,
            output_class=InvertStringCaseSoapResponse,
        )

    def InvertCaseFirstAdjustStringToPrevious(
        self, input: InvertCaseFirstAdjustStringToPreviousSoapRequest
    ) -> InvertCaseFirstAdjustStringToPreviousSoapResponse:
        return self._execute_action(
            action_name="InvertCaseFirstAdjustStringToPrevious",
            input_object=input,
            output_class=InvertCaseFirstAdjustStringToPreviousSoapResponse,
        )

    def InvertCaseFirstAdjustStringToCurrent(
        self, input: InvertCaseFirstAdjustStringToCurrentSoapRequest
    ) -> InvertCaseFirstAdjustStringToCurrentSoapResponse:
        return self._execute_action(
            action_name="InvertCaseFirstAdjustStringToCurrent",
            input_object=input,
            output_class=InvertCaseFirstAdjustStringToCurrentSoapResponse,
        )

    def AllUppercaseWithToken(
        self, input: AllUppercaseWithTokenSoapRequest
    ) -> AllUppercaseWithTokenSoapResponse:
        return self._execute_action(
            action_name="AllUppercaseWithToken",
            input_object=input,
            output_class=AllUppercaseWithTokenSoapResponse,
        )

    def AllLowercaseWithToken(
        self, input: AllLowercaseWithTokenSoapRequest
    ) -> AllLowercaseWithTokenSoapResponse:
        return self._execute_action(
            action_name="AllLowercaseWithToken",
            input_object=input,
            output_class=AllLowercaseWithTokenSoapResponse,
        )

    def UppercaseWordsWithToken(
        self, input: UppercaseWordsWithTokenSoapRequest
    ) -> UppercaseWordsWithTokenSoapResponse:
        return self._execute_action(
            action_name="UppercaseWordsWithToken",
            input_object=input,
            output_class=UppercaseWordsWithTokenSoapResponse,
        )

    def LowercaseWordsWithToken(
        self, input: LowercaseWordsWithTokenSoapRequest
    ) -> LowercaseWordsWithTokenSoapResponse:
        return self._execute_action(
            action_name="LowercaseWordsWithToken",
            input_object=input,
            output_class=LowercaseWordsWithTokenSoapResponse,
        )
```

messages.py

Those classes behave like Django models. You put data in constructor in attrbiutes and those predefined are 
for validation, internal behaviour puropses 


Why they look that way?  
Those classes are required due to https://www.w3.org/TR/wsdl.html#_message  
Theorically: `<wsdl:part>` describes node for request Body  
Practically: looks every service does one `<wsdl:part name="parameters">` node, so I left it that way in case if 
some services really used that possibility

```python
from soaptools.code_generators.python.client.types import Message, Part
from .types import (
    TitleCaseWordsWithTokenComplexType,
    TitleCaseWordsWithTokenResponseComplexType,
    InvertStringCaseComplexType,
    InvertStringCaseResponseComplexType,
    InvertCaseFirstAdjustStringToPreviousComplexType,
    InvertCaseFirstAdjustStringToPreviousResponseComplexType,
    InvertCaseFirstAdjustStringToCurrentComplexType,
    InvertCaseFirstAdjustStringToCurrentResponseComplexType,
    AllUppercaseWithTokenComplexType,
    AllUppercaseWithTokenResponseComplexType,
    AllLowercaseWithTokenComplexType,
    AllLowercaseWithTokenResponseComplexType,
    UppercaseWordsWithTokenComplexType,
    UppercaseWordsWithTokenResponseComplexType,
    LowercaseWordsWithTokenComplexType,
    LowercaseWordsWithTokenResponseComplexType,
)


class TitleCaseWordsWithTokenSoapRequest(Message):
    parameters = Part(type=TitleCaseWordsWithTokenComplexType)

    def __init__(self, parameters: TitleCaseWordsWithTokenComplexType):
        super().__init__(parameters=parameters)


class TitleCaseWordsWithTokenSoapResponse(Message):
    parameters = Part(type=TitleCaseWordsWithTokenResponseComplexType)

    def __init__(self, parameters: TitleCaseWordsWithTokenResponseComplexType):
        super().__init__(parameters=parameters)

[...]
```

types.py

Those classes represent XSchema types. Like in messages, for constructor arguments you pass types defined
in Element.type, or if its simple type e.g. `sText = Element(type=xs.StringSimpleType)` you can pass just string

```python
from soaptools.code_generators.python.definitions.types.base import (
    ComplexType,
    Element,
)
from soaptools.code_generators.python.definitions.types import xs



class TitleCaseWordsWithTokenComplexType(ComplexType):
    sText = Element(type=xs.StringSimpleType)
    sToken = Element(type=xs.StringSimpleType)

    def __init__(self, sText, sToken):
        super().__init__(sText=sText, sToken=sToken)

    class Meta:
        name = "TitleCaseWordsWithToken"
        targetNamespace = "http://www.dataaccess.com/webservicesserver/"


[...]


class AllLowercaseWithTokenResponseComplexType(ComplexType):
    AllLowercaseWithTokenResult = Element(type=xs.StringSimpleType)

    def __init__(self, AllLowercaseWithTokenResult):
        super().__init__(AllLowercaseWithTokenResult=AllLowercaseWithTokenResult)

    class Meta:
        name = "AllLowercaseWithTokenResponse"
        targetNamespace = "http://www.dataaccess.com/webservicesserver/"


class UppercaseWordsWithTokenComplexType(ComplexType):
    sAString = Element(type=xs.StringSimpleType)
    sToken = Element(type=xs.StringSimpleType)

    def __init__(self, sAString, sToken):
        super().__init__(sAString=sAString, sToken=sToken)

    class Meta:
        name = "UppercaseWordsWithToken"
        targetNamespace = "http://www.dataaccess.com/webservicesserver/"


class UppercaseWordsWithTokenResponseComplexType(ComplexType):
    UppercaseWordsWithTokenResult = Element(type=xs.StringSimpleType)

    def __init__(self, UppercaseWordsWithTokenResult):
        super().__init__(UppercaseWordsWithTokenResult=UppercaseWordsWithTokenResult)

    class Meta:
        name = "UppercaseWordsWithTokenResponse"
        targetNamespace = "http://www.dataaccess.com/webservicesserver/"


class LowercaseWordsWithTokenComplexType(ComplexType):
    sAString = Element(type=xs.StringSimpleType)
    sToken = Element(type=xs.StringSimpleType)

    def __init__(self, sAString, sToken):
        super().__init__(sAString=sAString, sToken=sToken)

    class Meta:
        name = "LowercaseWordsWithToken"
        targetNamespace = "http://www.dataaccess.com/webservicesserver/"


class LowercaseWordsWithTokenResponseComplexType(ComplexType):
    LowercaseWordsWithTokenResult = Element(type=xs.StringSimpleType)

    def __init__(self, LowercaseWordsWithTokenResult):
        super().__init__(LowercaseWordsWithTokenResult=LowercaseWordsWithTokenResult)

    class Meta:
        name = "LowercaseWordsWithTokenResponse"
        targetNamespace = "http://www.dataaccess.com/webservicesserver/"

```
