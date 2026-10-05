"""Safe code execution engine — runs user code in a subprocess with timeout."""

import subprocess
import sys
import tempfile
import os
import textwrap


def execute_code(code: str, timeout: int = 30) -> dict:
    """Execute Python code in an isolated subprocess.

    Returns {"stdout": str, "stderr": str, "returncode": int, "timed_out": bool}
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, dir="/tmp"
    ) as f:
        f.write(code)
        f.flush()
        tmp_path = f.name

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"⏱  Execution timed out after {timeout}s",
            "returncode": 1,
            "timed_out": True,
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": 1,
            "timed_out": False,
        }
    finally:
        os.unlink(tmp_path)
