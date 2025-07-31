import subprocess
import shutil
import secrets
import string
import os
import pwd


def _generate_password(length=16):
    """Generates a random 16-character password with letters, digits, and . - ! symbols."""
    alphabet = string.ascii_letters + string.digits + '.-!'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def _write_ssh_key(username, public_key):
    """Writes a public SSH key to the user's authorized_keys file."""
    try:
        user_info = pwd.getpwnam(username)
        uid = user_info.pw_uid
        gid = user_info.pw_gid

        ssh_dir = f"/home/{username}/.ssh"
        auth_keys_file = f"{ssh_dir}/authorized_keys"

        os.makedirs(ssh_dir, exist_ok=True)
        os.chmod(ssh_dir, 0o700)
        shutil.chown(ssh_dir, user=uid, group=gid)

        with open(auth_keys_file, 'a') as f:
            f.write(f"{public_key}\n")

        os.chmod(auth_keys_file, 0o600)
        shutil.chown(auth_keys_file, user=uid, group=gid)

        print(f"SSH public key added successfully for user '{username}'.")
        return True
    except (KeyError, OSError) as e:
        print(f"Error writing SSH key for '{username}': {e}")
        return False

def _setup_ssh_key(username):
    """Handles getting and setting up SSH key for a user."""
    public_key = input("Paste the public key: ").strip()
    if not public_key:
        print("No public key provided. Skipping SSH key setup.")
        return
    _write_ssh_key(username, public_key)

def _get_sudo_group():
    """Determines the correct sudo group ('wheel' or 'sudo')."""
    if shutil.which("grep") and subprocess.run(["grep", "-q", "^wheel:", "/etc/group"], capture_output=True).returncode == 0:
        return "wheel"
    return "sudo"

