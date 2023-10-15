import logging
import time
import timeit
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

class WaitTimeoutException(Exception):
    def __init__(self, container_logs, message="Timeout reached while waiting on service!"):
        self.container_logs = container_logs
        super().__init__(message)

def custom_wait(self, check, timeout, pause, clock=timeit.default_timer):
    """Wait until a service is responsive."""

    ref = clock()
    now = ref
    while (now - ref) < timeout:
        if check():
            return
        time.sleep(pause)
        now = clock()

    # get container logs to provide info about failure
    output = self._docker_compose.execute("logs").decode("utf-8")

    raise WaitTimeoutException(container_logs=output)


@pytest.fixture(scope="session")
def monkeysession(request):
    mp = pytest.MonkeyPatch()
    request.addfinalizer(mp.undo)
    return mp


@pytest.fixture(scope="session")
def composed_environment(monkeysession, docker_ip, docker_services) -> ComposedEnvironment:
    from pytest_docker.plugin import Services
    monkeysession.setattr(Services, "wait_until_responsive", custom_wait)
    sftp_port = docker_services.port_for("sftp", 22)
    localstack_port = docker_services.port_for("localstack", 4566)
    try:
        docker_services.wait_until_responsive(
            timeout=10.0, pause=0.5, check=lambda: _is_responsive(host=docker_ip, sftp_port=7967, localstack_port=localstack_port)
        )
    except WaitTimeoutException as ex:
        logging.error(ex.container_logs)
        raise ex

    return ComposedEnvironment(host_name=docker_ip, sftp_port=sftp_port)