from typing import Any, Callable

from bh_grpc.generated.beehive.robobee.v1.github_pb2_grpc import (
    GithubServiceStub,
)
from bh_grpc.interceptors.client.outbound_auth import OutboundAuthInterceptor
from flask import Flask
import grpc


class GRPCClient:
    server_address: str = 'localhost:50080'
    outgoing_auth_key: str | None = None

    def __init__(self, app: Flask | None = None):
        self._initialized = False

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        self.server_address = app.config.setdefault(
            'ROBOBEE_GRPC_SERVER_ADDRESS',
            self.server_address,
        )

        self.outgoing_auth_key = app.config.setdefault(
            'ROBOBEE_GRPC_OUTGOING_AUTH_KEY',
            self.outgoing_auth_key,
        )

        # initialize client channel
        channel = grpc.insecure_channel(target=self.server_address)
        channel = grpc.intercept_channel(
            channel,
            OutboundAuthInterceptor(outbound_token=self.outgoing_auth_key),
        )

        # initialize service stubs
        self._github_stub = GithubServiceStub(channel)

        self._initialized = True

    @property
    def github_stub(self) -> GithubServiceStub:
        if not self._initialized:
            raise RuntimeError('GRPCClient not initialized')

        return self._github_stub

    def call_service_catch_error_status(
        self,
        rpc_func: Callable,
        rpc_func_args: tuple[Any],
        valid_status_codes: list[grpc.StatusCode],
    ) -> Any:
        """
        Use this helper function to wrap an RPC call and ignore specific
        response status codes, and instead return None for those cases.
        """
        try:
            return rpc_func(*rpc_func_args)
        except grpc.RpcError as ex:
            if ex.code() not in valid_status_codes:
                raise ex

            return None


grpc_client = GRPCClient()