def setup_user():
    username = input("Enter the username for the new user: ").strip()
    if not username:
        print("Username cannot be empty.")
        input("Press Enter to continue...")
        return

    print("\nSelect a shell for the user:")
    print("1. /bin/bash (default)")
    print("2. /sbin/nologin (disable login)")
    shell_choice = input("Enter your choice (1-2, default 1): ").strip()

    shell = "/bin/bash"
    if shell_choice == '2':
        shell = "/sbin/nologin"

    try:
        subprocess.run(["useradd", "-m", "-s", shell, username], check=True)
        print(f"User '{username}' created successfully with shell {shell}.")

        ssh_choice = input(f"Do you want to add an SSH public key for this user? (yes/no) [no]: ").strip().lower()
        if ssh_choice in ['yes', 'y']:
            _setup_ssh_key(username)

        setup_password_choice = input("Do you want to set a password for this user? (yes/no) [yes]: ").strip().lower()
        if setup_password_choice in ['', 'yes', 'y']:
            password = _generate_password()
            print("\nUse this randomly generated password or set a custom secure one:\n")
            print(f"{password}\n")
            print("\nWARNING: SAVE THIS PASSWORD IN A SECURE PLACE! \n\nIT WILL NOT BE DISPLAYED AGAIN!\n")

            print(f"Setting password for user '{username}'...")
            subprocess.run(["passwd", username], check=True)
            print(f"Password set for user '{username}'.")

            sudo_choice = input(f"Do you want to add user '{username}' to sudoers? (yes/no) [no]: ").strip().lower()
            if sudo_choice in ['yes', 'y']:
                sudo_group = _get_sudo_group()
                try:
                    subprocess.run(["usermod", "-aG", sudo_group, username], check=True)
                    print(f"User '{username}' added to {sudo_group} group.")
                except subprocess.CalledProcessError as e:
                    print(f"Error adding user '{username}' to {sudo_group} group: {e}")
        else:
            print("Password setup skipped.")

    except subprocess.CalledProcessError as e:
        print(f"Error creating user '{username}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    input("Press Enter to continue...")



def setup_veeam_user():
    """Sets up a specific user 'veeamsvc' with a random password and sudo access."""
    username = "veeamsvc"
    shell = "/bin/bash"
    print(f'Setting up user "{username}"...')

    try:
        pwd.getpwnam(username)
        print(f"User '{username}' already exists. Aborting setup.")
        input("Press Enter to continue...")
        return
    except KeyError:
        pass

    try:
        subprocess.run(["useradd", "-m", "-s", shell, username], check=True)
        print(f"User '{username}' created successfully.")

        ssh_choice = input(f"Do you want to add an SSH public key for '{username}'? (yes/no) [no]: ").strip().lower()
        if ssh_choice in ['yes', 'y']:
            _setup_ssh_key(username)

        password = _generate_password()
        subprocess.run(
            ["chpasswd"],
            input=f"{username}:{password}".encode('utf-8'),
            check=True,
            capture_output=True
        )
        print("\n" + "="*50)
        print(f"IMPORTANT: PASSWORD FOR '{username}'")
        print("="*50)
        print("\nWARNING: SAVE THIS PASSWORD IN A SECURE PLACE!")
        print("IT WILL NOT BE DISPLAYED AGAIN!\n")
        print(f"Password: {password}\n")
        print("="*50 + "\n")

        sudo_choice = input(f"Do you want to add user '{username}' to sudoers? (yes/no) [yes]: ").strip().lower()
        if sudo_choice in ['', 'yes', 'y']:
            sudo_group = _get_sudo_group()
            subprocess.run(["usermod", "-aG", sudo_group, username], check=True)
            print(f"User '{username}' added to '{sudo_group}' group.")

    except subprocess.CalledProcessError as e:
        print(f"Error during user setup for '{username}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    input("Press Enter to continue...")


def setup_ansible_user():
    """Sets up a secure 'ansible' user for automation with passwordless sudo."""
    username = "ansible"
    shell = "/sbin/nologin"
    print(f'Setting up user "{username}" for automation...')

    try:
        pwd.getpwnam(username)
        print(f"User '{username}' already exists. Aborting setup.")
        input("Press Enter to continue...")
        return
    except KeyError:
        pass

    print("\n" + "!"*60)
    print("! WARNING: SECURITY RISK                                     !")
    print("! This will create a user with PASSWORDLESS SUDO access.     !")
    print("! Anyone with the corresponding SSH private key will have    !")
    print("! full root access to this system without a password.        !")
    print("!"*60 + "\n")
    confirm = input(f"Are you sure you want to create the '{username}' user with these permissions? (yes/no) [no]: ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Setup for 'ansible' user cancelled.")
        input("Press Enter to continue...")
        return

    public_key = input("Paste the public SSH key for the 'ansible' user: ").strip()
    if not public_key:
        print("A public key is mandatory for the 'ansible' user. Aborting setup.")
        input("Press Enter to continue...")
        return

    user_created = False
    try:
        subprocess.run(["useradd", "-m", "-s", shell, username], check=True)
        user_created = True
        print(f"User '{username}' created successfully.")

        subprocess.run(["passwd", "-l", username], check=True, capture_output=True)
        print(f"Password for '{username}' has been locked.")

        sudoers_file = f"/etc/sudoers.d/{username}"
        sudoers_content = f"{username} ALL=(ALL) NOPASSWD: ALL\n"
        with open(sudoers_file, 'w') as f:
            f.write(sudoers_content)
        os.chmod(sudoers_file, 0o440)
        print(f"Configured passwordless sudo for '{username}' via {sudoers_file}.")

        if not _write_ssh_key(username, public_key):
            raise Exception("Failed to write SSH key.")

        print(f"\nSetup for user '{username}' is complete.")

    except Exception as e:
        print(f"\nAn error occurred during setup: {e}")
        print("Attempting to roll back changes...")
        if user_created:
            try:
                sudoers_file = f"/etc/sudoers.d/{username}"
                if os.path.exists(sudoers_file):
                    os.remove(sudoers_file)
                    print(f"Removed sudoers file: {sudoers_file}")
                subprocess.run(["userdel", "-r", username], check=True, capture_output=True)
                print(f"Successfully removed partially configured user '{username}'.")
            except Exception as cleanup_e:
                print(f"CRITICAL: Failed to clean up user '{username}'. Manual intervention required: {cleanup_e}")

    input("Press Enter to continue...")


def disable_user_login():    
    username = input("Enter the username to disable login for: ").strip()
    if not username:
        print("Username cannot be empty.")
        input("Press Enter to continue...")
        return
    try:
        subprocess.run(["usermod", "-s", "/sbin/nologin", username], check=True)
        print(f"Login disabled for user '{username}'.")
    except subprocess.CalledProcessError as e:
        print(f"Error disabling login for user '{username}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    input("Press Enter to continue...")


def remove_user():
    """Removes a user from the system."""
    username = input("Enter the username to remove: ").strip()
    if not username:
        print("Username cannot be empty.")
        input("Press Enter to continue...")
        return

    confirm_removal = input(f"Are you sure you want to remove user '{username}'? (yes/no): ").strip().lower()
    if confirm_removal not in ['yes', 'y']:
        print("User removal cancelled.")
        input("Press Enter to continue...")
        return

    final_confirm = input(f"This will permanently delete user '{username}'. Confirm again (yes/no): ").strip().lower()
    if final_confirm not in ['yes', 'y']:
        print("User removal cancelled.")
        input("Press Enter to continue...")
        return

    try:
        subprocess.run(["userdel", "-r", username], check=True)
        print(f"User '{username}' removed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error removing user '{username}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    input("Press Enter to continue...")
