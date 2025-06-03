# BPLIM Utils

**BPLIM Utils** is a small Python module that emulates some of Stata’s logging functionality and do-file execution flow for research contexts where reproducibility and ease of logging are important. The module provides:

- **BPLIMLogger**: A single-active logger class that redirects `stdout` and `stderr` to a chosen file, supports pausing/resuming (“off/on”) without closing, and enforces that only one active log can exist at a time.  
- **run_script**: A helper function to compile and run a Python script from a given path, ensuring correct tracebacks and exposing the file path as `__file__` to the executed code.

This repository is aimed at researchers using **BPLIM data** but can be adapted to other contexts.

---

## Features

1. **Stata-like Logging Behavior**  
   - Single active log file: prevents confusion from multiple overlapping logs.  
   - Pause/Resume: temporarily stop redirection (`off()`) or resume (`on()`) without closing the file.  
   - Clear status messages for **opened**, **resumed**, **paused**, and **closed** states.

2. **Script Execution**  
   - `run_script(script_path)` reads, compiles, and executes a Python script.  
   - Tracebacks reflect the original filename, not `"<string>"`.  
   - Allows the script to see `__file__` (the absolute path to the script), if needed.

3. **Lightweight and Flexible**  
   - Minimal dependencies (just standard Python libraries).  
   - Easy to integrate into existing research pipelines.

---

## Installation

### 1. Install via GitHub (Development Mode)

```bash
pip install git+https://github.com/BPLIM/bplim-utils.git
```

Alternatively, you can clone this repository and install locally:

```bash
git clone https://github.com/BPLIM/bplim-utils.git
cd bplim-utils
pip install .
```

---

## Usage

### 1. BPLIMLogger Methods

- `__init__(log_file, append=False)`
    - Prepares a logger with a target file and append mode.
    - Doesn’t redirect output yet.

- `init()`
    - Opens the file and starts redirection.

- `on()`
    - Resumes redirection if it was previously turned off.

- `off()`
    - Pauses redirection (output goes back to the console only).

- `close()`
    - Closes the file completely and frees the logger slot.

### 2. run_script
- `run_script(script_path)`
    - Reads the file at script_path, compiles it with the correct filename, and executes it.
    - The script can reference **\_\_file\_\_** to get its own absolute path.
    - Tracebacks show the original filename if errors occur.

--- 

## Example

### 1. Import the Logger and run_script

```python
from bplim_utils import BPLIMLogger, run_script

def main():
    # Create a logger for "main.log"
    logger = BPLIMLogger("main.log")
    
    # Initialize the logger => open the file & redirect output
    logger.init()
    
    # Print something (goes to console & "main.log")
    print("Hello, BPLIM!")

    # Pause logging
    logger.off()
    print("This goes only to console.")
    
    # Resume logging
    logger.on()
    print("Logging resumed!")
    
    # Close the logger
    logger.close()

    # Run an external Python script using run_script
    run_script("scripts/example_script.py")

if __name__ == "__main__":
    main()
```

--- 

## Contributing

- Fork this repository or create a feature branch from main.
- Add or modify code.
- Create a pull request explaining your changes.

All contributions are welcome - bug reports, suggestions, or pull requests!

---

## License

This project is licensed under the MIT License. It is provided “as is,” without any warranty of any kind - see the LICENSE file for details.

---

## Disclaimer

These utilities are intended for research contexts and are provided freely. Their usage or results do not imply any warranty or liability on behalf of the author. Users are responsible for validating outcomes produced by the code.

---

## Contact

- **Author**: BPLIM
- **Email**: bplim@bportugal.pt
- **GitHub**: [BPLIM](https://github.com/BPLIM)

Feel free to open an issue on this repo if you encounter any problems or have feature requests.
