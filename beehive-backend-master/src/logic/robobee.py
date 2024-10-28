from typing import Tuple
from urllib.parse import urlparse
from bh_grpc.generated.beehive.robobee.v1.github_pb2 import GetPRInfoRequest



def get_pr_info(pr_url, github_grpc_client):
    repo_organization, repo_name, pr_number = parse_pr_url(pr_url)

    request = GetPRInfoRequest(
        repo_organization=repo_organization,
        repo_name=repo_name,
        pr_id=pr_number
    )
    response = github_grpc_client.call_service_catch_error_status(
        rpc_func=github_grpc_client.github_stub.GetPRInfo,
        rpc_func_args=(request,),
        valid_status_codes=[],
    )
    return response


def parse_pr_url(pr_url: str) -> Tuple[str, str, int]:
    parsed_url = urlparse(pr_url)
    if 'github.com' not in parsed_url.netloc:
        raise ValueError("The provided URL is not a valid GitHub URL")
    path_parts = parsed_url.path.strip('/').split('/')
    if len(path_parts) < 4 or path_parts[2] != 'pull':
        raise ValueError("The provided URL does not appear to be a GitHub PR URL")
    repo_organization = path_parts[0]
    repo_name = path_parts[1]
    try:
        pr_number = int(path_parts[3])
    except ValueError as e:
        raise ValueError("Unable to convert PR number to integer") from e
    return repo_organization, repo_name, pr_number
