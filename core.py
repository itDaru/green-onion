import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_menu(options, is_main_menu=False):
    print("[Linux Repository Manager]\n\nSelect an option:\n")
    for i, option in enumerate(options):
        print(f"{i+1}. {option}")
    if is_main_menu:
        print("\n0. Exit")
    else:
        print("\n0. Back")

def get_choice(options):
    while True:
        try:
            choice = int(input("Enter your choice: "))
            if 0 <= choice <= len(options):
                return choice
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Invalid input. Enter a number.")
