from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_secretsmanager as ssm
from aws_cdk import core

from stacks.config import conf


class ECSStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the VPC
        vpc = ec2.Vpc(self, f"{id}-VPC", max_azs=2)

        # Create the ECS Cluster
        cluster = ecs.Cluster(self, f"{id}-Cluster", vpc=vpc)

        # Lookup the Route 53 hosted zone for the domain
        hosted_zone = route53.HostedZone.from_lookup(
            self,
            f"{id}-HostedZone",
            domain_name=conf.domain_name,
            private_zone=False,
        )

        # Create a DNS validated SSL certificate for the loadbalancer
        certificate = acm.DnsValidatedCertificate(
            self,
            f"{id}-Certificate",
            domain_name=f"{conf.api_subdomain}.{conf.domain_name}",
            hosted_zone=hosted_zone,
        )

        # Grab the Mapbox API key from secrets manager to inject into the container's environment.
        mapbox_secret = ssm.Secret.from_secret_name_v2(
            self,
            f"{id}-api-secret",
            "mapbox_api_key",
        )

        # Use the ApplicationLoadBalancedFargateService construct to pull the local Dockerfile,
        # push the image to ECR, and deploy to Fargate
        app = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            f"{id}-Webservice",
            cluster=cluster,
            domain_name=f"{conf.api_subdomain}.{conf.domain_name}",
            domain_zone=hosted_zone,
            certificate=certificate,
            assign_public_ip=True,
            cpu=conf.fargate_cpu_units,
            memory_limit_mib=conf.fargate_memory_limit_mb,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset(".."),
                container_port=conf.port,
                secrets={"MAPBOX_ACCESS_TOKEN": ecs.Secret.from_secrets_manager(mapbox_secret)},
            ),
        )

        # Add a custom health check to the target group in the ApplicationLoadBalancedFargateService constructs
        app.target_group.configure_health_check(path="/health", port=f"{conf.port}", healthy_http_codes="200,302")
