# 🛡️  Linux Repository Manager 🛡️

A Python-based tool to configure and manage a linux repository.

Intended for usage with Veeam.

## 🚀 Features

*   **Network Configuration**: Streamline network settings with interface selection and bond/plain networking options.
*   **iSCSI Configuration**: Connect to iSCSI servers and set up CHAP authentication.
*   **Configuration Clearing**: Easily clear existing network configurations.

## ⚙️  Prerequisites

*   Rocky Linux 9.x
*   Python 3.x

## 🛠️  Usage

1.  Run the main script with root privileges:

    ```bash
    sudo python3 main.py
    ```

2.  Follow the menu options to configure network and iSCSI settings.

###    OR

1.  Download the release binary.

2.  Run the binary with root privileges:

    ```bash
    sudo exec lrm
    ```

## 📂 File Structure
├── core.py # Core functions (clear_screen, display_menu, get_choice) 
├── iscsi_config.py # iSCSI configuration functions 
├── main.py # Main entry point 
├── network_config.py # Network configuration functions 
└── README.md # Documentation
