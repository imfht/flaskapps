import logging
import os
import shutil
import subprocess
import tarfile
import uuid
from abc import abstractmethod
from io import BytesIO
from pathlib import Path, PurePath
from typing import TYPE_CHECKING, Generic, Iterable, List, Mapping

from bento.error import DockerFailureException
from bento.tool.tool import R, Tool
from bento.util import Memo

DOCKER_INSTALLED = Memo[bool](lambda: shutil.which("docker") is not None)

if TYPE_CHECKING:
    import docker.client
    from docker.models.containers import Container


def get_docker_client() -> "docker.client.DockerClient":
    """Checks that docker client is reachable"""
    # import inside def for performance
    import docker

    try:
        client = docker.from_env()
        client.info()
        return client
    except Exception as e:
        logging.debug(e)
        raise DockerFailureException()


def copy_into_container(
    paths: Mapping[Path, str], container: "Container", destination_path: PurePath
) -> None:
    """Copy local ``paths`` to ``destination_path`` within ``container``.

    The ``container`` is assumed to be running.
    If ``destination_path`` does not exist, it will be created.
    """
    tar_buffer = BytesIO()
    with tarfile.open(mode="w", fileobj=tar_buffer) as archive:
        for p, loc in paths.items():
            archive.add(str(p), arcname=loc)
    tar_buffer.seek(0)
    tar_bytes = tar_buffer.read()

    logging.info(f"sending {len(tar_bytes)} bytes to {container}")
    container.put_archive(str(destination_path), tar_bytes)


class DockerTool(Generic[R], Tool[R]):
    UUID = str(uuid.uuid4())[:8]

    @property
    @abstractmethod
    def docker_image(self) -> str:
        """
        Returns the name of the docker image
        """
        pass

    @property
    @abstractmethod
    def docker_command(self) -> List[str]:
        """
        Returns the command to run in the docker image
        """
        pass

    @property
    def use_remote_docker(self) -> bool:
        """Return whether the Docker daemon is remote.

        We need to know because volume mounting doesn't work with remote daemons.
        """
        return (
            os.getenv("BENTO_REMOTE_DOCKER", "0") == "1"
            or os.getenv("R2C_USE_REMOTE_DOCKER", "0") == "1"
        )

    @property
    def additional_file_targets(self) -> Mapping[Path, str]:
        """
        Additional files, beyond the files to check, that should be copied to the Docker container

        For example, this might include configuration files.

        Format is mapping of local path objects to remote path strings.
        """
        return {}

    @property
    @abstractmethod
    def remote_code_path(self) -> str:
        """
        Where to locate remote code within the docker container
        """
        pass

    @property
    def container_name(self) -> str:
        """
        The name of the docker container

        This is used to separate the docker instances used by each instance of Bento and
        each instance of this class within Bento.
        """
        # UUID separates instances of Bento
        # Tool ID separates instances of the tool
        return f"bento-daemon-{self.UUID}-{self.tool_id()}"

    @property
    def local_volume_mapping(self) -> Mapping[str, Mapping[str, str]]:
        """The volumes to bind when Docker is running locally"""
        return {str(self.base_path): {"bind": self.remote_code_path, "mode": "ro"}}

    def is_allowed_returncode(self, returncode: int) -> bool:
        """Returns true iff the Docker container's return code indicates no error"""
        return returncode == 0

    def assemble_full_command(self, targets: Iterable[str]) -> List[str]:
        """Creates the full command to send to the docker container from file targets"""
        return self.docker_command + list(targets)

    def _prepull_image(self) -> None:
        """
        Pulls the docker image from Docker hub
        """
        client = get_docker_client()

        if not any(i for i in client.images.list() if self.docker_image in i.tags):
            client.images.pull(self.docker_image)
            logging.info(f"Pre-pulled {self.tool_id()} image")

    def _create_container(self, targets: Iterable[str]) -> "Container":
        """
        Creates and returns the Docker container
        """

        client = get_docker_client()

        our_containers = client.containers.list(
            filters={"name": self.container_name, "status": "running"}
        )
        if our_containers:
            logging.info(f"using existing {self.tool_id()} container")
            return our_containers[0]

        vols = {} if self.use_remote_docker else self.local_volume_mapping
        full_command = self.assemble_full_command(targets)

        logging.info(f"starting new {self.tool_id()} container")

        container: "Container" = client.containers.create(
            self.docker_image,
            command=full_command,
            auto_remove=True,
            name=self.container_name,
            volumes=vols,
            detach=True,
            working_dir=self.remote_code_path,
        )
        logging.info(f"started container: {container!r}")

        return container

    def _setup_remote_docker(
        self, container: "Container", expanded: Mapping[Path, str]
    ) -> None:
        """Copies files into the remote Docker container"""
        copy_into_container(expanded, container, PurePath(self.remote_code_path))
        copy_into_container(
            self.additional_file_targets, container, PurePath(self.remote_code_path)
        )

    def run_container(self, files: Iterable[str]) -> subprocess.CompletedProcess:
        """
        Run the Docker command
        """
        targets: Iterable[Path] = [Path(p) for p in files]
        command = self.docker_command
        is_remote = self.use_remote_docker
        expanded = {t: str(t.relative_to(self.base_path)) for t in targets}

        container = self._create_container(expanded.values())

        if is_remote:
            self._setup_remote_docker(container, expanded)

        # Python docker does not allow -a, so use subprocess.run
        result = subprocess.run(
            ["docker", "start", "-a", str(container.id)],
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        logging.info(
            f"{self.tool_id()}: Returned code {result.returncode} with stdout[:4000]:\n"
            f"{result.stdout[:4000]}\nstderr[:4000]\n{result.stderr[:4000]}"
        )

        if not self.is_allowed_returncode(result.returncode):
            raise subprocess.CalledProcessError(
                cmd=command,
                returncode=result.returncode,
                output=result.stdout,
                stderr=result.stderr,
            )

        return result

    def matches_project(self, files: Iterable[Path]) -> bool:
        return DOCKER_INSTALLED.value and self.project_has_file_paths(files)

    def setup(self) -> None:
        self._prepull_image()
