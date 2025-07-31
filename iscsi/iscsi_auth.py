def setup_chap_authentication():
    print("Setting up CHAP Authentication...\n")

    chap_username = input("Enter CHAP username: ").strip()
    chap_password = input("Enter CHAP password: ").strip()

    iscsid_conf_path = "/etc/iscsi/iscsid.conf"

    new_chap_lines = [
        "# Added by Hardened Repository Manager script:\n",
        "node.session.auth.authmethod = CHAP\n",
        f"node.session.auth.username = {chap_username}\n",
        f"node.session.auth.password = {chap_password}\n",
        "# End of iSCSI configuration made by the script.\n"
    ]

    print("The following changes will be made to iscsid.conf:")
    for line in new_chap_lines:
        print(line.strip())

    confirmation = input("\nDo you want to continue with this configuration? (yes/no): ").strip().lower()

    if confirmation == "yes":
        try:
            with open(iscsid_conf_path, "r") as f:
                lines = f.readlines()

            lines = new_chap_lines + lines

            with open(iscsid_conf_path, "w") as f:
                f.writelines(lines)

            print("CHAP authentication configured successfully!\n")

            print("Modified iscsid.conf contents:\n")
            with open(iscsid_conf_path, "r") as f:
                print(f.read())

        except FileNotFoundError:
            print(f"Error: {iscsid_conf_path} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("CHAP authentication setup cancelled.")
