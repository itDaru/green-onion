from core import clear_screen, display_menu, get_choice
from network import network_setup, network_check

def network_menu():
    options = [
        "Normal Network",
        "Bonded Network (NIC Teaming)"
    ]

    handler = network_check.get_network_manager()

    while True:
        clear_screen()
        display_menu(options, subtitle=f"\nDetected Network Handler: [ {handler} ]")
        choice = get_choice(options)

        if choice == 0:
            break
        elif choice == 1:
            network_setup.setup_network("normal")
        elif choice == 2:
            network_setup.setup_network("bonded")
        else:
            print("Invalid choice. Try again.\n")
