from core import clear_screen, display_menu, get_choice
from storage import storage_setup


def storage_menu():
    """Displays the local storage management menu and handles user choices."""
    options = [
        "List Disks",
        "Mount Disk",
        "Format Disk",
        "Setup RAID",
        "Setup LVM"
    ]

    while True:
        clear_screen()
        display_menu(options)
        choice = get_choice(options)

        if choice == 0:
            break
        elif choice == 1:
            storage_setup.list_disks()
        elif choice == 2:
            storage_setup.mount_disk()
        elif choice == 3:
            storage_setup.format_disk()
        elif choice == 4:
            storage_setup.setup_raid()
        elif choice == 5:
            storage_setup.setup_lvm()
        else:
            print("Invalid choice. Try again.\n")