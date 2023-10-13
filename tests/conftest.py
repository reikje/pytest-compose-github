import os
import socket
import paramiko
import pytest

from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class ComposedEnvironment:
    host_name: str
    sftp_port: int

def _is_responsive(host: str, port: int) -> bool:
    try:
        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())        
            ssh.connect(host, username="testuser", password="password", port=port)
        return True
    except:
        return False


@pytest.fixture(scope="session")
def composed_environment(docker_ip, docker_services) -> ComposedEnvironment:
    sftp_port = docker_services.port_for("sftp", 22)
    #host_name = "host.docker.internal"
    docker_services.wait_until_responsive(
        timeout=10.0, pause=0.5, check=lambda: _is_responsive(host=docker_ip, port=sftp_port)
    )
    return ComposedEnvironment(host_name=docker_ip, sftp_port=sftp_port)