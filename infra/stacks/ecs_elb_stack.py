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

        # Create the VPC
        vpc = ec2.Vpc(self, f"{id}-VPC", max_azs=2)

        # Create the ECS Cluster
        cluster = ecs.Cluster(self, f"{id}-Cluster", vpc=vpc)

        # Setup with subdomain
        api_domain_name = f"{conf.api_subdomain}.{conf.domain_name}"

        # Lookup the Route 53 hosted zone for the domain
        hosted_zone = route53.HostedZone.from_lookup(
            self,
            f"{id}-hosted-zone",
            domain_name=conf.domain_name,
            private_zone=False,
        )

        # Create a DNS validated SSL certificate for the loadbalancer
        certificate = acm.DnsValidatedCertificate(
            self,
            f"{id}-certificate",
            domain_name=api_domain_name,
            hosted_zone=hosted_zone,
        )

        # Create the load balancer
        alb = elbv2.ApplicationLoadBalancer(
            scope=self,
            id=f"{id}-alb",
            vpc=vpc,
            internet_facing=True,
        )

        # Listen on HTTPS
        listener = alb.add_listener(
            id=f"{id}-https-listener",
            port=443,
            open=False,
            default_action=elbv2.ListenerAction.fixed_response(200),
            certificates=[certificate],
        )

        # Redirect HTTP to HTTPS
        alb.add_redirect()

        # Add a security group to provide a secure connection between the ALB and the containers
        alb_sg = ec2.SecurityGroup(
            scope=self,
            id=f"{id}-alb-sg",
            vpc=vpc,
            allow_all_outbound=True,
        )
        alb_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), description="Allow incoming https traffic")
        alb.add_security_group(alb_sg)

        # Create a Fargate task definition
        task_def = ecs.FargateTaskDefinition(
            scope=self,
            id=f"{id}-task",
            family="geocoder-task",
            cpu=conf.fargate_cpu_units,
            memory_limit_mib=conf.fargate_memory_limit_mb,
        )

        # Grab the Mapbox API key from secrets manager to inject into the container's environment.
        mapbox_secret = ssm.Secret.from_secret_name_v2(
            self,
            f"{id}-api-secret",
            "mapbox_api_key",
        )

        # Add the container to the task definition
        container = task_def.add_container(
            f"{id}-container",
            image=ecs.RepositoryImage.from_asset(".."),
            secrets={"MAPBOX_ACCESS_TOKEN": ecs.Secret.from_secrets_manager(mapbox_secret)},
            logging=ecs.LogDriver.aws_logs(stream_prefix=f"{id}-ecs-logs"),
        )

        # Map the port from the container
        container.add_port_mappings(ecs.PortMapping(container_port=conf.port))

        # SG to allow connections from the application load balancer to the fargate containers
        ecs_sg = ec2.SecurityGroup(scope=self, id=f"{id}-ecs-sg", vpc=vpc, allow_all_outbound=True)
        ecs_sg.connections.allow_from(alb_sg, ec2.Port.all_tcp(), description="Application load balancer")

        # Create the Fargate service
        service = ecs.FargateService(
            scope=self,
            id=f"{id}-service",
            task_definition=task_def,
            platform_version=ecs.FargatePlatformVersion.LATEST,
            cluster=cluster,
            security_groups=[ecs_sg],
            assign_public_ip=True,
        )

        # set up alias for subdomain routing
        record_target = route53.RecordTarget.from_alias(route53_targets.LoadBalancerTarget(alb))

        route53.ARecord(
            scope=self,
            id=f"{id}-alias",
            target=record_target,
            zone=hosted_zone,
            record_name=api_domain_name,
        )

        # Add a listener for the service
        target_group = listener.add_targets(
            id=f"{id}-tg",
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[service],
            host_header=api_domain_name,
            priority=1,
        )

        # Configure the health check
        target_group.configure_health_check(path="/health", port=f"{conf.port}", healthy_http_codes="200,302")
