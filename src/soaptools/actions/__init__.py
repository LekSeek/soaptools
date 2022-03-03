from typing import List, Type

from soaptools.actions.action import Action
from soaptools.actions.generate_bindings import GenerateBindingsAction
from soaptools.actions.generate_client import GenerateClientAction

ALL_ACTIONS: List[Type[Action]] = [
    GenerateBindingsAction,
    GenerateClientAction
]
