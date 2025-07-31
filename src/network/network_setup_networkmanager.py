
import subprocess

def get_available_interfaces():
    try:
        output = subprocess.check_output(["nmcli", "-t", "-f", "DEVICE,TYPE", "device"]).decode()
        interfaces = []
        for line in output.strip().split('\n'):
            device, dev_type = line.split(':')
            if dev_type == "ethernet":
                interfaces.append(device)
        return interfaces
    except subprocess.CalledProcessError:
        return []

def configure_normal_network():
    print("Configuring Normal Network...\n")
    available_interfaces = get_available_interfaces()
    if not available_interfaces:
        print("No Ethernet interfaces found.\n")
        return

    print("Available interfaces:")
    for i, iface in enumerate(available_interfaces):
        print(f"{i+1}. {iface}")

    while True:
        try:
            choice = int(input("Select interface number: ")) - 1
            if 0 <= choice < len(available_interfaces):
                network_interface = available_interfaces[choice]
                break
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")

    while True:
        config_type = input("Use DHCP or Static IP? (dhcp/static): ").lower()
        if config_type in ["dhcp", "static"]:
            break
        else:
            print("Invalid choice. Please enter 'dhcp' or 'static'.")

    con_name = f"conn-{network_interface}"
    try:
        subprocess.run(["nmcli", "con", "delete", con_name], check=False, capture_output=True)
    except FileNotFoundError:
        pass

    if config_type == "dhcp":
        try:
            subprocess.run(["nmcli", "con", "add", "type", "ethernet", "con-name", con_name, "ifname", network_interface], check=True)
            print(f"\nDHCP configuration for {network_interface} applied successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error configuring DHCP: {e}")
    else:
        while True:
            ip_cidr = input("Enter IP/CIDR (e.g., 192.168.1.1/24): ")
            if "/" in ip_cidr:
                break
            else:
                print("Invalid format. Please use CIDR notation (e.g., 192.168.1.1/24).")
        gateway = input("Enter Gateway (e.g., 192.168.1.254): ")
        dns_servers = input("Enter DNS servers (comma-separated, e.g., 8.8.8.8,8.8.4.4): ")

        try:
            subprocess.run(["nmcli", "con", "add", "type", "ethernet", "con-name", con_name, "ifname", network_interface, "ip4", ip_cidr, "gw4", gateway], check=True)
            if dns_servers:
                subprocess.run(["nmcli", "con", "mod", con_name, "ipv4.dns", dns_servers], check=True)
            subprocess.run(["nmcli", "con", "mod", con_name, "ipv4.method", "manual"], check=True)
            subprocess.run(["nmcli", "con", "up", con_name], check=True)
            print(f"\nStatic IP configuration for {network_interface} applied successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error configuring Static IP: {e}")

def configure_bonded_network():
    print("Configuring Bonded Network...\n")
    available_interfaces = get_available_interfaces()
    if len(available_interfaces) < 2:
        print("At least two Ethernet interfaces are required for bonding.\n")
        return

    print("Available interfaces:")
    for i, iface in enumerate(available_interfaces):
        print(f"{i+1}. {iface}")

    selected_interfaces = []
    while True:
        try:
            choices = input("Select interface numbers (comma-separated, e.g., 1,2): ")
            indices = [int(c.strip()) - 1 for c in choices.split(',')]
            if all(0 <= i < len(available_interfaces) for i in indices):
                selected_interfaces = [available_interfaces[i] for i in indices]
                if len(selected_interfaces) >= 2:
                    break
                else:
                    print("Please select at least two interfaces.")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")

    bond_modes = ["round-robin", "active-backup", "xor", "broadcast", "802.3ad", "tlb", "alb"]
    print("\nAvailable bonding modes:")
    for i, mode in enumerate(bond_modes):
        print(f"{i+1}. {mode}")

    while True:
        try:
            choice = int(input("Select bonding mode number: ")) - 1
            if 0 <= choice < len(bond_modes):
                bond_mode = bond_modes[choice]
                break
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")

    while True:
        config_type = input("\nUse DHCP or Static IP for the bond? (dhcp/static): ").lower()
        if config_type in ["dhcp", "static"]:
            break
        else:
            print("Invalid choice. Please enter 'dhcp' or 'static'.")

    bond_name = "bond0"
    con_name = f"conn-{bond_name}"

    try:
        subprocess.run(["nmcli", "con", "delete", con_name], check=False, capture_output=True)
        for iface in selected_interfaces:
            subprocess.run(["nmcli", "con", "delete", f"conn-{iface}"], check=False, capture_output=True)
    except FileNotFoundError:
        pass

    try:
        subprocess.run(["nmcli", "con", "add", "type", "bond", "con-name", con_name, "ifname", bond_name, "mode", bond_mode], check=True)
        for iface in selected_interfaces:
            subprocess.run(["nmcli", "con", "add", "type", "ethernet", "con-name", f"conn-{iface}", "ifname", iface, "master", bond_name], check=True)

        if config_type == "dhcp":
            subprocess.run(["nmcli", "con", "mod", con_name, "ipv4.method", "auto"], check=True)
        else:
            while True:
                ip_cidr = input("Enter IP/CIDR for bond0 (e.g., 192.168.1.1/24): ")
                if "/" in ip_cidr:
                    break
                else:
                    print("Invalid format. Please use CIDR notation (e.g., 192.168.1.1/24).")
            gateway = input("Enter Gateway for bond0 (e.g., 192.168.1.254): ")
            dns_servers = input("Enter DNS servers for bond0 (comma-separated, e.g., 8.8.8.8,8.8.4.4): ")

            subprocess.run(["nmcli", "con", "mod", con_name, "ipv4.addresses", ip_cidr], check=True)
            subprocess.run(["nmcli", "con", "mod", con_name, "ipv4.gateway", gateway], check=True)
            if dns_servers:
                subprocess.run(["nmcli", "con", "mod", con_name, "ipv4.dns", dns_servers], check=True)
            subprocess.run(["nmcli", "con", "mod", con_name, "ipv4.method", "manual"], check=True)

        subprocess.run(["nmcli", "con", "up", con_name], check=True)
        print(f"\nBonded network '{bond_name}' configured successfully!")

    except subprocess.CalledProcessError as e:
        print(f"Error configuring bonded network: {e}")
