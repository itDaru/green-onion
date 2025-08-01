import os
import subprocess

def get_network_manager():
    """Identifies the networking handler in use on the system.

    Returns 'NetworkManager', 'netplan', 'systemd-networkd', or 'unknown'.
    """
    try:
        result = subprocess.run(["systemctl", "is-active", "NetworkManager"], capture_output=True, text=True)
        if result.returncode == 0:
            return "NetworkManager"

        result = subprocess.run(["which", "netplan"], capture_output=True, text=True)
        if result.returncode == 0:
            return "netplan"

        result = subprocess.run(["systemctl", "is-active", "systemd-networkd"], capture_output=True, text=True)
        if result.returncode == 0:
            return "systemd-networkd"

        if os.path.exists("/etc/network/interfaces"):
            return "ifupdown"

        result = subprocess.run(["systemctl", "is-active", "wickedd"], capture_output=True, text=True)
        if result.returncode == 0:
            return "wicked"

        if os.path.exists("/etc/conf.d/net"):
            return "netifrc"

    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"An error occurred while detecting network manager: {e}")

    return "unknown"

def print_network_manager_status():
    """Prints the detected networking manager."""
    handler = get_network_manager()
    print(f"Detected networking handler: {handler}")

if __name__ == "__main__":
    print_network_manager_status()
