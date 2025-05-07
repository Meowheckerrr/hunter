import subprocess
import os
import signal
import threading
import sys
import platform
import shutil
from typing import List, Optional
from .logging_config import logger

# Track running subprocesses for cleanup
running_sub_processes: List[subprocess.Popen] = []

def locate_executable(executable_name: str, provided_path: Optional[str] = None) -> str:
    """
    Locate an executable using the provided path or system PATH search.

    Args:
        executable_name: Name of the executable (e.g., 'BurpSuitePro', 'nmap').
        provided_path: Path provided by the user (if any).

    Returns:
        Path to the executable.

    Raises:
        FileNotFoundError: If no valid path is found.
    """
    # Check provided path
    if provided_path and os.path.exists(provided_path):
        logger.debug(f"Using provided path for {executable_name}: {provided_path}")
        return provided_path

    # Search in system PATH using shutil.which
    exec_path = shutil.which(executable_name)
    if exec_path:
        logger.debug(f"Found {executable_name} in PATH: {exec_path}")
        return exec_path

    raise FileNotFoundError(
        f"{executable_name} executable not found in PATH or at provided path. "
        "Please ensure it’s installed or specify a valid path with --burp-path."
    )

def run_cmd(cmd: str, shell: bool = True) -> bool:
    """
    Execute a command and log its status.

    Args:
        cmd: Command to execute.
        shell: Whether to run the command in a shell.

    Returns:
        True if the command succeeds, False otherwise.
    """
    logger.info(f"[+] Executing: {cmd}")
    try:
        subprocess.run(cmd, shell=shell, check=True)
        return True
    except subprocess.SubprocessError as e:
        logger.error(f"[!] Command failed: {cmd}, error: {e}")
        return False

def run_subprocess(cmd: str, log_file: Optional[str] = None) -> bool:
    """
    Execute a subprocess, optionally logging output to a file.

    Args:
        cmd: Command to execute.
        log_file: Optional file to log stdout/stderr.

    Returns:
        True if successful, False otherwise.
    """
    logger.info(f"🌀 [Starting]: {cmd}")
    process = None
    try:
        # Use context manager for file to ensure closure
        with (open(log_file, "a") if log_file else subprocess.DEVNULL) as stdout:
            stderr = stdout if log_file else subprocess.DEVNULL

            # Use setsid only on Unix-like systems
            preexec_fn = os.setsid if platform.system() != "Windows" else None

            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=stdout,
                stderr=stderr,
                preexec_fn=preexec_fn
            )
            running_sub_processes.append(process)
            process.wait()

            if process.returncode != 0:
                logger.error(f"❗ [Failed] {cmd}, exit code = {process.returncode}")
                return False
            logger.info(f"✅ [Completed] {cmd}")
            return True

    except Exception as e:
        logger.error(f"💥 [Error] {cmd} failed: {e}")
        if process:
            try:
                # Terminate process group (Unix) or process (Windows)
                if platform.system() != "Windows":
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()
                logger.info(f"🛑 [{cmd}] Terminated")
            except Exception as kill_error:
                logger.error(f"❗ Failed to terminate process: {kill_error}")
        return False
    finally:
        # Clean up completed process from list
        if process and process in running_sub_processes:
            running_sub_processes.remove(process)

def run_tool_as_thread(cmd: str, next_cmd: Optional[str] = None, log_file: Optional[str] = None) -> threading.Thread:
    """
    Run a command in a separate thread, optionally chaining a follow-up command.

    Args:
        cmd: Command to execute.
        next_cmd: Optional follow-up command.
        log_file: Optional file to log stdout/stderr.

    Returns:
        The thread object.
    """
    def target():
        success = run_subprocess(cmd, log_file)
        if success and next_cmd:
            logger.info(f"➡️ [Chaining] {next_cmd}")
            run_subprocess(next_cmd, log_file)

    thread = threading.Thread(target=target)
    thread.start()
    return thread

def kill_all_sub_process() -> None:
    """
    Terminate all running subprocesses and exit the program.
    """
    logger.info("💥 Detected Ctrl+C, cleaning up subprocesses...")
    for process in running_sub_processes[:]:  # Copy to avoid modifying during iteration
        try:
            if platform.system() != "Windows":
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                process.terminate()
            logger.info(f"🛑 Terminated PID {process.pid}")
        except Exception as e:
            logger.error(f"❗ Failed to terminate PID {process.pid}: {e}")
        finally:
            running_sub_processes.remove(process)
    sys.exit(0)