from abc import abstractmethod
from dataclasses import dataclass, field as dataclass_field
from typing import Collection, Dict, List, Optional, Sequence, Tuple, Type, Union

from mchy.cmd_modules.chains import IChain, IChainLink
from mchy.cmd_modules.function import IParam
from mchy.cmd_modules.helper import NULL_CTX_TYPE, get_key_with_type
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.common.config import Config
from mchy.contextual.struct.expr import CtxChainLink, CtxExprLitStr, CtxExprLits, CtxExprNode
from mchy.contextual.struct.expr.literals import CtxExprLitNull
from mchy.errors import StatementRepError
from mchy.library.std.ns import STD_NAMESPACE
from mchy.stmnt.struct import SmtAtom, SmtCmd, SmtFunc, SmtModule
from mchy.stmnt.struct.atoms import SmtConstFloat, SmtConstInt, SmtConstNull, SmtConstStr, SmtVar
from mchy.stmnt.struct.cmds.tag_ops import SmtRawEntitySelector


# ===== SELECTOR BUILDER =====

@dataclass
class SelectorBuilder:
    core: Optional[str] = None
    limit: Optional[int] = None
    sort: Optional[str] = None
    from_x: Optional[int] = None
    from_y: Optional[int] = None
    from_z: Optional[int] = None
    distance_min: Optional[float] = None
    distance_max: Optional[float] = None
    from_dx: Optional[int] = None
    from_dy: Optional[int] = None
    from_dz: Optional[int] = None
    required_team: Optional[str] = None
    prohibited_teams: List[str] = dataclass_field(default_factory=list)
    check_any_team: Optional[bool] = None
    check_no_team: Optional[bool] = None
    required_tags: List[str] = dataclass_field(default_factory=list)
    prohibited_tags: List[str] = dataclass_field(default_factory=list)
    required_scores: List[Tuple[str, Optional[int], Optional[int]]] = dataclass_field(default_factory=list)
    name: Optional[str] = None
    entity_type: Optional[str] = None
    required_predicates: List[str] = dataclass_field(default_factory=list)
    prohibited_predicates: List[str] = dataclass_field(default_factory=list)
    rotate_hrz_min: Optional[int] = None
    rotate_hrz_max: Optional[int] = None
    rotate_vert_min: Optional[int] = None
    rotate_vert_max: Optional[int] = None
    required_nbt: List[str] = dataclass_field(default_factory=list)
    prohibited_nbt: List[str] = dataclass_field(default_factory=list)
    level_min: Optional[int] = None
    level_max: Optional[int] = None
    required_gamemode: Optional[str] = None
    prohibited_gamemodes: List[str] = dataclass_field(default_factory=list)
    advancements: List[str] = dataclass_field(default_factory=list)  # advancements={story/mine_stone=true,story/smelt_iron=true}

    def build(self) -> str:
        if self.core is None:
            raise StatementRepError("Attempting to build SelectorBuilder without 'core' set")
        filters: List[str] = []
        # limitations
        if self.limit is not None:
            filters.append(f"limit={str(self.limit)}")
        if self.sort is not None:
            filters.append(f"sort={self.sort}")
        # positioning
        if self.from_x is not None:
            filters.append(f"x={self.from_x}")
        if self.from_y is not None:
            filters.append(f"y={self.from_y}")
        if self.from_z is not None:
            filters.append(f"z={self.from_z}")
        # distance
        if (self.distance_min is not None) or (self.distance_max is not None):
            filters.append(
                f"distance={(self.distance_min if self.distance_min is not None else '')}.." +
                f"{(self.distance_max if self.distance_max is not None else '')}"
            )
        # volume
        if self.from_dx is not None:
            filters.append(f"dx={self.from_dx}")
        if self.from_dy is not None:
            filters.append(f"dy={self.from_dy}")
        if self.from_dz is not None:
            filters.append(f"dz={self.from_dz}")
        # team
        if self.required_team is not None:
            filters.append(f"team={self.required_team}")
        for prohibited_team in self.prohibited_teams:
            filters.append(f"team=!{prohibited_team}")
        if self.check_any_team is not None:
            filters.append(f"team=!")
        if self.check_no_team is not None:
            filters.append(f"team=")
        # tags
        for req_tag in self.required_tags:
            filters.append(f"tag={req_tag}")
        for prohibited_tag in self.prohibited_tags:
            filters.append(f"tag=!{prohibited_tag}")
        # scores
        if len(self.required_scores) > 0:
            # scores={foo=10,bar=1..5}
            scores: List[str] = []
            for score, smin, smax in self.required_scores:
                scores.append(f"{score}={(smin if smin is not None else '')}..{(smax if smax is not None else '')}")
            filters.append("scores={"+",".join(scores)+"}")
        # name
        if self.name is not None:
            filters.append(f'name="{self.name}"')
        # type
        if self.entity_type is not None:
            filters.append(f"type={self.entity_type}")
        # predicates
        for req_pred in self.required_predicates:
            filters.append(f"predicate={req_pred}")
        for prohibited_pred in self.prohibited_predicates:
            filters.append(f"predicate=!{prohibited_pred}")
        # rotate
        if (self.rotate_hrz_min is not None) or (self.rotate_hrz_max is not None):
            filters.append(
                f"y_rotation={(self.rotate_hrz_min if self.rotate_hrz_min is not None else '')}.." +
                f"{(self.rotate_hrz_max if self.rotate_hrz_max is not None else '')}"
            )
        if (self.rotate_vert_min is not None) or (self.rotate_vert_max is not None):
            filters.append(
                f"x_rotation={(self.rotate_vert_min if self.rotate_vert_min is not None else '')}.." +
                f"{(self.rotate_vert_max if self.rotate_vert_max is not None else '')}"
            )
        # nbt
        for req_nbt in self.required_nbt:
            filters.append(f"nbt={req_nbt}")
        for prohibited_nbt in self.prohibited_nbt:
            filters.append(f"nbt=!{prohibited_nbt}")
        # level
        if (self.level_min is not None) or (self.level_max is not None):
            filters.append(
                f"level={(self.level_min if self.level_min is not None else '')}.." +
                f"{(self.level_max if self.level_max is not None else '')}"
            )
        # gamemode
        if self.required_gamemode is not None:
            filters.append(f'gamemode={self.required_gamemode}')
        for prohibited_gamemode in self.prohibited_gamemodes:
            filters.append(f'gamemode=!{prohibited_gamemode}')
        # advancements
        if len(self.advancements) > 0:
            # advancements={story/mine_stone=true,story/smelt_iron=true}
            filters.append("advancements={"+",".join(self.advancements)+"}")

        # > render selector <
        if len(filters) >= 1:
            return self.core+"[" + ",".join(filters) + "]"
        else:
            return self.core


