import unittest

from bh_grpc.generated.beehive.robobee.v1.github_pb2 import GetPRInfoRequest
from bh_grpc.generated.beehive.robobee.v1.github_pb2_grpc import GithubServiceServicer
import grpc
import pytest

from src.utils.grpc_client import GRPCClient

from src import app as flask_app


class TestGRPCClientExtension(unittest.TestCase):
    def test_extension_uninitialized(self):
        grpc_client = GRPCClient()

        with pytest.raises(RuntimeError):
            assert grpc_client.github_stub

        request = GetPRInfoRequest(
            repo_organization='org', repo_name='repo', pr_id=5
        )

        # github_stup property will raise a RuntimeError because the extension
        # is not initialized
        with pytest.raises(RuntimeError):
            grpc_client.github_stub.GetPRInfo(request)

    def test_extension_initialized(self):
        grpc_client = GRPCClient()

        app = flask_app.create_app('testing')
        grpc_client.init_app(app)

        # should not raise a RuntimeError now that the extension is initialized
        assert grpc_client.github_stub

        request = GetPRInfoRequest(
            repo_organization='org', repo_name='repo', pr_id=5
        )

        # should raise a RpcError this time because there is no server running
        with pytest.raises(grpc.RpcError):
            grpc_client.github_stub.GetPRInfo(request)
