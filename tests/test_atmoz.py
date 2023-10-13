from src.sftp import list_folder_password


def test_connecting(composed_environment):
    sftp_host = composed_environment.host_name
    sftp_port = composed_environment.sftp_port
    sftp_user = "testuser"
    sftp_password = "password"

    files = list_folder_password(host_name=sftp_host, user_name=sftp_user, 
                                 password=sftp_password, port=sftp_port)
    assert files == []