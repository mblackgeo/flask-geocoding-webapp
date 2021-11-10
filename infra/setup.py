import setuptools

with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="geocoder-infra",
    version="0.1.0",
    description="CDK infra for the Geocoder Flask Webapp",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Martin Black",
    package_dir={"": "stacks"},
    packages=setuptools.find_packages(where="infra"),
    install_requires=[
        "aws-cdk.core==1.130.0",
        "aws_cdk.aws_certificatemanager as acm==1.130.0",
        "aws_cdk.aws_ec2 as ec2==1.130.0",
        "aws_cdk.aws_ecs as ecs==1.130.0",
        "aws_cdk.aws_ecs_patterns as ecs_patterns==1.130.0",
        "aws_cdk.aws_elasticloadbalancingv2 as elb==1.130.0",
        "aws_cdk.aws_logs as logs==1.130.0",
        "aws_cdk.aws_route53 as route53==1.130.0",
        "python-dotenv~=0.17",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
