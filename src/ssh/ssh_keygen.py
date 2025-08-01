import subprocess
import os
import pwd
import tempfile

from users.users_setup import _write_ssh_key

def generate_ssh_keypair():
    """Generates an SSH keypair and offers to add the public key to user accounts."""
    print("Select an SSH key algorithm:")
    print("1. ED25519 (Modern, highly secure, and fast) [Default]")
    print("2. RSA (Recommended for general use)")
    print("3. ECDSA (Smaller keys, faster performance)")
    print("4. DSA (Legacy, not recommended)")

    algorithms = {
        "1": "ed25519",
        "2": "rsa",
        "3": "ecdsa",
        "4": "dsa"
    }

    while True:
        choice = input("Enter your choice (1-4, default 1): ").strip() or "1"
        if choice in algorithms:
            algo = algorithms[choice]
            break
        else:
            print("Invalid choice. Please select a number between 1 and 4.")

    comment = input("Enter a comment for the key (e.g., your_email@example.com, press Enter to skip): ").strip()

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            private_key_path = os.path.join(tmpdir, "temp_ssh_key")
            public_key_path = f"{private_key_path}.pub"

            command_parts = ["ssh-keygen", "-t", algo, "-f", private_key_path, "-q", "-N", ""]
            if comment:
                command_parts.extend(["-C", comment])

            print("\n--- SSH Key Generation ---")
            print(f"Algorithm selected: {algo.upper()}")
            if comment:
                print(f"Comment: '{comment}'")

            subprocess.run(command_parts, check=True, capture_output=True)

            with open(private_key_path, 'r') as f:
                private_key = f.read().strip()
            with open(public_key_path, 'r') as f:
                public_key = f.read().strip()

            print("\n--- Generated SSH Private Key (Copy this now!) ---")
            print("WARNING: This private key will not be saved to disk by this script.")
            print("Please copy it to a secure location immediately.")
            print("=" * 70)
            print(private_key)
            print("=" * 70)

            print("\n--- Generated SSH Public Key ---")
            print(public_key)
            print("=" * 70)

            print("\n--- Add Public Key to User(s) ---")
            users = [p.pw_name for p in pwd.getpwall() if p.pw_uid >= 1000 and 'nologin' not in p.pw_shell]
            if not users:
                print("No suitable users found to add the public key to.")
            else:
                print("\nAvailable users:")
                for i, user in enumerate(users):
                    print(f"{i+1}. {user}")

                selected_indices_str = input("Enter numbers of users to add the key to (e.g., 1,3), or press Enter to skip: ").strip()

                if selected_indices_str:
                    try:
                        selected_indices = [int(x.strip()) - 1 for x in selected_indices_str.split(',')]

                        for index in selected_indices:
                            if 0 <= index < len(users):
                                username = users[index]
                                print(f"Adding public key to {username}...")
                                _write_ssh_key(username, public_key)
                            else:
                                print(f"Invalid user number: {index + 1}. Skipping.")

                    except ValueError:
                        print("Invalid input. Please enter numbers separated by commas.")

    except subprocess.CalledProcessError as e:
        print(f"\nError generating SSH key. ssh-keygen exited with an error:")
        print(f"Stderr: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    input("Press Enter to continue...")

if __name__ == "__main__":
    generate_ssh_keypair()
