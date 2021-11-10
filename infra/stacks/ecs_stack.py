from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_logs as logs
from aws_cdk import aws_route53 as route53
from aws_cdk import core

from stacks.config import conf


class ECSStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Register a task definition for this container
        task_definition = ecs.FargateTaskDefinition(
            self,
            id=f"{id}-ecs-task-definition",
            memory_limit_mib=conf.fargate_memory_limit_mb,
            cpu=conf.fargate_cpu_units,
        )

        # Add the container from the parent directory
        app_container = task_definition.add_container(
            id=f"{id}-container",
            image=ecs.ContainerImage.from_asset(".."),
            logging=ecs.AwsLogDriver(stream_prefix=id, log_retention=logs.RetentionDays.ONE_DAY),
        )

        # Map the container ports
        app_container.add_port_mappings(ecs.PortMapping(container_port=conf.port, host_port=conf.port))

        # Setup Route 53 domain and certs if required
        if conf.domain_name:
            root_domain = conf.domain_name
            domain_name = f"{conf.api_subdomain}.{root_domain}"

            # Get the HostedZone of the root domain
            domain_zone = route53.HostedZone.from_lookup(self, "baseZone", domain_name=root_domain)

            # Create a certificate for the api subdomain
            domain_cert = acm.Certificate(
                self,
                "Certificate",
                domain_name=domain_name,
                validation=acm.CertificateValidation.from_dns(domain_zone),
            )

        else:
            domain_cert = None
            domain_zone = None
            domain_name = None

        # Create the load balanced service to serve the container
        service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            id=f"{id}-fargate-service",
            assign_public_ip=True,
            desired_count=1,
            task_definition=task_definition,
            open_listener=True,
            domain_name=domain_name,
            domain_zone=domain_zone,
            certificate=domain_cert,
            enable_ecs_managed_tags=True,
        )

        service.target_group.configure_health_check(path="/health")
