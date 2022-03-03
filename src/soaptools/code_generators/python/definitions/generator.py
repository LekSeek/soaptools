import ast
import copy
from collections import OrderedDict
from typing import List

from soaptools.code_generators.python.definitions.types import BASE_TYPES, AnyType
from soaptools.helpers.py import Duration
from soaptools.soap.schema_parser.declarations import SimpleTypeDeclaration, ComplexTypeDeclaration, ElementDeclaration, Declaration, \
    TypeDeclaration
from soaptools.helpers.text_cases import to_upper_camel_case, to_snake_case
from soaptools.soap.schema_parser.restriction_elements import MinInclusiveRestrictionDeclaration, \
    EnumerationRestrictionDeclaration, MaxInclusiveRestrictionDeclaration, PatternRestrictionDeclaration, \
    RestrictionDeclaration


class TypesRegistry:
    def __init__(self):
        self.__storage = OrderedDict()

    def add_predefined_base_type(self, definition: AnyType):
        self.__storage["type" + definition.identifier] = {"name": "xs." + definition.__name__, "def": None}

    def add_type_class_def(self, identifier: str, class_def: ast.ClassDef):
        composite_identifier = "type" + identifier
        self.__storage[composite_identifier] = {"name": class_def.name, "def": class_def}

    def add_element_class_def(self, identifier: str, class_def: ast.ClassDef):
        composite_identifier = "element" + identifier
        self.__storage[composite_identifier] = {"name": class_def.name, "def": class_def}

    def get_type_by_identifier(self, identifier):
        return self.__storage.get("type" + identifier)

    def get_element_by_identifier(self, identifier):
        return self.__storage.get("element" + identifier)

    def get_all_class_definitions(self):
        return filter(bool, map(lambda val: val["def"], self.__storage.values()))


