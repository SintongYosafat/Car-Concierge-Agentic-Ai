from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ecr_assets as ecr_assets,
    aws_iam as iam,
    aws_secretsmanager as sm,
    aws_logs as logs,
    CfnOutput,
)
from constructs import Construct


class AiConciergeStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # --- Secret (must exist in Secrets Manager: prd/ai_concierge/be) ---
        secret = sm.Secret.from_secret_name_v2(
            self, "AppSecret", "prd/ai_concierge/be"
        )

        # --- VPC (existing — same VPC as ElastiCache Valkey) ---
        vpc = ec2.Vpc.from_lookup(
            self, "Vpc",
            vpc_id="vpc-0bde35b6fa21f42fe",
        )

        # --- Valkey security group (allow Fargate → Valkey) ---
        valkey_sg = ec2.SecurityGroup.from_security_group_id(
            self, "ValkeySG", "sg-07aff04c2b52b6b13",
        )

        # --- ECS Cluster ---
        cluster = ecs.Cluster(
            self, "Cluster",
            vpc=vpc,
            container_insights_v2=ecs.ContainerInsights.ENABLED,
        )

        # --- Docker image from project root ---
        image = ecs.ContainerImage.from_asset(
            directory="..",
            file="Dockerfile",
            platform=ecr_assets.Platform.LINUX_AMD64,
        )

        # --- Fargate Service + ALB ---
        service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "Service",
            cluster=cluster,
            cpu=1024,
            memory_limit_mib=2048,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=image,
                container_port=8000,
                environment={
                    "AC_ENV": "prd",
                    "AC_LOG_LEVEL": "INFO",
                    "AC_LOG_FORMAT": "json",
                    "AWS_REGION": self.region,
                    "AC_DEFAULT_MODEL": "bedrock_nova_pro",
                    "AC_EMBEDDING_MODEL": "amazon.titan-embed-text-v2:0",
                    "AC_GUARDRAIL_ID": "",
                    # Keyspaces
                    # "AC_KS_HOST": "cassandra.us-east-1.amazonaws.com",
                    "AC_KS_PORT": "9142",
                    "AC_KS_KEYSPACE": "concierge",
                    "AC_KS_CHAT_TABLE": "chat_messages",
                    "AC_KS_ADS_TABLE": "product_ads_clean_v2",
                    # OpenSearch
                    "AC_OS_PORT": "443",
                    "AC_OS_INDEX": "car_ads_hybrid_v2",
                    "AC_OS_TIMEOUT": "60",
                    "AC_OS_RETRY": "2",
                    # S3
                    "AC_AGENT_SESSION": "admo-session-bucket",
                    # Valkey
                    "AC_VALKEY_PORT": "6379",
                    "AC_VALKEY_DEFAULT_TTL": "1800",
                    "AC_VALKEY_CACHE_PREFIX": "agent_semantic_cache:",
                    "AC_SIMILARITY_THRESHOLD": "0.95"
                },
                secrets={
                    "AC_BASIC_AUTH_PASSWORD": ecs.Secret.from_secrets_manager(secret, "AC_BASIC_AUTH_PASSWORD"),
                    "AC_OPENAI_KEY": ecs.Secret.from_secrets_manager(secret, "AC_OPENAI_KEY"),
                    "AC_OS_HOST": ecs.Secret.from_secrets_manager(secret, "AC_OS_HOST"),
                    "AC_OS_USER": ecs.Secret.from_secrets_manager(secret, "AC_OS_USER"),
                    "AC_OS_PASS": ecs.Secret.from_secrets_manager(secret, "AC_OS_PASS"),
                    "AC_VALKEY_HOST": ecs.Secret.from_secrets_manager(secret, "AC_VALKEY_HOST"),
                    "AC_KS_HOST": ecs.Secret.from_secrets_manager(secret, "AC_KS_HOST")
                },
                log_driver=ecs.LogDrivers.aws_logs(
                    stream_prefix="ai-concierge",
                    log_retention=logs.RetentionDays.TWO_WEEKS,
                ),
            ),
            public_load_balancer=True,
            health_check_grace_period=Duration.seconds(120),
        )

        # --- Health check ---
        service.target_group.configure_health_check(
            path="/health",
            healthy_http_codes="200",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(10),
        )

        # --- IAM: Bedrock, S3, Keyspaces ---
        task_role = service.task_definition.task_role

        task_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:ApplyGuardrail",
            ],
            resources=["*"],
        ))

        task_role.add_to_policy(iam.PolicyStatement(
            actions=["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
            resources=[
                "arn:aws:s3:::admo-session-bucket",
                "arn:aws:s3:::admo-session-bucket/*",
            ],
        ))

        task_role.add_to_policy(iam.PolicyStatement(
            actions=["cassandra:Select", "cassandra:Modify"],
            resources=["*"],
        ))

        # --- Outputs ---
        CfnOutput(self, "ServiceUrl",
            value=f"http://{service.load_balancer.load_balancer_dns_name}",
            description="ALB URL",
        )

        # --- Allow Fargate → Valkey on port 6379 ---
        valkey_sg.add_ingress_rule(
            peer=service.service.connections.security_groups[0],
            connection=ec2.Port.tcp(6379),
            description="Fargate to Valkey",
        )

        # --- Auto Scaling (1-3 tasks, based on CPU) ---
        scaling = service.service.auto_scale_task_count(
            min_capacity=1,
            max_capacity=3,
        )
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(120),
            scale_out_cooldown=Duration.seconds(60),
        )
