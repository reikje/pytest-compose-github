from src.sftp import list_folder_password


def test_connecting(composed_environment):
    sftp_host = composed_environment.host_name
    sftp_port = composed_environment.sftp_port
    sftp_user = "testuser"
    sftp_password = "test"

    files = list_folder_password(host_name="127.0.0.1", user_name="testuser", 
                                 password="test", port=54168)
    assert files == []