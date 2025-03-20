import os
from typing import Union
from pathlib import Path


def run_script(script_path: Union[Path, str]) -> None:
    """
    Compiles and executes a Python script from the given path.
    This sets the filename to `script_path` so that stack traces
    show the correct file/line if an error occurs, and also
    injects `__script__` into the script's globals so the file
    path is accessible at runtime. That means, inside the script,
    you can do:

    `print("Running script:", __script__)`

    Parameters
    ----------
    script_path : Union[Path, str]
        The path to the Python script to execute.

    Raises
    ------
    Any exceptions raised by the executed script will propagate up.
    """
    with open(script_path, "r") as f:
        script_content = f.read()

    # Compile with the actual file path, so error tracebacks
    # reference that file name, not "<string>".
    code_obj = compile(script_content, script_path, "exec")

    # Create a dictionary of globals for the script execution.
    # We store `__script__` as an absolute path, so the script can
    # reference its own filename if desired (like printing it).
    script_globals = globals()
    script_globals["__script__"] = os.path.abspath(script_path)

    # Execute in these combined globals, allowing the script to
    # access existing definitions (and the new `__script__`).
    exec(code_obj, script_globals)
