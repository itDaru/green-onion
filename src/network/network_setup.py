from network import network_check
from network import network_setup_netplan, network_setup_networkd, network_setup_networkmanager, network_setup_ifupdown, network_setup_wicked, network_setup_netifrc

def setup_network(network_type):
    """
    Configures the network based on the detected network manager and the selected network type.

    Args:
        network_type (str): "normal" or "bonded".
    """
    handler = network_check.get_network_manager()

    if handler == "NetworkManager":
        if network_type == "normal":
            network_setup_networkmanager.configure_normal_network()
        elif network_type == "bonded":
            network_setup_networkmanager.configure_bonded_network()
    elif handler == "netplan":
        if network_type == "normal":
            network_setup_netplan.configure_normal_network()
        elif network_type == "bonded":
            network_setup_netplan.configure_bonded_network()
    elif handler == "systemd-networkd":
        if network_type == "normal":
            network_setup_networkd.configure_normal_network()
        elif network_type == "bonded":
            network_setup_networkd.configure_bonded_network()
    elif handler == "ifupdown":
        if network_type == "normal":
            network_setup_ifupdown.configure_normal_network()
        elif network_type == "bonded":
            network_setup_ifupdown.configure_bonded_network()
    elif handler == "wicked":
        if network_type == "normal":
            network_setup_wicked.configure_normal_network()
        elif network_type == "bonded":
            network_setup_wicked.configure_bonded_network()
    elif handler == "netifrc":
        if network_type == "normal":
            network_setup_netifrc.configure_normal_network()
        elif network_type == "bonded":
            network_setup_netifrc.configure_bonded_network()
    else:
        print("Unknown or unsupported network manager.")