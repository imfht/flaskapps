from typing import Any, Dict, List, Mapping, Optional

from docker.models.containers import ContainerCollection
from docker.models.images import ImageCollection

class DockerClient:
    @classmethod
    def from_env(cls, **kwargs: Any) -> DockerClient:
        """
        Args:
            version (str): The version of the API to use. Set to ``auto`` to
                automatically detect the server's version. Default: ``1.30``
            timeout (int): Default timeout for API calls, in seconds.
            ssl_version (int): A valid `SSL version`_.
            assert_hostname (bool): Verify the hostname of the server.
            environment (dict): The environment to read environment variables
                from. Default: the value of ``os.environ``
            credstore_env (dict): Override environment variables when calling
                the credential store process.
        """
        ...
    @property
    def containers(self) -> ContainerCollection: ...
    @property
    def images(self) -> ImageCollection: ...
    def info(self) -> Dict[str, Any]: ...

from_env = DockerClient.from_env
