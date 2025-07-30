import core
import network_config
import iscsi_config
import os

def main():
    if os.geteuid() != 0:
        print("WARNING: THIS SCRIPT SHOULD BE RUN AS ROOT.\nExit the script and re-run it as root.")
        input("Press [Enter] to continue as a non-root user under your own risk.")

    options = [
        "Configure Network",
        "Configure iSCSI",
        "Another action",
        "Perform task",
        "Clear Configurations"
    ]

    while True:
        core.clear_screen()
        core.display_menu(options, is_main_menu=True)
        choice = core.get_choice(options)

        if choice == 0:
            print("Exiting...")
            break
        elif choice == 1:
            network_config.configure_network()
        elif choice == 2:
            iscsi_config.configure_iscsi()
        elif choice == 5:
            network_config.clear_configurations()
        else:
            print(f"You selected option {choice}: {options[choice-1]}\n")

if __name__ == "__main__":
    main()