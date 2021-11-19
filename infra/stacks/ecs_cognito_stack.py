import urllib

from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_elasticloadbalancingv2 as elb
from aws_cdk import aws_elasticloadbalancingv2_actions as elb_actions
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_secretsmanager as ssm
from aws_cdk import core

from stacks.config import conf


class ECSCognitoStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # ---------------------------------------------------------------------
        # VPC / ECS setup
        # ---------------------------------------------------------------------
        # Create the VPC
        vpc = ec2.Vpc(self, f"{id}-vpc", max_azs=2, nat_gateways=0)

        # Create the ECS Cluster
        cluster = ecs.Cluster(self, f"{id}-cluster", vpc=vpc)

        # Optionally setup with (sub)domain
        api_domain_name = f"{conf.api_subdomain}.{conf.domain_name}"

        # ---------------------------------------------------------------------
        # Cognito setup
        # ---------------------------------------------------------------------

        # Create a user pool and get Cognito to send a verification email to the
        # user to confirm their account
        self.user_pool = cognito.UserPool(
            self,
            f"{id}-user-pool",
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(username=True, email=True),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(mutable=True, required=True),
            ),
            user_verification=cognito.UserVerificationConfig(
                email_subject=f"Verify your account for - {api_domain_name}",
                email_style=cognito.VerificationEmailStyle.LINK,
            ),
        )

        # Add a custom domain for the hosted UI
        self.user_pool_custom_domain = self.user_pool.add_domain(
            f"{id}-user-pool-domain",
            cognito_domain=cognito.CognitoDomainOptions(domain_prefix=conf.cognito_subdomain),
        )

        # Create an app client that the ALB can use for authentication
        self.user_pool_client = self.user_pool.add_client(
            f"{id}-alb-app-client",
            user_pool_client_name="AlbAuthentication",
            generate_secret=True,
            o_auth=cognito.OAuthSettings(
                callback_urls=[
                    # This is the endpoint where the ALB accepts the
                    # response from Cognito
                    f"https://{api_domain_name}/oauth2/idpresponse",
                    # This is here to allow a redirect to the login page
                    # after the logout has been completed
                    f"https://{api_domain_name}",
                ],
                flows=cognito.OAuthFlows(authorization_code_grant=True),
                scopes=[cognito.OAuthScope.OPENID],
            ),
            supported_identity_providers=[cognito.UserPoolClientIdentityProvider.COGNITO],
        )

        # Logout URLs and redirect URIs can't be set in CDK constructs natively ...yet
        user_pool_client_cf = self.user_pool_client.node.default_child
        user_pool_client_cf.logout_ur_ls = [
            # This is here to allow a redirect to the login page
            # after the logout has been completed
            f"https://{api_domain_name}"
        ]

        self.user_pool_full_domain = self.user_pool_custom_domain.base_url()
        redirect_uri = urllib.parse.quote(f"https://{api_domain_name}")
        self.user_pool_logout_url = (
            f"{self.user_pool_full_domain}/logout?"
            + f"client_id={self.user_pool_client.user_pool_client_id}&"
            + f"logout_uri={redirect_uri}"
        )

        self.user_pool_user_info_url = f"{self.user_pool_full_domain}/oauth2/userInfo"

        # ---------------------------------------------------------------------
        # Route 53 setup
        # ---------------------------------------------------------------------
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

        # ---------------------------------------------------------------------
        # Fargate setup
        # ---------------------------------------------------------------------
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
            f"{id}-webservice",
            cluster=cluster,
            domain_name=api_domain_name,
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
                environment={
                    "LOGOUT_URL": self.user_pool_logout_url,
                    "USER_INFO_URL": self.user_pool_user_info_url,
                },
            ),
        )

        # Add a custom health check to the target group in the ApplicationLoadBalancedFargateService constructs
        app.target_group.configure_health_check(path="/health", port=f"{conf.port}", healthy_http_codes="200,302")

        # ---------------------------------------------------------------------
        # Link Load balancer and Cognito
        # ---------------------------------------------------------------------
        # Add an additional HTTPS egress rule to the Load Balancers
        # security group to talk to Cognito, by default the construct
        # doesn't allow the ALB to make an outbound request
        lb_security_group = app.load_balancer.connections.security_groups[0]

        lb_security_group.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port(protocol=ec2.Protocol.TCP, string_representation="443", from_port=443, to_port=443),
            description="Outbound HTTPS traffic to get to Cognito",
        )

        # Allow 10 seconds for in flight requests before termination,
        # the default of 5 minutes is much too high.
        app.target_group.set_attribute(key="deregistration_delay.timeout_seconds", value="10")

        # Add the authentication actions as a rule with priority
        app.listener.add_action(
            f"{id}-authenticate-rule",
            priority=1000,
            action=elb_actions.AuthenticateCognitoAction(
                next=elb.ListenerAction.forward(target_groups=[app.target_group]),
                user_pool=self.user_pool,
                user_pool_client=self.user_pool_client,
                user_pool_domain=self.user_pool_custom_domain,
            ),
            host_header=api_domain_name,
        )
