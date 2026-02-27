import ssl, boto3, certifi
from fastapi import Request
from cassandra.cluster import Cluster
from cassandra import ProtocolVersion, ConsistencyLevel
from cassandra.policies import DCAwareRoundRobinPolicy
from cassandra_sigv4.auth import SigV4AuthProvider
from app_strands_agent.core import settings


class KeyspaceClient:
    """
    Amazon Keyspaces (Cassandra) client dengan fix untuk multiple hosts.
    """
    
    def __init__(self):
        self._load_env_vars()
        self._validate_config()
        self._setup_aws_auth()
        self._connect_to_keyspaces()
        self._prepare_statements()
    
    def _load_env_vars(self):
        self.host = settings.get("KS_HOST")
        self.port = int(settings.get("KS_PORT", 9142))
        self.keyspace = settings.get("KS_KEYSPACE")
        self.table = settings.get("KS_CHAT_TABLE")
        self.region = settings.get("AWS_REGION", "us-east-1")
    
    def _validate_config(self):
        missing = []
        if not self.host:
            missing.append("AC_KS_HOST")
        if not self.keyspace:
            missing.append("AC_KS_KEYSPACE")
        if not self.table:
            missing.append("AC_KS_CHAT_TABLE")
        
        if missing:
            raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")
        
        print("\n" + "="*50)
        print("Keyspaces Configuration:")
        print(f"  Host: {self.host}")
        print(f"  Port: {self.port}")
        print(f"  Keyspace: {self.keyspace}")
        print(f"  Table: {self.table}")
        print(f"  Region: {self.region}")
        print("="*50 + "\n")
    
    def _setup_aws_auth(self):
        """Setup AWS SigV4 authentication."""
        try:
            self.boto_session = boto3.Session(region_name=self.region)
            sts = self.boto_session.client('sts')
            identity = sts.get_caller_identity()
            print(f"✓ AWS Authenticated as: {identity['Arn']}")
            
            self.auth_provider = SigV4AuthProvider(self.boto_session)
            
        except Exception as e:
            raise RuntimeError(f"AWS authentication failed: {e}")
    
    def _connect_to_keyspaces(self):
        """Connect to Amazon Keyspaces."""
        
        # SSL Context
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.check_hostname = False  # Penting untuk Keyspaces
        
        # Load balancing policy untuk AWS Keyspaces
        lb_policy = DCAwareRoundRobinPolicy(local_dc='us-east-1')
        
        try:
            print(f"Connecting to AWS Keyspaces at {self.host}:{self.port} ...")
            
            self.cluster = Cluster(
                [self.host],
                port=self.port,
                ssl_context=ssl_context,
                auth_provider=self.auth_provider,
                protocol_version=ProtocolVersion.V4,
                load_balancing_policy=lb_policy,
                connect_timeout=30,
                control_connection_timeout=30
            )
            
            # Connect dan test query
            self.session = self.cluster.connect()
            rows = self.session.execute("SELECT release_version FROM system.local")
            version = rows.one()[0]
            print(f"✓ Connected to Keyspaces (Cassandra {version})")
            
            self.session.set_keyspace(self.keyspace)
            print(f"✓ Using keyspace: {self.keyspace}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Keyspaces: {e}")
    
    def _prepare_statements(self):
        """Prepare statements with LOCAL_QUORUM untuk Keyspaces."""
        try:
            self.insert_stmt = self.session.prepare(f"""
                INSERT INTO {self.table} (
                    user_id,
                    session_id,
                    timestamp,
                    role,
                    message
                )
                VALUES (?, ?, toTimestamp(now()), ?, ?)
            """)
            
            # Required for AWS Keyspaces
            self.insert_stmt.consistency_level = ConsistencyLevel.LOCAL_QUORUM
            print(f"✓ Prepared INSERT statement for {self.table}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to prepare statements: {e}")
    
    def save(self, user_id: str, session_id: str, role: str, message: str):
        """Save a chat message to Keyspaces."""
        try:
            self.session.execute(
                self.insert_stmt,
                (user_id, session_id, role, message),
                timeout=10.0
            )
            print(f"✓ Saved message for user {user_id}")
        except Exception as e:
            print(f"x Failed to save message: {e}")
            raise
    
    def close(self):
        """Close connection gracefully."""
        try:
            if hasattr(self, 'cluster') and self.cluster:
                self.cluster.shutdown()
                print("✓ Keyspaces connection closed")
        except Exception as e:
            print(f"! Error closing connection: {e}")


def create_keyspace_client():
    """Factory function for Keyspaces client."""
    return KeyspaceClient()

def get_keyspaces(request: Request) -> KeyspaceClient:
    """Return Keyspaces client from app.state"""
    return request.app.state.keyspaces