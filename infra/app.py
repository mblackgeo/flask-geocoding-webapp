from aws_cdk import core

from stacks.config import conf
from stacks.ecs_elb_stack import EcsElbStack

app = core.App()
cdk_environment = core.Environment(region=conf.aws_region, account=conf.aws_account)

# Option 1 - Use ecs_patterns.ApplicationLoadBalancedFargateService
# This will create most things automatically behind the scenes but gives up
# some flexibility in how the load balancer can be used
# from stacks.ecs_stack import ECSStack
# container_stack = ECSStack(app, "geocoder-stack", env=cdk_environment)

# Option 2 - Create the full stack manually including the elastic load balancer
# This allows for multiple fargate services to use the same ELB which can save
# costs if many apps are deployed
# Note: a domain is currently required for using this stack
container_stack = EcsElbStack(app, "geocoder-stack", env=cdk_environment)

app.synth()
