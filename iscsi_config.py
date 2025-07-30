import subprocess
from core import clear_screen, display_menu, get_choice

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
            # Implement Connect to iSCSI Server logic here
        elif choice == 2:
            setup_chap_authentication()
        elif choice == 3:
            print("Listing iSCSI disks...\n")
            # Implement List iSCSI disks logic here
        elif choice == 4:
            print("Mounting iSCSI disk...\n")
            # Implement Mount iSCSI disk logic here
        elif choice == 5:
            print("Formatting iSCSI disk...\n")
            # Implement Format iSCSI disk logic here
        else:
            print("Invalid choice. Try again.\n")

def setup_chap_authentication():
    print("Setting up CHAP Authentication...\n")

    # Get CHAP username and password from the user
    chap_username = input("Enter CHAP username: ").strip()
    chap_password = input("Enter CHAP password: ").strip()

    # Define the path to the iscsid.conf file
    iscsid_conf_path = "/etc/iscsi/iscsid.conf"

    # Prepare the new CHAP configuration lines
    new_chap_lines = [
        "# Added by Hardened Repository Manager script:\n",
        "node.session.auth.authmethod = CHAP\n",
        f"node.session.auth.username = {chap_username}\n",
        f"node.session.auth.password = {chap_password}\n",
        "# End of iSCSI configuration made by the script.\n"
    ]

    # Display the changes to the user
    print("The following changes will be made to iscsid.conf:")
    for line in new_chap_lines:
        print(line.strip())

    # Ask the user to confirm
    confirmation = input("\nDo you want to continue with this configuration? (yes/no): ").strip().lower()

    if confirmation == "yes":
        try:
            # Read the contents of the iscsid.conf file
            with open(iscsid_conf_path, "r") as f:
                lines = f.readlines()

            # Insert the new CHAP configuration lines at the beginning of the file
            lines = new_chap_lines + lines

            # Write the modified contents back to the iscsid.conf file
            with open(iscsid_conf_path, "w") as f:
                f.writelines(lines)

            print("CHAP authentication configured successfully!\n")

            # Display the modified contents of the iscsid.conf file
            print("Modified iscsid.conf contents:\n")
            with open(iscsid_conf_path, "r") as f:
                print(f.read())

        except FileNotFoundError:
            print(f"Error: {iscsid_conf_path} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("CHAP authentication setup cancelled.")