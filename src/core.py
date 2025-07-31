import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_menu(options, is_main_menu=False, subtitle=None):
    print("""
  _      _                          ____                           _  _                      
 | |    (_) _ __   _   _ __  __    |  _ \  ___  _ __    ___   ___ (_)| |_  ___   _ __  _   _ 
 | |    | || '_ \ | | | |\ \/ /    | |_) |/ _ \| '_ \  / _ \ / __|| || __|/ _ \ | '__|| | | |
 | |___ | || | | || |_| | >  <     |  _ <|  __/| |_) || (_) |\__ \| || |_| (_) || |   | |_| |
 |_____||_||_| |_| \__,_|/_/\_\    |_| \_\\___|| .__/  \___/ |___/|_| \__\\___/ |_|    \__, |
                        _    _                 |_|                                     |___/                                            
                       |  \/  |  __ _  _ __    __ _   __ _   ___  _ __           
                       | |\/| | / _` || '_ \  / _` | / _` | / _ \| '__|          
                       | |  | || (_| || | | || (_| || (_| ||  __/| |             
                       |_|  |_| \__,_||_| |_| \__,_|\__, | \___||_|             
                                                     |___/                     
""")
    if subtitle:
        print(f"{subtitle}\n")
    print("Select an option:\n")
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
