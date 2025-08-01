from core import clear_screen, display_menu, get_choice
from iscsi import iscsi_setup, iscsi_auth

def configure_iscsi():
    iscsi_options = [
        "Connect to iSCSI Server",
        "Setup CHAP Authentication",
        "List iSCSI Disks",
        "Format iSCSI Disk",
        "Mount iSCSI Disk"
    ]
    while True:
        clear_screen()
        display_menu(iscsi_options)
        choice = get_choice(iscsi_options)

        if choice == 0:
            break
        elif choice == 1:
            iscsi_setup.iscsi_connect()
        elif choice == 2:
            setup_chap_authentication()
        elif choice == 3:
            iscsi_setup.list_iscsi_disks()
        elif choice == 4:
            iscsi_setup.format_iscsi_disk()
        elif choice == 5:
            iscsi_setup.mount_iscsi_disk()
        else:
            print("Invalid choice. Try again.\n")
