from hashlib import md5
from liku import HTMLElement
from starlette.requests import Request
from starlette.responses import HTMLResponse
from likulau._internal.utils import run_async
from likulau.types import RPCFunction
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

RPC_IDENT = "liku-rpc"
RPC_MAPPING: dict[str, RPCFunction] = {}


def get_rpc_ident(func: RPCFunction):
    ident = md5(func.__qualname__.encode()).hexdigest()
    if ident not in RPC_MAPPING:
        RPC_MAPPING[ident] = func

    return ident


def get_rpc_endpoint(func: RPCFunction):
    ident = get_rpc_ident(func)
    return f"?{RPC_IDENT}={ident}"


class FormRPCMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        rpc_ident = request.query_params.get(RPC_IDENT)
        if not rpc_ident:
            return await call_next(request)

        rpc_func = RPC_MAPPING.get(rpc_ident)
        if not rpc_func:
            return await call_next(request)

        async with request.form() as form:
            response = await run_async(rpc_func, form)
            if isinstance(response, HTMLElement):
                response = HTMLResponse(str(response))
            return response
