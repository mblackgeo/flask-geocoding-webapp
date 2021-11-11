from aws_cdk import core

from stacks.config import conf
from stacks.ecs_stack import ECSStack

app = core.App()
cdk_environment = core.Environment(region=conf.aws_region, account=conf.aws_account)
container_stack = ECSStack(app, "geocoder-stack", env=cdk_environment)

app.synth()
