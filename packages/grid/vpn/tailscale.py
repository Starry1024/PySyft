# stdlib
import os
import sys
from typing import Dict

# third party
from flask import Flask
from flask_executor import Executor
from flask_executor.futures import Future
from secure.base_entrypoint import Shell2HTTP  # type: ignore

# Flask application instance
app = Flask(__name__)

executor = Executor(app)
shell2http = Shell2HTTP(app=app, executor=executor, base_url_prefix="/commands/")

hostname = os.environ.get("HOSTNAME", "node")  # default to node


key = os.environ.get("STACK_API_KEY", None)  # Get key from environment
if key is None:
    print("No STACK_API_KEY found, exiting.")
    sys.exit(1)


def up_callback(context: Dict, future: Future) -> None:
    # optional user-defined callback function
    print(context, future.result())


shell2http.register_command(
    endpoint="up",
    command_name="tailscale up",
    callback_fn=up_callback,
    decorators=[],
)


def status_callback(context: Dict, future: Future) -> None:
    # optional user-defined callback function
    print(context, future.result())


shell2http.register_command(
    endpoint="status",
    command_name="tailscale status",
    callback_fn=status_callback,
    decorators=[],
)
