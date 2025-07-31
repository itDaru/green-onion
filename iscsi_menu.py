import subprocess
from core import clear_screen, display_menu, get_choice
from iscsi_auth import setup_chap_authentication
import iscsi_setup

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
            iscsi_setup.configure_iscsi_connection()
        elif choice == 2:
            setup_chap_authentication()
        elif choice == 3:
            iscsi_setup.list_iscsi_disks()
        elif choice == 4:
            iscsi_setup.list_iscsi_disks()
        elif choice == 5:
            iscsi_setup.format_iscsi_disk()
        else:
            print("Invalid choice. Try again.\n")
