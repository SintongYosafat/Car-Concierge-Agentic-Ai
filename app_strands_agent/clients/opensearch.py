from opensearchpy import OpenSearch
from app_strands_agent.core import settings


def create_opensearch_client() -> OpenSearch:
    """
    Create and configure an OpenSearch client.
    """
    host = settings.OS_HOST
    port = settings.OS_PORT
    user = settings.OS_USER
    password = settings.OS_PASS
    timeout = settings.OS_TIMEOUT
    max_retries = settings.OS_RETRY

    return OpenSearch(
        hosts=[{"host": host, "port": int(port)}],
        http_auth=(user, password),
        use_ssl=True,
        verify_certs=True,
        timeout=int(timeout),
        max_retries=int(max_retries),
        retry_on_timeout=True,
    )