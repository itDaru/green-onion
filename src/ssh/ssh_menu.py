from core import clear_screen, display_menu, get_choice
from ssh import ssh_keygen
from ssh import ssh_setup

def ssh_menu():
    """Displays the SSH management menu and handles user choices."""
    options = [
        "Enable/Disable SSH",
        "Harden SSH",
        "Generate SSH Keypair"
    ]

    while True:
        clear_screen()
        display_menu(options)
        choice = get_choice(options)

        if choice == 0:
            break
        elif choice == 1:
            ssh_setup.toggle_ssh_service()
        elif choice == 2:
            ssh_setup.harden_ssh()
        elif choice == 3:
            ssh_keygen.generate_ssh_keypair()
        else:
            print("Invalid choice. Try again.\n")