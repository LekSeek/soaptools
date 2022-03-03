from dataclasses import dataclass
from typing import List, Dict


class RestrictionRuleDeclaration:
    pass


@dataclass
class RestrictionDeclaration:
    base: str
    rules: List[RestrictionRuleDeclaration]


@dataclass
class MinInclusiveRestrictionDeclaration(RestrictionRuleDeclaration):
    min: int


@dataclass
class MaxInclusiveRestrictionDeclaration(RestrictionRuleDeclaration):
    max: int


@dataclass
class EnumerationRestrictionDeclaration(RestrictionRuleDeclaration):
    enumeration_options: Dict[str, str]


@dataclass
class PatternRestrictionDeclaration(RestrictionRuleDeclaration):
    pattern: str

