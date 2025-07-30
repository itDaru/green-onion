import subprocess
from core import clear_screen, display_menu, get_choice

def get_available_interfaces():
    try:
        output = subprocess.check_output(["ip", "link", "show"]).decode()
        interfaces = []
        lines = output.splitlines()
        for line in lines:
            if ":" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    interface_name = parts[1].strip()
                    interfaces.append(interface_name)
        return interfaces
    except subprocess.CalledProcessError:
        return []

def configure_network():
    print("Configuring Network...\n")
    
    # List available interfaces
    available_interfaces = get_available_interfaces()
    if available_interfaces:
        print("Available interfaces:")
        selected_interfaces = []
        while True:
            for iface in available_interfaces:
                if iface in selected_interfaces:
                    print(f"{iface} [SELECTED]")
                else:
                    print(iface)
            print()

            interface = input("Enter interface name (e.g., eth0, enp0s3) or type 'done': ").strip()
            if interface.lower() == 'done':
                break
            if interface not in available_interfaces:
                print("Not a valid interface")
                continue
            if interface in selected_interfaces:
                print("Interface already selected.")
                continue
            selected_interfaces.append(interface)

        if not selected_interfaces:
            print("No interfaces selected. Aborting.")
            return

        # 2. Bond or Plain Networking
        if len(selected_interfaces) > 1:
            # Configure Bond
            print("\nConfiguring bond0...\n")
            
            # Create bond interface
            try:
                subprocess.run(["nmcli", "con", "add", "type", "bond", "con-name", "bond0", "ifname", "bond0", "mode", "active-backup"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error creating bond0: {e}")
                return

            # Add interfaces to bond
            for iface in selected_interfaces:
                try:
                    subprocess.run(["nmcli", "con", "add", "type", "ethernet", "con-name", f"bond0-slave-{iface}", "ifname", iface, "master", "bond0"], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error adding {iface} to bond0: {e}")
                    return
            
            # Bring up the bond
            try:
                subprocess.run(["nmcli", "con", "up", "bond0"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error bringing up bond0: {e}")
                return
            
            network_interface = "bond0"  # Use bond0 for further configuration
        else:
            # Configure Plain Networking
            print(f"\nConfiguring {selected_interfaces[0]}...\n")
            network_interface = selected_interfaces[0]

        # 3. Network Configuration (Common for both Bond and Plain)
        
        # Network CIDR
        while True:
            network_cidr = input("Enter Network CIDR (e.g., 10.0.1.10/24): ").strip()
            if "/" in network_cidr:
                break
            else:
                print("Invalid CIDR format. Include the subnet mask (e.g., /24).")

        # Network Gateway
        network_gateway = input("Enter Network Gateway (e.g., 10.0.1.1): ").strip()

        # Network DNS
        network_dns = input("Enter Network DNS (e.g., 10.0.1.1, 10.0.1.254): ").strip()
        dns_servers = network_dns.split(',')

        # Apply Configuration using nmcli
        try:
            con_name = f"static-{network_interface}"
            subprocess.run(["nmcli", "con", "add", "type", "ethernet", "con-name", con_name, "ifname", network_interface, "ip4", network_cidr, "gw4", network_gateway], check=True)
            
            for dns in dns_servers:
                subprocess.run(["nmcli", "con", "mod", con_name, "+ipv4.dns", dns.strip()], check=True)

            subprocess.run(["nmcli", "con", "mod", con_name, "ipv4.method", "manual"], check=True)
            subprocess.run(["nmcli", "con", "up", con_name], check=True)
            
            print("\nNetwork configuration applied successfully!")

        except subprocess.CalledProcessError as e:
            print(f"Error configuring network: {e}")
    else:
        print("No interfaces found.\n")

def get_nmcli_connections():
    try:
        output = subprocess.check_output(["nmcli", "con", "show"]).decode()
        connections = []
        lines = output.splitlines()
        for line in lines[1:]:  # Skip header line
            parts = line.split()
            if len(parts) > 3:
                name = parts[0]
                uuid = parts[1]
                con_type = parts[2]
                device = parts[3]
                connections.append({"name": name, "uuid": uuid, "type": con_type, "device": device})
        return connections
    except subprocess.CalledProcessError:
        return []

def clear_configurations():
    options = [
        "Clear Networking Configuration",
        "Option 2: Do something else",
        "Option 3: Another action",
        "Option 4: Perform task"
    ]

    while True:
        clear_screen()
        display_menu(options)
        choice = get_choice(options)

        if choice == 0:
            break
        elif choice == 1:
            print("Clearing Networking Configuration...\n")
            
            # Get configured network interfaces from nmcli
            connections = get_nmcli_connections()
            
            if not connections:
                print("No network connections found.\n")
                break
            
            # Display configured interfaces
            print("Configured network connections:")
            selected_connections = []
            while True:
                for con in connections:
                    if con in selected_connections:
                        print(f"{con['name']} ({con['device']}) [SELECTED]")
                    else:
                        print(f"{con['name']} ({con['device']})")
                print()
                
                connection_name = input("Enter connection name to clear (or 'done'): ").strip()
                if connection_name.lower() == 'done':
                    break
                
                # Find the connection
                connection_to_clear = None
                for con in connections:
                    if con['name'] == connection_name:
                        connection_to_clear = con
                        break
                
                if not connection_to_clear:
                    print("Not a valid connection name.")
                    continue
                
                if connection_to_clear in selected_connections:
                    print("Connection already selected.")
                    continue
                
                selected_connections.append(connection_to_clear)
            
            if not selected_connections:
                print("No connections selected. Aborting.\n")
                break
            
            # Clear selected interfaces
            for con in selected_connections:
                try:
                    subprocess.run(["nmcli", "con", "delete", con['name']], check=True)
                    print(f"Connection '{con['name']}' deleted successfully.")
                except subprocess.CalledProcessError as e:
                    print(f"Error deleting connection '{con['name']}': {e}")
        else:
            print(f"You selected option {choice}: {options[choice-1]}\n")