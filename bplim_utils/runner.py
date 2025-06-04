import os
import inspect
from pathlib import Path
from typing import Union


def run_script(script_path: Union[Path, str]) -> None:
    """
    Compiles and executes a Python script from the given path 
    using the caller's global namespace. This allows variables 
    defined in one script (e.g., config.py) to persist across 
    other executed scripts (step1.py, step2.py).
    It also sets the filename to `script_path` so that stack traces
    show the correct file/line if an error occurs. `__file__` and 
    `__name__` are overridden temporarily to simulate direct script 
    execution.

    Args:
        script_path (Union[Path, str]): Path to the script to run.
    """
    script_path = os.path.abspath(script_path)

    with open(script_path, "r", encoding="utf-8") as f:
        script_content = f.read()

    code_obj = compile(script_content, script_path, "exec")

    # Get the caller's global scope
    caller_globals = inspect.currentframe().f_back.f_globals

    # Save and temporarily override __file__ and __name__
    old_file = caller_globals.get("__file__")
    old_name = caller_globals.get("__name__")

    caller_globals["__file__"] = script_path
    caller_globals["__name__"] = "__main__"

    try:
        exec(code_obj, caller_globals)
    finally:
        # Restore original values
        if old_file is not None:
            caller_globals["__file__"] = old_file
        else:
            caller_globals.pop("__file__", None)

        if old_name is not None:
            caller_globals["__name__"] = old_name
        else:
            caller_globals.pop("__name__", None)