# ===== PARENT CLASSES =====
class ChainLinkPartialSelector(IChainLink, abstract=True):

    @abstractmethod
    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        ...


class ChainLinkPartialEntitiesSelector(ChainLinkPartialSelector, abstract=True):

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkPartialEntitiesSelector


class ChainLinkPartialEntitySelector(ChainLinkPartialSelector, abstract=True):

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkPartialEntitySelector


class ChainLinkPartialPlayersSelector(ChainLinkPartialSelector, abstract=True):

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkPartialPlayersSelector


class ChainLinkPartialPlayerSelector(ChainLinkPartialSelector, abstract=True):

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkPartialPlayerSelector


# ===== STARTING POINTS =====
class ChainLinkGetEntities(ChainLinkPartialEntitiesSelector):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "get_entities"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return []

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        builder.core = "@e"


class ChainLinkGetEntity(ChainLinkPartialEntitySelector):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "get_entity"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [IParam("sort", InertType(InertCoreTypes.STR, True), CtxExprLitStr("nearest", src_loc=ComLoc()))]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        builder.core = "@e"
        builder.limit = 1
        builder.sort = get_key_with_type(param_binding, "sort", SmtConstStr).value


class ChainLinkGetPlayers(ChainLinkPartialPlayersSelector):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "get_players"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return []

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        builder.core = "@a"


class ChainLinkGetPlayer(ChainLinkPartialPlayerSelector):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "get_player"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [IParam("sort", InertType(InertCoreTypes.STR, True), CtxExprLitStr("nearest", src_loc=ComLoc()))]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        builder.core = "@a"
        builder.limit = 1
        builder.sort = get_key_with_type(param_binding, "sort", SmtConstStr).value


