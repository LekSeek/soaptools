import math
from typing import Dict

import lxml.etree

from soaptools.code_generators.python.definitions.exceptions import ValidationException
from soaptools.code_generators.python.definitions.restriction_elements import Enumeration
from soaptools.helpers.py import chain_hasattr, chain_getattr
from soaptools.soap.namespaces import XS_NAMESPACE


class AnyType:
    """
    Base type for EVERY other type.
    """
    value: object

    def __init__(self):
        for required_attr in ["Meta.name", "Meta.targetNamespace"]:
            if not chain_hasattr(self, required_attr):
                raise Exception(f"{required_attr} required")

    class Meta:
        name = "anyType"
        targetNamespace = XS_NAMESPACE

    @classmethod
    def from_lxml_node(cls, node):
        raise NotImplementedError

    def to_lxml(self):
        raise NotImplementedError

    def validate(self):
        raise NotImplementedError

    @property
    def xml_value(self):
        """
        Hook to be eventually overriden by subclasses.
        It should return xml ready value. E.g. instead of True, "true"
        """
        raise NotImplementedError

    @classmethod
    @property
    def identifier(cls):
        return f"{{{cls.Meta.targetNamespace}}}{cls.Meta.name}"


class SimpleType(AnyType):

    def __init__(self, value):
        super().__init__()
        if isinstance(value, lxml.etree._Element):
            value = value.text
        self.value = value

    @classmethod
    def from_lxml_node(cls, node):
        return cls(value=node.text)

    def to_lxml(self):
        raise NotImplementedError

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_val):
        self._value = new_val
        self.validate()

    def validate(self):
        if chain_hasattr(self, "Meta.restriction"):
            self.Meta.restriction.validate(self.value)

    @property
    def xml_value(self):
        return self._value


class Element:
    def __init__(self, type, default=None, min_occurs=1, max_occurs=1, nillable=False):
        if not issubclass(type, AnyType):
            raise ValueError("type must be AnyType subclass")
        self.type = type

        self.default = default

        if min_occurs < 0:
            raise ValueError("min_occurs must be greater or equal 0")
        self.min_occurs = min_occurs

        if max_occurs == "unbounded":
            max_occurs = math.inf
        else:
            if not isinstance(max_occurs, int) and not isinstance(max_occurs, float):  # math.inf is just hacky float
                raise ValueError("max_occurs must be positive integer or 'unbounded'")
            if max_occurs < 0:
                raise ValueError("max_occurs must be greater or equal 0")
            if max_occurs < min_occurs:
                raise ValueError("max_occurs must be equal or greater than min_occurs")
        self.max_occurs = max_occurs

        if not isinstance(nillable, bool):
            raise TypeError("nillable must be bool")
        self.nillable = nillable


class ComplexType(AnyType):
    def __init__(self, **kwargs):
        self._value = {}
        super().__init__()
        self.Meta.elements_definitions = self._get_elements_definitions()

        for key, element in self.Meta.elements_definitions.items():
            setattr(self, key, kwargs.get(key))

    def __getattribute__(self, item):
        old_getter = super().__getattribute__
        values = old_getter("_value")
        if values is None:
            values = {}
        if item in values:
            element_definition = self.Meta.elements_definitions[item]
            values = [i_val.value if issubclass(element_definition.type, SimpleType) else i_val for i_val in
                      values[item]]
            if element_definition.max_occurs > 1:
                return values
            return values[0] if values else None
        return old_getter(item)

    def __setattr__(self, key, value):
        old_setter = super().__setattr__
        if key not in chain_getattr(self, "Meta.elements_definitions", []):
            old_setter(key, value)
            return

        if not isinstance(value, list):
            if value is None:
                value = []
            else:
                value = [value]

        cleaned_values = []
        element_definition = self.Meta.elements_definitions[key]
        for idx, i_value in enumerate(value):
            if isinstance(i_value, element_definition.type):
                cleaned_values.append(i_value)
            elif isinstance(i_value, AnyType):
                raise ValidationException({idx: f"Invalid type passed EXPECTED {self.type} FOUND {i_value.__class__}"})
            elif isinstance(i_value, lxml.etree._Element):
                children = i_value.getchildren()
                new_value = None
                if children:
                    new_value = {}
                    for child in children:
                        tag = child.tag.split("}")[-1]
                        new_value[tag] = new_value.get(tag, []) + [child]
                elif i_value.text:
                    new_value = i_value.text  # todo: or it should be "" if None ?

                if new_value is not None:
                    try:
                        if issubclass(element_definition.type, ComplexType):
                            new_value = element_definition.type(**new_value)
                        else:
                            new_value = element_definition.type(value=new_value)
                    except ValidationException as e:
                        raise ValidationException({key: e.reason})

                    cleaned_values.append(new_value)
            elif issubclass(element_definition.type, SimpleType):
                try:
                    cleaned_values.append(element_definition.type(value=i_value))
                except ValidationException as e:
                    raise ValidationException({key: e.reason})
            elif issubclass(element_definition.type, ComplexType):
                try:
                    cleaned_values.append(element_definition.type(**i_value))
                except ValidationException as e:
                    raise ValidationException({key: e.reason})
            else:
                raise Exception()  # todo

        self._value[key] = cleaned_values

    def __dir__(self):
        return self._value.keys()

    def validate(self):
        for key, value in self._value:
            try:
                value.validate()
            except ValidationException as e:
                raise ValidationException(reason={key: e.reason})

    @classmethod
    def from_lxml_node(cls, node: lxml.etree.Element):
        elements_defs = cls._get_elements_definitions()
        kwargs = {
            element_name: [i_elem for i_elem in node.findall(f"{{{cls.Meta.targetNamespace}}}{element_name}")]
            for element_name, element_def in elements_defs.items()
        }
        return cls(**kwargs)

    @property
    def value(self):
        out = {}
        for k, values in self._value.items():
            out_val = [v_elem.value for v_elem in values]
            if self.Meta.elements_definitions[k].max_occurs == 1:
                out_val = out_val[0] if out_val else None
            out[k] = out_val
        return out

    @property
    def xml_value(self):
        out = {}
        for k, values in self._value.items():
            out_val = [v_elem.xml_value for v_elem in values]
            if self.Meta.elements_definitions[k].max_occurs == 1:
                out_val = out_val[0] if out_val else None
            out[k] = out_val
        return out

    @classmethod
    def _get_elements_definitions(cls) -> Dict[str, Element]:
        if chain_hasattr(cls, "Meta.elements_definitions"):
            return cls.Meta.elements_definitions
        return {
            k: getattr(cls, k)
            for k in filter(lambda k: isinstance(getattr(cls, k), Element), dir(cls))
        }
