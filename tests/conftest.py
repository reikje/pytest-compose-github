import logging
import os
import socket
import paramiko
import pytest
import boto3
from botocore.client import BaseClient
from botocore.config import Config

from dataclasses import dataclass
from dataclasses_json import dataclass_json

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

@dataclass_json
@dataclass
class ComposedEnvironment:
    host_name: str
    sftp_port: int

@staticmethod
def create_aws_client(service_name: str, endpoint_url: str) -> BaseClient:
    return boto3.client(service_name, aws_access_key_id="neededForAwsSDK", aws_secret_access_key="neededForAwsSDK", config=Config(region_name="us-east-1"), endpoint_url=endpoint_url)

def _is_responsive(host: str, sftp_port: int, localstack_port: int) -> bool:
    try:
        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())        
            ssh.connect(host, username="testuser", password="password", port=sftp_port)

        localstack_url = "http://{}:{}".format(host, localstack_port)
        s3_client = create_aws_client(service_name="s3", endpoint_url=localstack_url)
        s3_client.list_buckets()

        return True
    except Exception as e:
        return False


@pytest.fixture(scope="session")
def composed_environment(docker_ip, docker_services) -> ComposedEnvironment:
    sftp_port = docker_services.port_for("sftp", 22)
    localstack_port = docker_services.port_for("localstack", 4566)
    #host_name = "host.docker.internal"
    docker_services.wait_until_responsive(
        timeout=10.0, pause=0.5, check=lambda: _is_responsive(host=docker_ip, sftp_port=sftp_port, localstack_port=localstack_port)
    )

    return ComposedEnvironment(host_name=docker_ip, sftp_port=sftp_port)