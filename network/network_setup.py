import subprocess

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

def configure_ethernet():
    print("Configuring Ethernet...\n")
    available_interfaces = get_available_interfaces()
    if not available_interfaces:
        print("No interfaces found.\n")
        return

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

    configure_network(network_interface)

def configure_bond():
    print("Configuring Bond...\n")
    available_interfaces = get_available_interfaces()
    if len(available_interfaces) < 2:
        print("Not enough interfaces available for bonding.\n")
        return

    selected_interfaces = []
    while True:
        print("Available interfaces:")
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

    if len(selected_interfaces) < 2:
        print("Please select at least two interfaces for bonding.\n")
        return

    print("\nConfiguring bond0...\n")
    try:
        subprocess.run(["nmcli", "con", "add", "type", "bond", "con-name", "bond0", "ifname", "bond0", "mode", "active-backup"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error creating bond0: {e}")
        return

    for iface in selected_interfaces:
        try:
            subprocess.run(["nmcli", "con", "add", "type", "ethernet", "con-name", f"bond0-slave-{iface}", "ifname", iface, "master", "bond0"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error adding {iface} to bond0: {e}")
            return

    try:
        subprocess.run(["nmcli", "con", "up", "bond0"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error bringing up bond0: {e}")
        return

    configure_network("bond0")

def configure_network(network_interface):
    while True:
        network_cidr = input("Enter Network CIDR (e.g., 10.0.1.10/24): ").strip()
        if "/" in network_cidr:
            break
        else:
            print("Invalid CIDR format. Include the subnet mask (e.g., /24).")

    network_gateway = input("Enter Network Gateway (e.g., 10.0.1.1): ").strip()

    network_dns = input("Enter Network DNS (e.g., 10.0.1.1, 10.0.1.254): ").strip()
    dns_servers = network_dns.split(',')

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

def configure_normal_network():
    print("Configuring Normal Network...\n")
    available_interfaces = get_available_interfaces()
    if not available_interfaces:
        print("No interfaces found.\n")
        return

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
        network_ip = input("Enter static IP address (e.g., 192.168.1.100): ").strip()
        if network_ip:
            break
        else:
            print("IP address cannot be empty.")

    while True:
        network_cidr = input("Enter Network CIDR (e.g., 24 for 255.255.255.0): ").strip()
        if network_cidr.isdigit() and 0 <= int(network_cidr) <= 32:
            network_cidr = f"/{network_cidr}"
            break
        else:
            print("Invalid CIDR value. It should be a number between 0 and 32.")

    while True:
        network_gateway = input("Enter Network Gateway (e.g., 192.168.1.1): ").strip()
        if network_gateway:
            break
        else:
            print("Gateway cannot be empty.")

    while True:
        network_dns = input("Enter Network DNS (comma-separated, e.g., 8.8.8.8,8.8.4.4): ").strip()
        if network_dns:
            dns_servers = network_dns.split(',')
            break
        else:
            print("DNS servers cannot be empty.")

    con_name = f"static-{network_interface}"
    try:
        subprocess.run(["nmcli", "con", "add", "type", "ethernet", "con-name", con_name, "ifname", network_interface, "ip4", f"{network_ip}{network_cidr}", "gw4", network_gateway], check=True)
        
        for dns in dns_servers:
            subprocess.run(["nmcli", "con", "mod", con_name, "+ipv4.dns", dns.strip()], check=True)

        subprocess.run(["nmcli", "con", "mod", con_name, "ipv4.method", "manual"], check=True)
        subprocess.run(["nmcli", "con", "up", con_name], check=True)
        
        print("\nNormal network configuration applied successfully!")

    except subprocess.CalledProcessError as e:
        print(f"Error configuring normal network: {e}")

def configure_bonded_network():
    print("Configuring Bonded Network (NIC Teaming)...\n")
    available_interfaces = get_available_interfaces()
    if len(available_interfaces) < 2:
        print("Not enough interfaces available for bonding.\n")
        return

    selected_interfaces = []
    while True:
        print("Available interfaces:")
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

    if len(selected_interfaces) < 2:
        print("Please select at least two interfaces for bonding.\n")
        return

    print("\nConfiguring bond0...\n")
    try:
        subprocess.run(["nmcli", "con", "add", "type", "bond", "con-name", "bond0", "ifname", "bond0", "mode", "active-backup"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error creating bond0: {e}")
        return

    for iface in selected_interfaces:
        try:
            subprocess.run(["nmcli", "con", "add", "type", "ethernet", "con-name", f"bond0-slave-{iface}", "ifname", iface, "master", "bond0"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error adding {iface} to bond0: {e}")
            return

    while True:
        network_ip = input("Enter static IP address for bond0 (e.g., 192.168.1.200): ").strip()
        if network_ip:
            break
        else:
            print("IP address cannot be empty.")

    while True:
        network_cidr = input("Enter Network CIDR for bond0 (e.g., 24 for 255.255.255.0): ").strip()
        if network_cidr.isdigit() and 0 <= int(network_cidr) <= 32:
            network_cidr = f"/{network_cidr}"
            break
        else:
            print("Invalid CIDR value. It should be a number between 0 and 32.")

    while True:
        network_gateway = input("Enter Network Gateway for bond0 (e.g., 192.168.1.1): ").strip()
        if network_gateway:
            break
        else:
            print("Gateway cannot be empty.")

    while True:
        network_dns = input("Enter Network DNS for bond0 (comma-separated, e.g., 8.8.8.8,8.8.4.4): ").strip()
        if network_dns:
            dns_servers = network_dns.split(',')
            break
        else:
            print("DNS servers cannot be empty.")

    con_name = "bond0"
    try:
        subprocess.run(["nmcli", "con", "mod", con_name, "ip4", f"{network_ip}{network_cidr}"], check=True)
        subprocess.run(["nmcli", "con", "mod", con_name, "gw4", network_gateway], check=True)
        
        for dns in dns_servers:
            subprocess.run(["nmcli", "con", "mod", con_name, "+ipv4.dns", dns.strip()], check=True)

        subprocess.run(["nmcli", "con", "mod", con_name, "ipv4.method", "manual"], check=True)
        subprocess.run(["nmcli", "con", "up", con_name], check=True)
        
        print("\nBonded network configuration applied successfully!")

    except subprocess.CalledProcessError as e:
        print(f"Error configuring bonded network: {e}")

def get_nmcli_connections():
    try:
        output = subprocess.check_output(["nmcli", "con", "show"]).decode()
        connections = []
        lines = output.splitlines()
        for line in lines[1:]:
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
            
            connections = get_nmcli_connections()
            
            if not connections:
                print("No network connections found.\n")
                break
            
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
            
            for con in selected_connections:
                try:
                    subprocess.run(["nmcli", "con", "delete", con['name']], check=True)
                    print(f"Connection '{con['name']}' deleted successfully.")
                except subprocess.CalledProcessError as e:
                    print(f"Error deleting connection '{con['name']}': {e}")
        else:
            print(f"You selected option {choice}: {options[choice-1]}\n")
