from core import clear_screen, display_menu, get_choice
from network import network_setup

def network_menu():
    options = [
        "Normal Network",
        "Bonded Network (NIC Teaming)"
    ]

    while True:
        clear_screen()
        display_menu(options)
        choice = get_choice(options)

        if choice == 0:
            break
        elif choice == 1:
            network_setup.configure_normal_network()
        elif choice == 2:
            network_setup.configure_bonded_network()
        else:
            print("Invalid choice. Try again.\n")