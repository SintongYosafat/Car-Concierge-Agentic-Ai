import aws_cdk as cdk
from stack import AiConciergeStack

app = cdk.App()

AiConciergeStack(
    app,
    "AiConciergeStack",
    env=cdk.Environment(
        account=app.node.try_get_context("account"),
        region=app.node.try_get_context("region") or "us-east-1",
    ),
)

app.synth()
