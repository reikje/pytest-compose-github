import logging

from dataclasses import dataclass
from typing import List, Optional

from paramiko import SSHClient
import paramiko


logger = logging.getLogger()
logger.setLevel(logging.INFO)



def list_folder_password(host_name: str, user_name: str, password: str, port: int = 22, remote_folder: Optional[str] = None) -> List[str]:
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        logger.info(f"About to connect to SFTP at {host_name}:{port} using username {user_name} and password {password[:3]}***.")
        ssh.connect(host_name, username=user_name, password=password, port=port)
        return _list_folder(ssh_client=ssh, remote_folder=remote_folder)
    

def _list_folder(ssh_client: SSHClient, remote_folder: Optional[str] = None) -> List[str]:
    sftp_files = []
    with ssh_client.open_sftp() as sftp:
        path = remote_folder or "."
        remote_files = sftp.listdir_attr(path=path)
        remote_files = [remote_file for remote_file in remote_files if not remote_file.filename.startswith(".")]

        for remote_file in remote_files:
            if remote_file.longname and remote_file.longname.startswith("d"):
                logger.info(f"Entering directory {path}/{remote_file.filename} ...")
                sftp_files = sftp_files + _list_folder(ssh_client=ssh_client, remote_folder=f"{path}/{remote_file.filename}")
            else:
                sftp_files.append(remote_file.filename)

    return sftp_files
