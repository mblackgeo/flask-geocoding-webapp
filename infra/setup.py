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
        "aws_cdk.aws_certificatemanager==1.132.0",
        "aws_cdk.aws_cognito==1.132.0",
        "aws_cdk.aws_ec2==1.132.0",
        "aws_cdk.aws_ecs==1.132.0",
        "aws_cdk.aws_ecs_patterns==1.132.0",
        "aws_cdk.aws_elasticloadbalancingv2==1.132.0",
        "aws_cdk.aws_elasticloadbalancingv2_actions==1.132.0",
        "aws_cdk.aws_lambda==1.132.0",
        "aws_cdk.aws_route53==1.132.0",
        "aws_cdk.aws_secretsmanager==1.132.0",
        "aws-cdk.core==1.132.0",
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
