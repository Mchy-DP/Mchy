

from typing import List
from mchy.cmd_modules.docs_data import DocsData
from mchy.cmd_modules.name_spaces import Namespace
from mchy.cmd_modules.param import IParam


def _validate_params(params: List[IParam], docs: DocsData, func_name: str, what_is_this: str):
    valid_param_labels = {param.label for param in params}
    for doc_param_name in docs.param_info.keys():
        assert doc_param_name in valid_param_labels, (
            f"The documented parameter `{doc_param_name}` is not among the parameters of {what_is_this} `{func_name}`, valid params are [{', '.join(valid_param_labels)}]"
        )


def test_docs_param_match():
    for ns_name, ns in Namespace.namespaces.items():
        for func in ns.ifuncs:
            _validate_params(func.get_params(), func.get_docs(), func.get_name(), "function")

        for prop in ns.iprops:
            assert len(prop.get_docs().param_info.keys()) == 0, f"Property `{prop.get_name()}` has documented parameters despite being a property"

        for chain_link in ns.ichain_links:
            chain_params = chain_link.get_params()
            if chain_params is None:
                assert len(chain_link.get_docs().param_info.keys()) == 0, f"Chain-property `{prop.get_name()}` has documented parameters despite being a chain property"
            else:
                _validate_params(chain_link.get_params(), chain_link.get_docs(), chain_link.get_name(), "chain-function")
