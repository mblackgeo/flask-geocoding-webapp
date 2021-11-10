from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_elasticloadbalancingv2 as elb
from aws_cdk import aws_logs as logs
from aws_cdk import aws_route53 as route53
from aws_cdk import core

from stacks.config import conf


class ECSStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a VPC
        vpc = ec2.Vpc(scope=self, id=f"{id}-vpc", cidr="10.0.8.0/21")

        # Create an Elastic Container Service cluster in the VPC
        ecs_cluster = ecs.Cluster(self, id=f"{id}-ecs", cluster_name="serving-ecs", vpc=vpc, container_insights=True)

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

            # Serve traffic on HTTPS
            protocol = elb.ApplicationProtocol.HTTPS

        else:
            protocol = elb.ApplicationProtocol.HTTP
            domain_cert = None
            domain_name = None
            domain_zone = None

        # Create the load balanced service to serve the container
        self.service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            id=f"{id}-fargate-service",
            assign_public_ip=True,
            cluster=ecs_cluster,
            desired_count=1,
            task_definition=task_definition,
            open_listener=True,
            listener_port=conf.port,
            target_protocol=protocol,
            domain_name=domain_name,
            domain_zone=domain_zone,
            certificate=domain_cert,
            enable_ecs_managed_tags=True,
        )
