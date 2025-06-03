import os
from typing import Union
from pathlib import Path


def run_script(script_path: Union[Path, str]) -> None:
    """
    Compiles and executes a Python script from the given path.
    This sets the filename to `script_path` so that stack traces
    show the correct file/line if an error occurs. While the 
    script is running, it temporarily replaces the __file__ 
    and __name__ globals.

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

    # Save previous globals
    old_file = globals().get("__file__")
    old_name = globals().get("__name__")

    # Temporarily override
    globals()["__file__"] = os.path.abspath(script_path)
    globals()["__name__"] = "__main__"

    # Execute code and restore original values 
    try:
        exec(code_obj, globals())
    finally:
        # Restore original values
        if old_file is not None:
            globals()["__file__"] = old_file
        else:
            globals().pop("__file__", None)

        if old_name is not None:
            globals()["__name__"] = old_name
        else:
            globals().pop("__name__", None)