class TypesCodeGenerator:

    def __init__(self, all_declarations: List[TypeDeclaration], generate_only_declarations: List[TypeDeclaration] = None):
        """

        :param all_declarations:
        :param generate_only_declarations: sublist of all_declarations
        """

        self.declarations = copy.deepcopy(all_declarations)
        self.generate_only_declarations = copy.deepcopy(generate_only_declarations)
        self.generated_types_registry = TypesRegistry()

        for base_type in BASE_TYPES:
            self.generated_types_registry.add_predefined_base_type(base_type)

    def generate(self) -> ast.Module:
        # todo: dont import unnecessary things
        acc = [
            ast.ImportFrom(
                module="soaptools.code_generators.python.definitions.types.base",
                names=[
                    ast.alias(name="SimpleType"),
                    ast.alias(name="ComplexType"),
                    ast.alias(name="Element"),
                ],
                level=0
            ),
            ast.ImportFrom(
                module="soaptools.code_generators.python.definitions.types",
                names=[ast.alias(name="xs")],
                level=0
            ),
            ast.ImportFrom(
                module="soaptools.code_generators.python.definitions.restriction_elements",
                names=[
                    ast.alias(name="MinInclusive"),
                    ast.alias(name="MaxInclusive"),
                    ast.alias(name="Enumeration"),
                    ast.alias(name="Pattern"),
                    ast.alias(name="Restriction"),
                ],
                level=0
            ),
            ast.ImportFrom(
                module="soaptools.helpers.py",
                names=[
                    ast.alias(name="Duration"),
                ],
                level=0
            ),
        ]
        declarations_to_generate = self.generate_only_declarations or self.declarations
        for declaration in declarations_to_generate:
            # ignore if element declaration is identical to type declaration:
            if (
                isinstance(declaration, ElementDeclaration) and
                any(filter(lambda i_decl: i_decl.identifier == declaration.identifier and isinstance(i_decl, TypeDeclaration), self.declarations))
            ):
                continue
            self.__generate_type_from_declaration(declaration)
        for class_def in self.generated_types_registry.get_all_class_definitions():
            acc.append(class_def)

        return ast.Module(body=acc, type_ignores=[])

    def __get_type_name_from_identifier(self, identifier):
        generated_type = self.generated_types_registry.get_type_by_identifier(identifier)
        if generated_type:
            return generated_type["name"]

        declaration_to_generate = next(filter(lambda declaration: isinstance(declaration, TypeDeclaration) and declaration.identifier == identifier, self.declarations), None)
        if not declaration_to_generate:
            raise self.TypeNotFoundException(identifier)
        generated_class_def = self.__generate_type_from_declaration(declaration_to_generate)
        return generated_class_def.name

    def __generate_type_from_declaration(self, declaration: Declaration):
        if isinstance(declaration, TypeDeclaration):
            if found := self.generated_types_registry.get_type_by_identifier(declaration.identifier):
                return found["def"]
            if isinstance(declaration, SimpleTypeDeclaration):
                class_def = self.__generate_simple_type_class(declaration)
            elif isinstance(declaration, ComplexTypeDeclaration):
                class_def = self.__generate_complex_type_class(declaration)
            else:
                raise Exception()
            self.generated_types_registry.add_type_class_def(declaration.identifier, class_def)
        elif isinstance(declaration, ElementDeclaration):
            if found := self.generated_types_registry.get_element_by_identifier(declaration.identifier):
                return found["def"]
            class_def = self.__generate_element_class(declaration)
            self.generated_types_registry.add_element_class_def(declaration.identifier, class_def)
        else:
            raise Exception()
        return class_def

    def __generate_simple_type_class(self, declaration: SimpleTypeDeclaration):
        body = []
        base_class_name = "SimpleType"
        if declaration.restriction.base:
            base_class_name = self.__get_type_name_from_identifier(declaration.restriction.base)
        meta_class = self.__get_metadata_class(declaration)
        if declaration.restriction.rules:
            meta_class.body.append(
                ast.Assign(
                    targets=[ast.Name(id="restriction")],
                    value=self.__generate_restriction_class_instance(declaration.restriction),
                    lineno=1
                )
            )
        body.append(meta_class)
        return ast.ClassDef(
            name=to_upper_camel_case(declaration.name) + "SimpleType",
            bases=[ast.Name(id=base_class_name)],
            body=body,
            decorator_list=[],
            keywords=[]
        )

    def __generate_complex_type_class(self, declaration: ComplexTypeDeclaration, class_name:str = None):
        body = []
        constructor_attributes = []

        for sub_element in declaration.elements:
            constructor_attrib = {"name": sub_element.name}
            if sub_element.min_occurs == 0:
                constructor_attrib["default"] = None
            constructor_attributes.append(constructor_attrib)
            body.append(
                ast.Assign(
                    targets=[ast.Name(id=sub_element.name)],
                    value=self.__get_subelement_declaration(sub_element),
                    lineno=1
                ),
            )
        if constructor_attributes:
            body.append(self.__get_constructor(constructor_attributes))
        body.append(self.__get_metadata_class(declaration))
        return ast.ClassDef(
            name=class_name or to_upper_camel_case(declaration.name) + "ComplexType",
            bases=[ast.Name(id="ComplexType")],
            body=body,
            decorator_list=[],
            keywords=[]
        )

    def __generate_element_class(self, declaration: ElementDeclaration):
        class_name = to_upper_camel_case(declaration.name) + "Element"
        if type := declaration.type:
            return ast.ClassDef(
                name=class_name,
                bases=[ast.Name(id=self.__get_type_name_from_identifier(type))],
                body=[self.__get_metadata_class(declaration)],
                decorator_list=[],
                keywords=[]
            )
        elif declaration.elements is not None:
            return self.__generate_complex_type_class(declaration, class_name)
        else:
            raise Exception()

    def __get_subelement_declaration(self, sub_element: ElementDeclaration):
        element_kwargs_names = ["default", "fixed", "id"]
        element_kwargs = {}
        for attr_name in element_kwargs_names:
            declaration_attr_name = to_snake_case(attr_name)
            if declaration_attr_name not in sub_element.__dict__ or sub_element.__dict__[declaration_attr_name] == None:
                continue
            element_kwargs[to_snake_case(attr_name)] = ast.Constant(value=getattr(sub_element, declaration_attr_name))

        if sub_element.min_occurs != 1:
            element_kwargs["min_occurs"] = ast.Constant(value=sub_element.min_occurs)
        if sub_element.max_occurs != 1:
            element_kwargs["max_occurs"] = ast.Constant(value=sub_element.max_occurs)
        if "type" in sub_element.__dict__:  # add find_type
            element_kwargs["type"] = ast.Name(id=self.__get_type_name_from_identifier(sub_element.type))

        return ast.Call(
            func=ast.Name(id="Element"),
            args=[],
            keywords=[
                ast.keyword(arg=key, value=val)
                for key, val in element_kwargs.items()
            ]
        )

    def __get_metadata_info(self, declaration: Declaration):
        return {
            "name": declaration.name,
            "targetNamespace": declaration.target_namespace
        }

    def __get_metadata_class(self, declaration: Declaration):
        return ast.ClassDef(
            name="Meta",
            body=[
                ast.Assign(targets=[ast.Name(id=key)], value=ast.Constant(val), lineno=1)
                for key, val in self.__get_metadata_info(declaration).items()
            ],
            decorator_list=[],
            keywords=[],
            bases=[]
        )

    def __get_constructor(self, attributes):
        args = [ast.arg(arg="self")]
        kw_defaults = [None]
        for attr in attributes:
            args.append(ast.arg(arg=attr["name"]))
            kw_defaults.append(ast.Constant(value=attr["default"]) if "default" in attr else None)

        return ast.FunctionDef(
            name="__init__",
            args=ast.arguments(
                posonlyargs=[],
                kwonlyargs=[],
                args=args,
                defaults=kw_defaults,
            ),
            decorator_list=[],
            lineno=1,
            body=[
                ast.Call(
                    func=ast.Name(id="super().__init__"),
                    args=[],
                    keywords=[
                        ast.keyword(arg=attribute["name"], value=ast.Name(id=attribute["name"]))
                        for attribute in attributes
                    ]
                )
            ]
        )

    def __generate_restriction_class_instance(self, restriction_declaration: RestrictionDeclaration):
        rules = []
        for rule in restriction_declaration.rules:
            if isinstance(rule, MinInclusiveRestrictionDeclaration):
                rules.append(ast.Call(
                    func=ast.Name(id="MinInclusive"),
                    args=[],
                    keywords=[ast.keyword(arg="min", value=self.__get_pythonic_value_ast(rule.min))]))
            elif isinstance(rule, MaxInclusiveRestrictionDeclaration):
                rules.append(ast.Call(
                    func=ast.Name(id="MaxInclusive"),
                    args=[],
                    keywords=[ast.keyword(arg="max", value=self.__get_pythonic_value_ast(rule.max))]))
            elif isinstance(rule, EnumerationRestrictionDeclaration):
                keys = []
                values = []
                for k, v in rule.enumeration_options.items():
                    keys.append(ast.Constant(value=k))
                    values.append(ast.Constant(value=v))
                rules.append(ast.Call(
                    func=ast.Name(id="Enumeration"),
                    args=[],
                    keywords=[ast.keyword(arg="accepted_values", value=ast.Dict(keys=keys, values=values))]
                ))
            elif isinstance(rule, PatternRestrictionDeclaration):
                rules.append(ast.Call(
                    func=ast.Name(id="Pattern"),
                    args=[],
                    keywords=[ast.keyword(arg="pattern", value=ast.Constant(value=rule.pattern))])
                )
        kwargs = []
        if rules:
            kwargs.append(ast.keyword(arg="rules", value=ast.List(elts=rules)))

        return ast.Call(
            func=ast.Name(id="Restriction"),
            args=[],
            keywords=kwargs
        )

    def __get_pythonic_value_ast(self, value):
        try:
            Duration.from_iso8601(value)
            return ast.Call(
                func=ast.Name(id="Duration.from_iso8601"),
                args=[ast.Constant(value=value)],
                keywords=[]
            )
        except ValueError as e:
            pass
        if value.__class__ in [bool, str, int, float]:
            return ast.Constant(value=value)
        else:
            raise Exception()

    class TypeNotFoundException(Exception):
        pass