# ===== FILTERS =====
class ChainLinkPartialSelectorFromPosition(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "from_position"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("x", InertType(InertCoreTypes.INT, const=True)),
            IParam("y", InertType(InertCoreTypes.INT, const=True)),
            IParam("z", InertType(InertCoreTypes.INT, const=True))
        ]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        builder.from_x = get_key_with_type(param_binding, "x", SmtConstInt).value
        builder.from_y = get_key_with_type(param_binding, "y", SmtConstInt).value
        builder.from_z = get_key_with_type(param_binding, "z", SmtConstInt).value


class ChainLinkPartialEntitiesSelectorFromPosition(ChainLinkPartialEntitiesSelector, ChainLinkPartialSelectorFromPosition):
    ...


class ChainLinkPartialEntitySelectorFromPosition(ChainLinkPartialEntitySelector, ChainLinkPartialSelectorFromPosition):
    ...


class ChainLinkPartialPlayersSelectorFromPosition(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorFromPosition):
    ...


class ChainLinkPartialPlayerSelectorFromPosition(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorFromPosition):
    ...


class ChainLinkPartialSelectorInRadius(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "in_radius"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("min", InertType(InertCoreTypes.FLOAT, const=True, nullable=True), CtxExprLitNull(src_loc=ComLoc())),
            IParam("max", InertType(InertCoreTypes.FLOAT, const=True, nullable=True), CtxExprLitNull(src_loc=ComLoc())),
        ]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        try:
            builder.distance_min = get_key_with_type(param_binding, "min", SmtConstFloat).value
        except StatementRepError:
            # This will re-crash if it is neither an int or null
            get_key_with_type(param_binding, "min", SmtConstNull)
            builder.distance_min = None
        try:
            builder.distance_max = get_key_with_type(param_binding, "max", SmtConstFloat).value
        except StatementRepError:
            # This will re-crash if it is neither an int or null
            get_key_with_type(param_binding, "max", SmtConstNull)
            builder.distance_max = None


class ChainLinkPartialEntitiesSelectorInRadius(ChainLinkPartialEntitiesSelector, ChainLinkPartialSelectorInRadius):
    ...


class ChainLinkPartialEntitySelectorInRadius(ChainLinkPartialEntitySelector, ChainLinkPartialSelectorInRadius):
    ...


class ChainLinkPartialPlayersSelectorInRadius(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorInRadius):
    ...


class ChainLinkPartialPlayerSelectorInRadius(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorInRadius):
    ...


class ChainLinkPartialSelectorInVolume(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "in_volume"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("dx", InertType(InertCoreTypes.INT, const=True)),
            IParam("dy", InertType(InertCoreTypes.INT, const=True)),
            IParam("dz", InertType(InertCoreTypes.INT, const=True))
        ]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        builder.from_dx = get_key_with_type(param_binding, "dx", SmtConstInt).value
        builder.from_dy = get_key_with_type(param_binding, "dy", SmtConstInt).value
        builder.from_dz = get_key_with_type(param_binding, "dz", SmtConstInt).value


class ChainLinkPartialEntitiesSelectorInVolume(ChainLinkPartialEntitiesSelector, ChainLinkPartialSelectorInVolume):
    ...


class ChainLinkPartialEntitySelectorInVolume(ChainLinkPartialEntitySelector, ChainLinkPartialSelectorInVolume):
    ...


class ChainLinkPartialPlayersSelectorInVolume(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorInVolume):
    ...


class ChainLinkPartialPlayerSelectorInVolume(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorInVolume):
    ...


class ChainLinkPartialSelectorInTeam(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "in_team"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("team", InertType(InertCoreTypes.STR, const=True, nullable=True))
        ]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        try:
            builder.required_team = get_key_with_type(param_binding, "team", SmtConstStr).value
        except StatementRepError:
            # This will re-crash if it is neither the expected const or null
            get_key_with_type(param_binding, "team", SmtConstNull)
            builder.check_any_team = True


class ChainLinkPartialEntitiesSelectorInTeam(ChainLinkPartialEntitiesSelector, ChainLinkPartialSelectorInTeam):
    ...


class ChainLinkPartialEntitySelectorInTeam(ChainLinkPartialEntitySelector, ChainLinkPartialSelectorInTeam):
    ...


