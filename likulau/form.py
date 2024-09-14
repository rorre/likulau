from typing import Unpack
import liku.elements as e
from liku.signatures import FormHTMLAttributes

from likulau._internal.form_rpc import get_rpc_endpoint
from likulau.types import RPCFunction


class LikuFormHTMLAttributes(FormHTMLAttributes, total=False):
    action: RPCFunction | str


def Form(children: list, **attribs: Unpack[LikuFormHTMLAttributes]):
    action = attribs.get("action")
    if callable(action):
        attribs["action"] = get_rpc_endpoint(action)

    return e.form(props=attribs, children=children)
