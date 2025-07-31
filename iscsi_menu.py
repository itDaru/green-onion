import subprocess
from core import clear_screen, display_menu, get_choice
from iscsi_auth import setup_chap_authentication

def configure_iscsi():
    iscsi_options = [
        "Connect to iSCSI Server",
        "Setup CHAP Authentication",
        "List iSCSI disks",
        "Mount iSCSI disk",
        "Format iSCSI disk"
    ]
    while True:
        clear_screen()
        display_menu(iscsi_options)
        choice = get_choice(iscsi_options)

        if choice == 0:
            break
        elif choice == 1:
            print("Connecting to iSCSI Server...\n")
        elif choice == 2:
            setup_chap_authentication()
        elif choice == 3:
            print("Listing iSCSI disks...\n")
        elif choice == 4:
            print("Mounting iSCSI disk...\n")
        elif choice == 5:
            print("Formatting iSCSI disk...\n")
        else:
            print("Invalid choice. Try again.\n")
