import base64
import json
import logging
import os

logger = logging.getLogger(__name__)


def _bool_env(name, default="False"):
    return os.getenv(name, default).strip().lower() == "true"


def _apply_secrets(values):
    if not isinstance(values, dict):
        raise ValueError("Secrets payload must be a JSON object")
    for key, value in values.items():
        if key not in os.environ or os.environ.get(key) == "":
            os.environ[str(key)] = "" if value is None else str(value)


def load_aws_secrets_manager():
    secret_id = os.getenv("AWS_SECRETS_MANAGER_SECRET_ID")
    if not secret_id:
        return

    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
    required = _bool_env("AWS_SECRETS_MANAGER_REQUIRED", "False")

    if not region:
        message = "AWS_SECRETS_MANAGER_SECRET_ID is set but no AWS_REGION/AWS_DEFAULT_REGION provided."
        if required:
            raise RuntimeError(message)
        logger.warning(message)
        return

    try:
        import boto3
    except Exception as exc:
        if required:
            raise RuntimeError("boto3 is required for AWS Secrets Manager.") from exc
        logger.warning("boto3 not available for AWS Secrets Manager: %s", exc)
        return

    try:
        client = boto3.client("secretsmanager", region_name=region)
        response = client.get_secret_value(SecretId=secret_id)
        secret_string = response.get("SecretString")
        if not secret_string:
            secret_binary = response.get("SecretBinary")
            if secret_binary:
                secret_string = base64.b64decode(secret_binary).decode("utf-8")

        if not secret_string:
            raise ValueError("Secrets Manager returned an empty secret.")

        try:
            data = json.loads(secret_string)
        except json.JSONDecodeError:
            data = {}
            for line in secret_string.splitlines():
                if "=" in line:
                    key, value = line.split("=", 1)
                    data[key.strip()] = value.strip()

        _apply_secrets(data)
    except Exception as exc:
        if required:
            raise
        logger.warning("Failed to load AWS Secrets Manager secret: %s", exc)
