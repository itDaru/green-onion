from core import clear_screen, display_menu, get_choice
from users import users_setup


def users_menu():
    """Displays the user management menu and handles user choices."""
    options = [
        "Setup user",
        'Setup user "veeamsvc"',
        'Setup user "ansible"',
        "Disable user login",
        "Remove user"
    ]

    while True:
        clear_screen()
        display_menu(options)
        choice = get_choice(options)

        if choice == 0:
            break
        elif choice == 1:
            users_setup.setup_user()
        elif choice == 2:
            users_setup.setup_veeam_user()
        elif choice == 3:
            users_setup.setup_ansible_user()
        elif choice == 4:
            users_setup.disable_user_login()
        elif choice == 5:
            users_setup.remove_user()
        else:
            print("Invalid choice. Try again.\n")
