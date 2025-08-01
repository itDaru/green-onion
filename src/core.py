import os
from blessed import Terminal

term = Terminal()

def clear_screen():
    print(term.clear)

def display_menu(options, is_main_menu=False, subtitle=None):
    clear_screen()

    # --- Title ---
    title = """
  _      _                          ____                            _  _                      
 | |    (_) _ __   _   _ __  __    |  _ \   ___  _ __    ___   ___ (_)| |_   ___   _ __  _   _ 
 | |    | || '_ \ | | | |\ \/ /    | |_) | / _ \| '_ \  / _ \ / __|| || __| / _ \ | '__|| | | |
 | |___ | || | | || |_| | >  <     |  _ < |  __/| |_) || (_) |\__ \| || |_ | (_) || |   | |_| |
 |_____||_||_| |_| \__,_|/_/\_\    |_| \_\ \___|| .__/  \___/ |___/|_| \__\ \___/ |_|    \__, |
                        _    _                  |_|                                      |___/                                            
                       |  \/  |  __ _  _ __    __ _   __ _   ___  _ __           
                       | |\/| | / _` || '_ \  / _` | / _` | / _ \| '__|          
                       | |  | || (_| || | | || (_| || (_| ||  __/| |             
                       |_|  |_| \__,_||_| |_| \__,_| \__, | \___||_|             
                                                     |___/                     
"""
    title_lines = title.splitlines()
    # Calculate the width of the title block for centering
    block_width = max(len(line) for line in title_lines)
    start_col = (term.width - block_width) // 2

    for line in title_lines:
        # Use term.move_x to set the starting column for each line
        print(term.move_x(start_col) + line)

    # --- Subtitle ---
    if subtitle:
        print(term.center(subtitle))
        print() # Add a blank line

    # --- Separator ---
    print(term.center("--- --- ---"))
    print()

    # --- Options ---
    option_lines = []
    option_lines.append("Select an option:")
    option_lines.append("") # Add a blank line

    for i, option in enumerate(options):
        option_lines.append(f"{i+1}. {option}")

    if is_main_menu:
        option_lines.append("")
        option_lines.append("0. Exit")
    else:
        option_lines.append("")
        option_lines.append("0. Back")

    # Calculate the width of the options block for centering
    block_width = max(len(line) for line in option_lines)
    start_col = (term.width - block_width) // 2

    for line in option_lines:
        # Use term.move_x to set the starting column for each line
        print(term.move_x(start_col) + line)

def get_choice(options):
    print("\n" * 3)
    while True:
        try:
            # Center the input prompt
            prompt = "Enter your choice: "
            with term.location(x=(term.width - len(prompt)) // 2):
                choice_str = input(prompt)
            choice = int(choice_str)

            if 0 <= choice <= len(options):
                return choice
            else:
                # Center the error message
                error_msg = "Invalid choice. Try again."
                with term.location(x=(term.width - len(error_msg)) // 2):
                    print(error_msg)
        except ValueError:
            # Center the error message
            error_msg = "Invalid input. Enter a number."
            with term.location(x=(term.width - len(error_msg)) // 2):
                print(error_msg)
