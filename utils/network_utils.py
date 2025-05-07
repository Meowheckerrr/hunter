import socket
import time
from .logging_config import logger

def wait_for_port(host: str, port: int, timeout: float = 999999) -> bool:
    """
    Wait for a port to become available.

    Args:
        host: Hostname or IP address.
        port: Port number.
        timeout: Maximum time to wait in seconds.

    Returns:
        True if the port is open, False if the timeout is reached.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                logger.info(f"✅ Port {port} on {host} is open")
                return True
        except (OSError, ConnectionRefusedError) as e:
            logger.debug(f"Waiting for {host}:{port}: {e}")
            time.sleep(1)
    logger.error(f"❌ Timeout waiting for port {port} on {host}")
    return False