class ChainLinkPartialPlayersSelectorInTeam(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorInTeam):
    ...


class ChainLinkPartialPlayerSelectorInTeam(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorInTeam):
    ...


class ChainLinkPartialSelectorNotInTeam(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "not_in_team"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("team", InertType(InertCoreTypes.STR, const=True))
        ]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        builder.prohibited_teams.append(get_key_with_type(param_binding, "team", SmtConstStr).value)


class ChainLinkPartialEntitiesSelectorNotInTeam(ChainLinkPartialEntitiesSelector, ChainLinkPartialSelectorNotInTeam):
    ...


class ChainLinkPartialEntitySelectorNotInTeam(ChainLinkPartialEntitySelector, ChainLinkPartialSelectorNotInTeam):
    ...


class ChainLinkPartialPlayersSelectorNotInTeam(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorNotInTeam):
    ...


class ChainLinkPartialPlayerSelectorNotInTeam(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorNotInTeam):
    ...


class ChainLinkPartialSelectorInNoTeam(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "with_no_team"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return []

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        builder.check_no_team = True


class ChainLinkPartialEntitiesSelectorInNoTeam(ChainLinkPartialEntitiesSelector, ChainLinkPartialSelectorInNoTeam):
    ...


class ChainLinkPartialEntitySelectorInNoTeam(ChainLinkPartialEntitySelector, ChainLinkPartialSelectorInNoTeam):
    ...


class ChainLinkPartialPlayersSelectorInNoTeam(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorInNoTeam):
    ...


class ChainLinkPartialPlayerSelectorInNoTeam(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorInNoTeam):
    ...


class ChainLinkPartialSelectorWithTag(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "with_tag"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("tag", InertType(InertCoreTypes.STR, const=True))
        ]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        builder.required_tags.append(get_key_with_type(param_binding, "tag", SmtConstStr).value)


class ChainLinkPartialEntitiesSelectorWithTag(ChainLinkPartialEntitiesSelector, ChainLinkPartialSelectorWithTag):
    ...


class ChainLinkPartialEntitySelectorWithTag(ChainLinkPartialEntitySelector, ChainLinkPartialSelectorWithTag):
    ...


class ChainLinkPartialPlayersSelectorWithTag(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorWithTag):
    ...


class ChainLinkPartialPlayerSelectorWithTag(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorWithTag):
    ...


class ChainLinkPartialSelectorNotWithTag(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "without_tag"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("tag", InertType(InertCoreTypes.STR, const=True))
        ]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        builder.prohibited_tags.append(get_key_with_type(param_binding, "tag", SmtConstStr).value)


class ChainLinkPartialEntitiesSelectorNotWithTag(ChainLinkPartialEntitiesSelector, ChainLinkPartialSelectorNotWithTag):
    ...


class ChainLinkPartialEntitySelectorNotWithTag(ChainLinkPartialEntitySelector, ChainLinkPartialSelectorNotWithTag):
    ...


class ChainLinkPartialPlayersSelectorNotWithTag(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorNotWithTag):
    ...


class ChainLinkPartialPlayerSelectorNotWithTag(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorNotWithTag):
    ...


class ChainLinkPartialSelectorWithScore(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "with_score"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("score", InertType(InertCoreTypes.STR, const=True)),
            IParam("min", InertType(InertCoreTypes.INT, const=True, nullable=True), CtxExprLitNull(src_loc=ComLoc())),
            IParam("max", InertType(InertCoreTypes.INT, const=True, nullable=True), CtxExprLitNull(src_loc=ComLoc())),
        ]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        try:
            min_score = get_key_with_type(param_binding, "min", SmtConstInt).value
        except StatementRepError:
            # This will re-crash if it is neither the expected const or null
            get_key_with_type(param_binding, "min", SmtConstNull)
            min_score = None
        try:
            max_score = get_key_with_type(param_binding, "max", SmtConstInt).value
        except StatementRepError:
            # This will re-crash if it is neither the expected const or null
            get_key_with_type(param_binding, "max", SmtConstNull)
            max_score = None
        builder.required_scores.append(
            (
                get_key_with_type(param_binding, "score", SmtConstStr).value,
                min_score,
                max_score
            )
        )


class ChainLinkPartialEntitiesSelectorWithScore(ChainLinkPartialEntitiesSelector, ChainLinkPartialSelectorWithScore):
    ...


class ChainLinkPartialEntitySelectorWithScore(ChainLinkPartialEntitySelector, ChainLinkPartialSelectorWithScore):
    ...


class ChainLinkPartialPlayersSelectorWithScore(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorWithScore):
    ...


class ChainLinkPartialPlayerSelectorWithScore(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorWithScore):
    ...


class ChainLinkPartialSelectorOfType(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "of_type"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [IParam("entity_type", InertType(InertCoreTypes.STR, const=True))]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        builder.entity_type = get_key_with_type(param_binding, "entity_type", SmtConstStr).value


class ChainLinkPartialEntitiesSelectorOfType(ChainLinkPartialEntitiesSelector, ChainLinkPartialSelectorOfType):
    ...


class ChainLinkPartialEntitySelectorOfType(ChainLinkPartialEntitySelector, ChainLinkPartialSelectorOfType):
    ...


class ChainLinkPartialSelectorOfName(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "of_name"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [IParam("name", InertType(InertCoreTypes.STR, const=True))]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        builder.name = get_key_with_type(param_binding, "name", SmtConstStr).value


class ChainLinkPartialEntitiesSelectorOfName(ChainLinkPartialEntitiesSelector, ChainLinkPartialSelectorOfName):
    ...


class ChainLinkPartialEntitySelectorOfName(ChainLinkPartialEntitySelector, ChainLinkPartialSelectorOfName):
    ...


class ChainLinkPartialPlayersSelectorOfName(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorOfName):
    ...


class ChainLinkPartialPlayerSelectorOfName(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorOfName):
    ...


class ChainLinkPartialSelectorPredicatePassing(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "passing_predicate"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("predicate", InertType(InertCoreTypes.STR, const=True))
        ]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        builder.required_predicates.append(get_key_with_type(param_binding, "predicate", SmtConstStr).value)


class ChainLinkPartialEntitiesSelectorPredicatePassing(ChainLinkPartialEntitiesSelector, ChainLinkPartialSelectorPredicatePassing):
    ...


class ChainLinkPartialEntitySelectorPredicatePassing(ChainLinkPartialEntitySelector, ChainLinkPartialSelectorPredicatePassing):
    ...


class ChainLinkPartialPlayersSelectorPredicatePassing(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorPredicatePassing):
    ...


class ChainLinkPartialPlayerSelectorPredicatePassing(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorPredicatePassing):
    ...


class ChainLinkPartialSelectorPredicateFailing(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "failing_predicate"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("predicate", InertType(InertCoreTypes.STR, const=True))
        ]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        builder.prohibited_predicates.append(get_key_with_type(param_binding, "predicate", SmtConstStr).value)


class ChainLinkPartialEntitiesSelectorPredicateFailing(ChainLinkPartialEntitiesSelector, ChainLinkPartialSelectorPredicateFailing):
    ...


class ChainLinkPartialEntitySelectorPredicateFailing(ChainLinkPartialEntitySelector, ChainLinkPartialSelectorPredicateFailing):
    ...


class ChainLinkPartialPlayersSelectorPredicateFailing(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorPredicateFailing):
    ...


class ChainLinkPartialPlayerSelectorPredicateFailing(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorPredicateFailing):
    ...


class ChainLinkPartialSelectorWithVertRot(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "with_vert_rot"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("min", InertType(InertCoreTypes.INT, const=True)),
            IParam("max", InertType(InertCoreTypes.INT, const=True))
        ]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        try:
            builder.rotate_vert_min = get_key_with_type(param_binding, "min", SmtConstInt).value
        except StatementRepError:
            # This will re-crash if it is neither an int or null
            get_key_with_type(param_binding, "min", SmtConstNull)
            builder.rotate_vert_min = None
        try:
            builder.rotate_vert_max = get_key_with_type(param_binding, "max", SmtConstInt).value
        except StatementRepError:
            # This will re-crash if it is neither an int or null
            get_key_with_type(param_binding, "max", SmtConstNull)
            builder.rotate_vert_max = None


class ChainLinkPartialEntitiesSelectorWithVertRot(ChainLinkPartialEntitiesSelector, ChainLinkPartialSelectorWithVertRot):
    ...


class ChainLinkPartialEntitySelectorWithVertRot(ChainLinkPartialEntitySelector, ChainLinkPartialSelectorWithVertRot):
    ...


class ChainLinkPartialPlayersSelectorWithVertRot(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorWithVertRot):
    ...


class ChainLinkPartialPlayerSelectorWithVertRot(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorWithVertRot):
    ...


class ChainLinkPartialSelectorWithHrzRot(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "with_hrz_rot"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("min", InertType(InertCoreTypes.INT, const=True)),
            IParam("max", InertType(InertCoreTypes.INT, const=True))
        ]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        try:
            builder.rotate_hrz_min = get_key_with_type(param_binding, "min", SmtConstInt).value
        except StatementRepError:
            # This will re-crash if it is neither an int or null
            get_key_with_type(param_binding, "min", SmtConstNull)
            builder.rotate_hrz_min = None
        try:
            builder.rotate_hrz_max = get_key_with_type(param_binding, "max", SmtConstInt).value
        except StatementRepError:
            # This will re-crash if it is neither an int or null
            get_key_with_type(param_binding, "max", SmtConstNull)
            builder.rotate_hrz_max = None


class ChainLinkPartialEntitiesSelectorWithHrzRot(ChainLinkPartialEntitiesSelector, ChainLinkPartialSelectorWithHrzRot):
    ...


class ChainLinkPartialEntitySelectorWithHrzRot(ChainLinkPartialEntitySelector, ChainLinkPartialSelectorWithHrzRot):
    ...


class ChainLinkPartialPlayersSelectorWithHrzRot(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorWithHrzRot):
    ...


class ChainLinkPartialPlayerSelectorWithHrzRot(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorWithHrzRot):
    ...


class ChainLinkPartialSelectorMatchingNbt(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "matching_nbt"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("nbt", InertType(InertCoreTypes.STR, const=True))
        ]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        builder.required_nbt.append(get_key_with_type(param_binding, "nbt", SmtConstStr).value)


class ChainLinkPartialEntitiesSelectorMatchingNbt(ChainLinkPartialEntitiesSelector, ChainLinkPartialSelectorMatchingNbt):
    ...


class ChainLinkPartialEntitySelectorMatchingNbt(ChainLinkPartialEntitySelector, ChainLinkPartialSelectorMatchingNbt):
    ...


class ChainLinkPartialPlayersSelectorMatchingNbt(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorMatchingNbt):
    ...


class ChainLinkPartialPlayerSelectorMatchingNbt(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorMatchingNbt):
    ...


class ChainLinkPartialSelectorNotMatchingNbt(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "not_matching_nbt"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("nbt", InertType(InertCoreTypes.STR, const=True))
        ]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        builder.prohibited_nbt.append(get_key_with_type(param_binding, "nbt", SmtConstStr).value)


class ChainLinkPartialEntitiesSelectorNotMatchingNbt(ChainLinkPartialEntitiesSelector, ChainLinkPartialSelectorNotMatchingNbt):
    ...


class ChainLinkPartialEntitySelectorNotMatchingNbt(ChainLinkPartialEntitySelector, ChainLinkPartialSelectorNotMatchingNbt):
    ...


class ChainLinkPartialPlayersSelectorNotMatchingNbt(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorNotMatchingNbt):
    ...


class ChainLinkPartialPlayerSelectorNotMatchingNbt(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorNotMatchingNbt):
    ...


class ChainLinkPartialSelectorWithLevel(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "with_level"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("min", InertType(InertCoreTypes.INT, const=True)),
            IParam("max", InertType(InertCoreTypes.INT, const=True))
        ]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        try:
            builder.level_min = get_key_with_type(param_binding, "min", SmtConstInt).value
        except StatementRepError:
            # This will re-crash if it is neither an int or null
            get_key_with_type(param_binding, "min", SmtConstNull)
            builder.level_min = None
        try:
            builder.level_max = get_key_with_type(param_binding, "max", SmtConstInt).value
        except StatementRepError:
            # This will re-crash if it is neither an int or null
            get_key_with_type(param_binding, "max", SmtConstNull)
            builder.level_max = None


class ChainLinkPartialPlayersSelectorWithLevel(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorWithLevel):
    ...


class ChainLinkPartialPlayerSelectorWithLevel(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorWithLevel):
    ...


class ChainLinkPartialSelectorInGamemode(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "in_gamemode"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("mode", InertType(InertCoreTypes.STR, const=True))
        ]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        builder.required_gamemode = get_key_with_type(param_binding, "mode", SmtConstStr).value


class ChainLinkPartialPlayersSelectorInGamemode(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorInGamemode):
    ...


class ChainLinkPartialPlayerSelectorInGamemode(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorInGamemode):
    ...


class ChainLinkPartialSelectorNotInGamemode(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "not_in_gamemode"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("mode", InertType(InertCoreTypes.STR, const=True))
        ]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        builder.prohibited_gamemodes.append(get_key_with_type(param_binding, "mode", SmtConstStr).value)


class ChainLinkPartialPlayersSelectorNotInGamemode(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorNotInGamemode):
    ...


class ChainLinkPartialPlayerSelectorNotInGamemode(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorNotInGamemode):
    ...


class ChainLinkPartialSelectorAdvancementMatches(ChainLinkPartialSelector, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "advancement_matches"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("advancement", InertType(InertCoreTypes.STR, const=True))
        ]

    def build_selector(self, builder: SelectorBuilder, param_binding: Dict[str, SmtAtom]) -> None:
        builder.advancements.append(get_key_with_type(param_binding, "advancement", SmtConstStr).value)


class ChainLinkPartialPlayersSelectorAdvancementMatches(ChainLinkPartialPlayersSelector, ChainLinkPartialSelectorAdvancementMatches):
    ...


class ChainLinkPartialPlayerSelectorAdvancementMatches(ChainLinkPartialPlayerSelector, ChainLinkPartialSelectorAdvancementMatches):
    ...


# ===== TERMINAL =====
class ChainPartialSelectorFind(IChain, abstract=True):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "find"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return []

    def stmnt_conv(
            self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]], module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        # build selector
        selector_builder = SelectorBuilder()
        for link, param_binding, _ in clink_param_binding:
            if isinstance(link, ChainPartialSelectorFind):
                continue  # No need to parse the chain itself
            if not isinstance(link, ChainLinkPartialSelector):
                raise StatementRepError(f"Link that does not derive from `{ChainLinkPartialSelector.__name__}` encountered in find (unknown_link={type(link).__name__})")
            link.build_selector(selector_builder, param_binding)
        # output
        output_register: SmtVar
        if isinstance(clink_param_binding[0][0], ChainLinkGetEntities):
            output_register = function.new_pseudo_var(ExecType(ExecCoreTypes.ENTITY, True))
        elif isinstance(clink_param_binding[0][0], ChainLinkGetEntity):
            output_register = function.new_pseudo_var(ExecType(ExecCoreTypes.ENTITY, False))
        elif isinstance(clink_param_binding[0][0], ChainLinkGetPlayers):
            output_register = function.new_pseudo_var(ExecType(ExecCoreTypes.PLAYER, True))
        elif isinstance(clink_param_binding[0][0], ChainLinkGetPlayer):
            output_register = function.new_pseudo_var(ExecType(ExecCoreTypes.PLAYER, False))
        else:
            raise StatementRepError(f"Unknown starting chain link `{type(clink_param_binding[0][0]).__name__}`")
        return [SmtRawEntitySelector(executor, output_register, selector_builder.build())], output_register


class ChainPartialEntitiesSelectorFind(ChainPartialSelectorFind):

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkPartialEntitiesSelector

    def get_chain_type(self) -> ComType:
        return ExecType(ExecCoreTypes.ENTITY, True)


class ChainPartialEntitySelectorFind(ChainPartialSelectorFind):

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkPartialEntitySelector

    def get_chain_type(self) -> ComType:
        return ExecType(ExecCoreTypes.ENTITY, False)


class ChainPartialPlayersSelectorFind(ChainPartialSelectorFind):

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkPartialPlayersSelector

    def get_chain_type(self) -> ComType:
        return ExecType(ExecCoreTypes.PLAYER, True)


class ChainPartialPlayerSelectorFind(ChainPartialSelectorFind):

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkPartialPlayerSelector

    def get_chain_type(self) -> ComType:
        return ExecType(ExecCoreTypes.PLAYER, False)
