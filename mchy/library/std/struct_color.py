from typing import Any, Collection, Dict, List, Optional, Sequence, Tuple, Type, Union

from mchy.cmd_modules.chains import IChain, IChainLink
from mchy.cmd_modules.function import IParam
from mchy.cmd_modules.helper import NULL_CTX_TYPE
from mchy.cmd_modules.name_spaces import Namespace
from mchy.cmd_modules.struct import IField, IStruct
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.common.config import Config
from mchy.contextual.struct.expr import CtxChainLink, CtxExprLits, CtxExprLitStr, CtxExprNode, CtxExprPyStruct
from mchy.contextual.struct.expr.structs import CtxPyStruct
from mchy.library.std.ns import STD_NAMESPACE


class StructColor(IStruct):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "Color"

    def get_fields(self) -> Sequence[IField]:
        return [
            IField("color_code", str),
        ]


class ChainLinkColor(IChainLink):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "colors"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None


class ChainColorBlack(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkColor

    def get_name(self) -> str:
        return "black"

    def get_chain_type(self) -> ComType:
        return StructColor.get_type()

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        return CtxExprPyStruct(struct, {"color_code": "black"})


class ChainColorDarkBlue(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkColor

    def get_name(self) -> str:
        return "dark_blue"

    def get_chain_type(self) -> ComType:
        return StructColor.get_type()

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        return CtxExprPyStruct(struct, {"color_code": "dark_blue"})


class ChainColorDarkGreen(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkColor

    def get_name(self) -> str:
        return "dark_green"

    def get_chain_type(self) -> ComType:
        return StructColor.get_type()

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        return CtxExprPyStruct(struct, {"color_code": "dark_green"})


class ChainColorDarkAqua(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkColor

    def get_name(self) -> str:
        return "dark_aqua"

    def get_chain_type(self) -> ComType:
        return StructColor.get_type()

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        return CtxExprPyStruct(struct, {"color_code": "dark_aqua"})


class ChainColorDarkRed(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkColor

    def get_name(self) -> str:
        return "dark_red"

    def get_chain_type(self) -> ComType:
        return StructColor.get_type()

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        return CtxExprPyStruct(struct, {"color_code": "dark_red"})


class ChainColorDarkPurple(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkColor

    def get_name(self) -> str:
        return "dark_purple"

    def get_chain_type(self) -> ComType:
        return StructColor.get_type()

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        return CtxExprPyStruct(struct, {"color_code": "dark_purple"})


class ChainColorGold(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkColor

    def get_name(self) -> str:
        return "gold"

    def get_chain_type(self) -> ComType:
        return StructColor.get_type()

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        return CtxExprPyStruct(struct, {"color_code": "gold"})


class ChainColorGray(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkColor

    def get_name(self) -> str:
        return "gray"

    def get_chain_type(self) -> ComType:
        return StructColor.get_type()

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        return CtxExprPyStruct(struct, {"color_code": "gray"})


class ChainColorDarkGray(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkColor

    def get_name(self) -> str:
        return "dark_gray"

    def get_chain_type(self) -> ComType:
        return StructColor.get_type()

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        return CtxExprPyStruct(struct, {"color_code": "dark_gray"})


class ChainColorBlue(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkColor

    def get_name(self) -> str:
        return "blue"

    def get_chain_type(self) -> ComType:
        return StructColor.get_type()

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        return CtxExprPyStruct(struct, {"color_code": "blue"})


class ChainColorGreen(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkColor

    def get_name(self) -> str:
        return "green"

    def get_chain_type(self) -> ComType:
        return StructColor.get_type()

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        return CtxExprPyStruct(struct, {"color_code": "green"})


class ChainColorAqua(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkColor

    def get_name(self) -> str:
        return "aqua"

    def get_chain_type(self) -> ComType:
        return StructColor.get_type()

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        return CtxExprPyStruct(struct, {"color_code": "aqua"})


class ChainColorRed(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkColor

    def get_name(self) -> str:
        return "red"

    def get_chain_type(self) -> ComType:
        return StructColor.get_type()

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        return CtxExprPyStruct(struct, {"color_code": "red"})


class ChainColorLightPurple(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkColor

    def get_name(self) -> str:
        return "light_purple"

    def get_chain_type(self) -> ComType:
        return StructColor.get_type()

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        return CtxExprPyStruct(struct, {"color_code": "light_purple"})


class ChainColorYellow(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkColor

    def get_name(self) -> str:
        return "yellow"

    def get_chain_type(self) -> ComType:
        return StructColor.get_type()

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        return CtxExprPyStruct(struct, {"color_code": "yellow"})


class ChainColorWhite(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkColor

    def get_name(self) -> str:
        return "white"

    def get_chain_type(self) -> ComType:
        return StructColor.get_type()

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        return CtxExprPyStruct(struct, {"color_code": "white"})


class ChainColorHex(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkColor

    def get_name(self) -> str:
        return "hex"

    def get_chain_type(self) -> ComType:
        return StructColor.get_type()

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [IParam("color_code", InertType(InertCoreTypes.STR, True))]

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        this_link = chain_links[-1]
        return CtxExprPyStruct(struct, {"color_code": this_link.get_arg_for_param_described("color_code", CtxExprLitStr).value})


class ChainColorLime(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkColor

    def get_name(self) -> str:
        return "lime"

    def get_chain_type(self) -> ComType:
        return StructColor.get_type()

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        return CtxExprPyStruct(struct, {"color_code": "#aaff00"})


class ChainColorCyan(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkColor

    def get_name(self) -> str:
        return "cyan"

    def get_chain_type(self) -> ComType:
        return StructColor.get_type()

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: 'CtxPyStruct') -> 'CtxExprPyStruct':
        return CtxExprPyStruct(struct, {"color_code": "#20B2AA"})
