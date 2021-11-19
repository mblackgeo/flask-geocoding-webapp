import os
from types import SimpleNamespace

from dotenv import load_dotenv

# Load variables from .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


conf = SimpleNamespace(
    aws_region=os.environ["AWS_REGION"],
    aws_account=os.environ["AWS_ACCOUNT"],
    domain_name=os.environ.get("DOMAIN_NAME", ""),
    api_subdomain=os.environ.get("API_SUBDOMAIN", ""),
    fargate_cpu_units=int(os.environ.get("FARGATE_CPU_UNITS", 512)),
    fargate_memory_limit_mb=int(os.environ.get("FARGATE_MEMORY_LIMIT_MB", 1024)),
    port=int(os.environ.get("PORT", 5000)),
    cognito_subdomain=os.environ.get("COGNITO_SUBDOMAIN", ""),
)
