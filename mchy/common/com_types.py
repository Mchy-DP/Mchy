from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Sequence, Tuple, Union

from mchy.errors import UnreachableError


class ExecCoreTypes(Enum):
    WORLD = "world"
    ENTITY = "Entity"
    PLAYER = "Player"


class InertCoreTypes(Enum):
    NULL = "null"
    BOOL = "bool"
    INT = "int"
    FLOAT = "float"
    STR = "str"


VALID_TYPE_STRINGS: List[str] = [e.value for e in ExecCoreTypes] + [e.value for e in InertCoreTypes]

CoreTypes = Union[ExecCoreTypes, InertCoreTypes]


class ComType(ABC):

    @abstractmethod
    def render(self) -> str:
        """Renders in a human readable way"""
        ...

    def is_intable(self) -> bool:
        return (
            isinstance(self, InertType) and
            (self.target in (InertCoreTypes.INT, InertCoreTypes.BOOL)) and
            (self.nullable is False)
        )


class TypeUnion:
    """Type unions indicate that the type can be any of the members of the union, as such all members of the union must be handled"""

    def __init__(self, *types: ComType) -> None:
        if len(types) == 0:
            raise ValueError("Types unions cannot be empty")
        self._types = tuple(types)

    @property
    def types(self) -> Tuple[ComType, ...]:
        return self._types

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.render()})"

    def render(self) -> str:
        return "Union[" + ', '.join([typ.render() for typ in self._types]) + "]"


class StructCoreType:
    """Unique instance created for every struct type requested by libraries"""

    def __init__(self, ns_rendering: str, name: str) -> None:
        self.ns_rendering: str = ns_rendering
        self.name = name


class ExecType(ComType):

    __match_args__ = ('target', 'group')

    def __init__(self, target: ExecCoreTypes, group: bool) -> None:
        self.target: ExecCoreTypes = target
        self.group: bool = group

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ExecType):
            return (self.target == other.target) and (self.group == other.group)
        return False

    def __hash__(self) -> int:
        return hash((self.target, self.group))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.render()})"

    def render(self) -> str:
        return f"Group[{self.target.value}]" if self.group else self.target.value


class InertType(ComType):

    __match_args__ = ('target', 'const', 'nullable')

    def __init__(self, target: InertCoreTypes, const: bool = False, nullable: bool = False) -> None:
        self.target: InertCoreTypes = target
        self.const: bool = const
        self.nullable: bool = nullable

    def __eq__(self, other: object) -> bool:
        if isinstance(other, InertType):
            return (self.target == other.target) and (self.const == other.const) and (self.nullable == other.nullable)
        return False

    def __hash__(self) -> int:
        return hash((self.target, self.const, self.nullable))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.render()})"

    def render(self) -> str:
        return f"{self.target.value}" + ("!" if self.const else "") + ("?" if self.nullable else "")


class StructType(ComType):

    def __init__(self, target: StructCoreType) -> None:  # TODO: add nullable?
        self.target: StructCoreType = target

    def __eq__(self, other: object) -> bool:
        if isinstance(other, StructType):
            return (self.target == other.target)
        return False

    def __hash__(self) -> int:
        return hash(self.target)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.render()})"

    def render(self) -> str:
        return f"{self.target.ns_rendering}::{self.target.name}"


def matches_type(guard_type: Union[TypeUnion, ComType], challenge_type: ComType) -> bool:
    """Returns true if a challenge type matches a guard type (similar to `is_subclass`)

    e.g.
    guard: Mammal          & Challenge: Dog   -> True  (because anything valid on mammal is valid on dog)
    guard: Entity          & Challenge: world -> False (because entity only commands cannot be used on world)
    guard: Union[int, str] & challenge: int   -> True  (because int is a member of the guard union)

    Args:
        guard_type: The type to test the challenge for matches against
        challenge_type: The type to test against the guard

    Returns:
        bool: True if actions valid on the guard type are valid on the challenge type, false otherwise
    """
    if guard_type == challenge_type:
        return True

    if isinstance(guard_type, StructType) and isinstance(challenge_type, StructType):
        return guard_type.target == challenge_type.target
    elif isinstance(guard_type, StructType) or (isinstance(challenge_type, StructType) and not isinstance(guard_type, TypeUnion)):
        return False  # Struct guards will never match non-struct challenges & struct challenges will never match non-(struct/type-union) guards
    elif isinstance(guard_type, ExecType) and isinstance(challenge_type, ExecType):
        if (
                    (guard_type.target == challenge_type.target) or
                    (guard_type.target == ExecCoreTypes.ENTITY and challenge_type.target in {ExecCoreTypes.ENTITY, ExecCoreTypes.PLAYER}) or
                    (guard_type.target == ExecCoreTypes.WORLD and challenge_type.target in {ExecCoreTypes.WORLD, ExecCoreTypes.ENTITY, ExecCoreTypes.PLAYER})
                ) and ((guard_type.group is True or guard_type.target == ExecCoreTypes.WORLD) or (challenge_type.group is False)):
            return True  # A group guard accepts singular challenges of the same or subset types
    elif (isinstance(guard_type, ExecType) and isinstance(challenge_type, InertType)) or (isinstance(guard_type, InertType) and isinstance(challenge_type, ExecType)):
        return False  # mismatched ExecType/InertType can never be a valid match
    elif isinstance(guard_type, InertType) and isinstance(challenge_type, InertType):
        if (
                    (challenge_type.target == guard_type.target) or
                    (challenge_type.target == InertCoreTypes.NULL and guard_type.nullable) or     # Nullable guards accept null
                    (guard_type.target == InertCoreTypes.INT and challenge_type.is_intable()) or  # Int guards accept any subclass of int
                    (guard_type.target == InertCoreTypes.FLOAT and challenge_type.is_intable())   # Float guards also accept any subclass of int
                ) and ((guard_type.const is False) or (challenge_type.const is True)) and ((guard_type.nullable is True) or (challenge_type.nullable is False)):
            return True
    elif isinstance(guard_type, TypeUnion):
        return any(matches_type(typ, challenge_type) for typ in guard_type.types)
    else:
        raise UnreachableError(f"Type types unexpectedly did not match any option {guard_type.render()} vs {challenge_type.render()}")
    return False


def cast_bool_to_int(cast_type: ComType):
    if isinstance(cast_type, InertType):
        if cast_type.target == InertCoreTypes.BOOL:
            return InertType(InertCoreTypes.INT, cast_type.const, cast_type.nullable)
    return cast_type


def executor_prefix(exec_type: ExecType, postfix: str, explicit_world: bool = False) -> str:
    if exec_type.target == ExecCoreTypes.WORLD:
        if explicit_world:
            return "world" + postfix
        else:
            return ""
    elif exec_type.target == ExecCoreTypes.ENTITY:
        if exec_type.group:
            return "Entities" + postfix
        else:
            return "Entity" + postfix
    elif exec_type.target == ExecCoreTypes.PLAYER:
        if exec_type.group:
            return "Players" + postfix
        else:
            return "Player" + postfix
    else:
        raise UnreachableError("Unhandled enum case")
