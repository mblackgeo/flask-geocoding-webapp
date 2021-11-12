from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as route53_targets
from aws_cdk import aws_secretsmanager as ssm
from aws_cdk import core

from stacks.config import conf


class EcsElbStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # ---------------------------------------------------------------------
        # VPC / ECS / ALB setup
        # ---------------------------------------------------------------------
        vpc = ec2.Vpc(self, f"{id}-vpc", max_azs=2, nat_gateways=0)

        cluster = ecs.Cluster(self, f"{id}-ecs-cluster", vpc=vpc)

        alb = elbv2.ApplicationLoadBalancer(
            scope=self,
            id=f"{id}-alb",
            vpc=vpc,
            internet_facing=True,
        )

        # ---------------------------------------------------------------------
        # Domain name
        # TODO allow this to be optional if there is no domain setup
        # ---------------------------------------------------------------------

        # Lookup the Route 53 hosted zone for the domain
        api_domain_name = f"{conf.api_subdomain}.{conf.domain_name}"
        hosted_zone = route53.HostedZone.from_lookup(
            self,
            f"{id}-hosted-zone",
            domain_name=conf.domain_name,
            private_zone=False,
        )

        # Create a DNS validated SSL certificate for the subdomain
        certificate = acm.DnsValidatedCertificate(
            self,
            f"{id}-certificate",
            domain_name=api_domain_name,
            hosted_zone=hosted_zone,
        )

        # setup A record for routing to the subdomain
        route53.ARecord(
            scope=self,
            id=f"{id}-alias",
            target=route53.RecordTarget.from_alias(route53_targets.LoadBalancerTarget(alb)),
            zone=hosted_zone,
            record_name=api_domain_name,
        )

        # Listen on HTTPS and redirect HTTP to HTTPS
        listener = alb.add_listener(
            id=f"{id}-https-listener",
            port=443,
            open=False,
            default_action=elbv2.ListenerAction.fixed_response(200),
            certificates=[certificate],
        )
        alb.add_redirect()

        # ---------------------------------------------------------------------
        # Security groups
        # ---------------------------------------------------------------------
        # Add a security group to allow HTTPS connections to the ALB
        alb_sg = ec2.SecurityGroup(
            scope=self,
            id=f"{id}-alb-sg",
            vpc=vpc,
            allow_all_outbound=True,
        )
        alb_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), description="Allow incoming https traffic")
        alb.add_security_group(alb_sg)

        # Allow connections from the application load balancer to the fargate containers
        ecs_sg = ec2.SecurityGroup(scope=self, id=f"{id}-ecs-sg", vpc=vpc, allow_all_outbound=True)
        ecs_sg.connections.allow_from(alb_sg, ec2.Port.all_tcp(), description="Application load balancer")

        # ---------------------------------------------------------------------
        # Fargate setup
        # ---------------------------------------------------------------------
        task_def = ecs.FargateTaskDefinition(
            scope=self,
            id=f"{id}-task",
            family="geocoder-task",
            cpu=conf.fargate_cpu_units,
            memory_limit_mib=conf.fargate_memory_limit_mb,
        )

        # Grab the Mapbox API key from secrets manager to inject into the
        # container's environment at run time
        mapbox_secret = ssm.Secret.from_secret_name_v2(
            self,
            f"{id}-api-secret",
            "mapbox_api_key",
        )

        # Add the container to the task definition and expose the correct port
        task_def.add_container(
            f"{id}-container",
            image=ecs.RepositoryImage.from_asset(".."),
            secrets={"MAPBOX_ACCESS_TOKEN": ecs.Secret.from_secrets_manager(mapbox_secret)},
            logging=ecs.LogDriver.aws_logs(stream_prefix=f"{id}-ecs-logs"),
            port_mappings=[ecs.PortMapping(container_port=conf.port)],
        )

        # Create the Fargate service that will run the task
        service = ecs.FargateService(
            scope=self,
            id=f"{id}-service",
            task_definition=task_def,
            platform_version=ecs.FargatePlatformVersion.LATEST,
            cluster=cluster,
            security_groups=[ecs_sg],
            assign_public_ip=True,
        )

        # Add a listener for the service on the load balancer and setup
        # the health check
        listener.add_targets(
            id=f"{id}-tg",
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[service],
            host_header=api_domain_name,
            priority=1,
            health_check=elbv2.HealthCheck(path="/health", port=f"{conf.port}", healthy_http_codes="200,302"),
        )
