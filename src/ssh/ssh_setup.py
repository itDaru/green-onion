import subprocess
import shutil
import datetime

def _get_ssh_service_name():
    """Determines the correct SSH service name (ssh.service or sshd.service)."""
    try:
        # Check for ssh.service
        result = subprocess.run(["systemctl", "list-unit-files", "--type=service"], capture_output=True, text=True, check=True)
        if "ssh.service" in result.stdout:
            return "ssh"
        # Check for sshd.service
        elif "sshd.service" in result.stdout:
            return "sshd"
        else:
            return None
    except subprocess.CalledProcessError:
        return None
    except FileNotFoundError:
        return None




def _get_ssh_status():
    """Checks if the ssh service is active."""
    ssh_service_name = _get_ssh_service_name()
    if not ssh_service_name:
        return "unknown" # Could not determine service name

    try:
        result = subprocess.run(["systemctl", "is-active", f"{ssh_service_name}.service"], capture_output=True, text=True)
        if result.returncode == 0:
            return "active"
        else:
            return "inactive"
    except FileNotFoundError:
        return "unknown"

def toggle_ssh_service():
    """Enables/disables and starts/stops the SSH service."""
    status = _get_ssh_status()
    print(f"\nCurrent SSH service status: {status.upper()}")

    if status == "unknown":
        print("Could not determine SSH status. 'systemctl' command might not be available.")
        input("Press Enter to continue...")
        return

    if status == "active":
        prompt = "Do you want to disable and stop the SSH service? (yes/no) [no]: "
        action = "disable"
    else:
        prompt = "Do you want to enable and start the SSH service? (yes/no) [yes]: "
        action = "enable"

    choice = input(prompt).strip().lower()

    if (action == "disable" and choice in ['y', 'yes']) or \
       (action == "enable" and choice in ['y', 'yes', '']):
        try:
            ssh_service_name = _get_ssh_service_name()
            if not ssh_service_name:
                print("Could not determine SSH service name. Cannot toggle service.")
                return

            if action == "enable":
                print("Enabling and starting SSH service...")
                subprocess.run(["systemctl", "enable", "--now", f"{ssh_service_name}.service"], check=True, capture_output=True)
                print("SSH service enabled and started successfully.")
            else:
                print("Disabling and stopping SSH service...")
                subprocess.run(["systemctl", "disable", "--now", f"{ssh_service_name}.service"], check=True, capture_output=True)
                print("SSH service stopped and disabled successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing systemctl command: {e.stderr}")
    else:
        print("No changes made.")

    input("Press Enter to continue...")


def harden_ssh():
    """Hardens the SSH server configuration by prepending secure settings."""
    sshd_config_path = "/etc/ssh/sshd_config"

    hardened_settings = [
        "# --- Hardened settings by Linux Repository Manager ---",
        "PermitRootLogin no",
        "PubkeyAuthentication yes",
        "PasswordAuthentication no",
        "ChallengeResponseAuthentication no",
        "PermitEmptyPasswords no",
        "X11Forwarding no",
        "MaxAuthTries 3",
        "LoginGraceTime 20",
        "# --- End of hardened settings ---"
    ]

    print("\n--- SSH Hardening ---")
    print("This will apply security settings to your SSH configuration by adding them to the top of the file.")

    print("\n" + "!"*70)
    print("! WARNING: This will disable password-based authentication.          !")
    print("! You will ONLY be able to log in using SSH keys.                    !")
    print("! Ensure you have configured an SSH key for a user with sudo access. !")
    print("!"*70 + "\n")

    confirm = input("Are you sure you want to apply these settings? (yes/no) [no]: ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("SSH hardening cancelled.")
        input("Press Enter to continue...")
        return

    try:
        backup_path = f"{sshd_config_path}.bak.{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        print(f"Creating backup of current configuration at {backup_path}...")
        shutil.copy2(sshd_config_path, backup_path)

        with open(sshd_config_path, 'r') as f:
            original_content = f.read()

        new_content = "\n".join(hardened_settings) + "\n\n" + original_content

        with open(sshd_config_path, 'w') as f:
            f.write(new_content)
        print(f"Hardened configuration written to {sshd_config_path}.")

        restart_choice = input("\nDo you want to restart the SSH service to apply changes now? (yes/no) [yes]: ").strip().lower()
        if restart_choice in ['', 'y', 'yes']:
            print("Restarting SSH service...")
            ssh_service_name = _get_ssh_service_name()
            if not ssh_service_name:
                print("Could not determine SSH service name. Cannot restart service.")
                return
            subprocess.run(["systemctl", "restart", f"{ssh_service_name}.service"], check=True, capture_output=True)
            print("SSH service restarted.")
        else:
            print("Please restart the SSH service manually ('sudo systemctl restart ssh') to apply changes.")

    except (FileNotFoundError, PermissionError, subprocess.CalledProcessError) as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    input("Press Enter to continue...")