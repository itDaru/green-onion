Linux Repository Manager 🐧

Table of Contents

	About the Project 🚀

    Features ✨

    Folder Structure 📂

    Getting Started 🛠️

        Prerequisites ✅

        Installation ⬇️

    Usage 🚀

    Contributing 🤝

    License 📜

    Contact 📧

About the Project 🚀

Linux Repository Manager is a python utility designed to effortlessly manage Linux system configurations. It currently provides powerful functionalities for iSCSI and network settings, aiming to simplify complex administrative tasks.

Features ✨

    iSCSI Management: Automate the setup and management of iSCSI disks! 🎯

    Network Configuration: Effortlessly configure network interfaces, set up a static normal interface or a static bond interface. 🌐

Folder Structure 📂

This project keeps things with a straightforward structure:

.
├── .github/              # GitHub 🤖
├── src/                  # Python utlity source code 🐍
│   ├── iscsi/            # Modules for iSCSI ✨
│   ├── network/          # Modules for networking 🧙‍♂️
│   ├── core/             # Core utilities and shared functions 🧠
│   └── main.py           # The main entry point for the application ▶️
├── .gitignore            # Files Git should totally ignore 🤫
├── LICENSE               # The project's license file 📜
└── README.md             # You are here! 👋

Getting Started 🛠️

Here's how to get this tool up and running on your servers

Prerequisites ✅

    Python 3.x
	nmcli utility

Usage 🚀

You've got a couple of ways to use Linux Repository Manager:

    [Recommended]
    Using a Release Binary (if available):
    wget https://github.com/itDaru/linux-repository-manager/releases/latest/download/lrm

# Example: Make the binary executable and run it with superuser powers
chmod +x lrm
sudo ./lrm

Cloning the Repository and Running Directly:
Prefer to roll with the source code? No problem! 
Clone the repo and execute main.py directly. This is great if you want to poke around the code or contribute. 🧑‍💻

```bash
git clone https://github.com/itDaru/linux-repository-manager.git
cd linux-repository-manager/src
sudo python3 main.py
```

# Contributing 🤝

Love what you see? Want to make it even better? Your contributions are super appreciated! 🙌

If you have a brilliant idea or find a bug, don't hesitate! Fork the repo, make your changes, and send a pull request. You can also open an issue with the "enhancement" tag. And hey, a ⭐ star ⭐ for the project would be awesome! Thanks a bunch!

    Fork the Project

    Create your Feature Branch (git checkout -b feature/AmazingFeature)

    Commit your Changes (git commit -m 'Add some AmazingFeature')

    Push to the Branch (git push origin feature/AmazingFeature)

    Open a Pull Request

# License 📜

This project is open-source and distributed under the MIT License. Check out the LICENSE file for all the details!

# Contact 📧

Got questions or just want to say hi? Feel free to reach out!

Project Link: https://github.com/itDaru/linux-repository-manager
