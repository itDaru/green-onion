# 🛡️  Linux Repository Manager 🛡️

A Python-based tool to configure and manage a Linux system, focusing on network, storage, and user setup for hardened repositories. The tool is built with security best practices in mind, including secure password generation and safe user provisioning.

Intended for usage with Veeam.

## 🚀 Features

*   **Network Configuration** 🌐: Streamline network settings with interface selection and bond/plain networking options.
*   **iSCSI Management** 🎯: Discover and connect to iSCSI targets, manage sessions, and configure CHAP authentication for secure storage connections.
*   **User Management** 👤: Create and manage system users with fine-grained controls.
    *   Create standard users with interactive password setup and optional SSH key/sudo access.
    *   Set up a dedicated `veeamsvc` user with a secure, randomly generated password.
    *   Provision a passwordless `ansible` user for automation, secured with an SSH key and non-interactive shell.
    *   Disable or completely remove users from the system.

## 🖥️ Supported OS:

### RedHat Family:
*   **RedHat Linux Enterprise 9.x**
*   **CentOS Stream**
*   **Rocky Linux 9.x**


## ⚙️  Prerequisites

*   Python 3.x

## 🛠️  Usage

1.  Run the main script with root privileges:

    ```bash
    sudo python3 main.py
    ```

2.  Follow the menu options to configure network, iSCSI, and user settings.

###    OR

1.  Download the release binary.

2.  Run the binary with root privileges:

    ```bash
    sudo exec lrm
    ```

## 📂 File Structure

.
├── 📂 .github
├── 📂 src
│   ├── 📂 iscsi
│   │   ├── iscsi_auth.py
│   │   ├── iscsi_menu.py
│   │   └── iscsi_setup.py
│   ├── 📂 network
│   │   ├── network_menu.py
│   │   └── network_setup.py
│   ├── 📂 ssh
│   │   ├── ssh_keygen.py
│   │   ├── ssh_menu.py
│   │   └── ssh_setup.py
│   ├── 📂 storage
│   │   ├── storage_menu.py
│   │   └── storage_setup.py
│   └── 📂 users
│       ├── users_menu.py
│       └── users_setup.py
├── .gitignore
├── LICENSE.md
└── README.md
