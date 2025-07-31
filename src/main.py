import core
from network import network_menu
from iscsi import iscsi_menu

def main():
    options = [
        "Configure Networking",
        "Configure iSCSI",
        "Configure Local Disks",
        "Setup Users",
        "Setup SSH with Keys"
    ]

    while True:
        core.clear_screen()
        core.display_menu(options, is_main_menu=True)
        choice = core.get_choice(options)

        if choice == 0:
            print("Exiting...")
            break
        elif choice == 1:
            network_menu.network_menu()
        elif choice == 2:
            iscsi_menu.configure_iscsi()
        else:
            print(f"You selected option {choice}: {options[choice-1]}\n")

if __name__ == "__main__":
    main()
