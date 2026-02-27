from ssl import PROTOCOL_TLSv1_2, SSLContext
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra import ConsistencyLevel
import boto3
from cassandra_sigv4.auth import SigV4AuthProvider
from ..core.config import settings


def get_session():
    """Create and return a Cassandra session based on configuration mode."""
    if settings['CASSANDRA_MODE'] == 'aws':
        ssl_context = SSLContext(PROTOCOL_TLSv1_2)

        # Use AWS credentials from settings
        boto_session = boto3.Session(
            aws_access_key_id=settings['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=settings['AWS_SECRET_ACCESS_KEY'],
            region_name=settings['AWS_REGION']
        )

        auth_provider = SigV4AuthProvider(boto_session)

        profile = ExecutionProfile(
            consistency_level=ConsistencyLevel.LOCAL_QUORUM
        )
        cluster = Cluster(
            [settings['CASSANDRA_HOST']], 
            ssl_context=ssl_context, 
            auth_provider=auth_provider,
            port=int(settings['CASSANDRA_PORT']), 
            execution_profiles={EXEC_PROFILE_DEFAULT: profile}
        )

        return cluster.connect()
    else:
        cluster = Cluster([settings['CASSANDRA_HOST']], port=int(settings['CASSANDRA_PORT']))
        return cluster.connect()
