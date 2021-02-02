from bento.tool.runner.docker import DockerTool as Docker  # noqa
from bento.tool.runner.js_tool import JsTool as Node  # noqa
from bento.tool.runner.python_tool import PythonTool as Python  # noqa

"""
Classes that define what runs a tool:

runner.Docker - Runs inside a Docker container
runner.Node - Installs with npm / yarn, runs with node
runner.Python - Installs with venv and pip3, runs with python3
"""
