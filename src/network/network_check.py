import subprocess

def get_network_manager():
    # sourcery skip: assign-if-exp, merge-else-if-into-elif
    """Identifies the networking handler in use on the system.

    Returns 'NetworkManager', 'netplan', 'systemd-networkd', or 'unknown'.
    """
    try:
        # Check for NetworkManager
        result = subprocess.run(["systemctl", "is-active", "NetworkManager"], capture_output=True, text=True)
        if result.returncode == 0:
            return "NetworkManager"

        # Check for netplan (common on Ubuntu/Debian)
        result = subprocess.run(["which", "netplan"], capture_output=True, text=True)
        if result.returncode == 0:
            return "netplan"

        # Check for systemd-networkd
        result = subprocess.run(["systemctl", "is-active", "systemd-networkd"], capture_output=True, text=True)
        if result.returncode == 0:
            return "systemd-networkd"

        # Check for ifupdown (Debian/Ubuntu older style)
        if os.path.exists("/etc/network/interfaces"):
            return "ifupdown"

        # Check for wicked (SUSE)
        result = subprocess.run(["systemctl", "is-active", "wickedd"], capture_output=True, text=True)
        if result.returncode == 0:
            return "wicked"

        # Check for netifrc (Gentoo)
        # This is a heuristic, as netifrc doesn't have a direct 'is-active' service.
        # We check for the existence of its main configuration directory.
        if os.path.exists("/etc/conf.d/net"):
            return "netifrc"



    except FileNotFoundError:
        # Commands like systemctl or which might not be found in minimal environments
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
