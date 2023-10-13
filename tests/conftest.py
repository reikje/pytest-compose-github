import os
import socket
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
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((host, port))
        return True
    except:
        return False


@pytest.fixture(scope="session")
def composed_environment(docker_services) -> ComposedEnvironment:
    sftp_port = docker_services.port_for("sftp", 22)
    #host_name = "host.docker.internal"
    host_name = "127.0.0.1"
    docker_services.wait_until_responsive(
        timeout=10.0, pause=0.5, check=lambda: _is_responsive(host=host_name, port=sftp_port)
    )
    return ComposedEnvironment(host_name=host_name, sftp_port=sftp_port)