# 🛡️  Linux Repository Manager 🛡️

A Python-based tool to configure and manage a Linux system, focusing on network, storage, and user setup for hardened repositories.
The tool is built with security best practices in mind, including secure password generation and safe user provisioning.

Intended for usage with Veeam.

## 🚀 Features

*   **Network Configuration** 🌐: Set up network interfaces with bonding/NIC teaming options.
*   **iSCSI Management** 🎯: Discover and connect to iSCSI targets, manage sessions, and configure CHAP authentication for secure storage connections.
*   **Local Storage Management** 💾: List, format, and mount local disks.
*   **User Management** 👤: Create and manage system users.
    *   Create standard users with interactive password setup and optional SSH key/sudo access.
    *   Set up a dedicated `veeamsvc` user with a secure, randomly generated password.
    *   Provision a passwordless `ansible` user for automation, secured with an SSH key and non-interactive shell.
    *   Disable or completely remove users from the system.
*   **SSH Management** 🔑: Enable/disable the SSH service, apply security hardening, and generate new SSH key pairs.

## ⚙️  Supported Systems:

*   **Systems with Network Manager** (Enterprise Linux)
*   **Systems with Ifupdown** (Debian)
*   **Systems with Netplan** (Ubuntu)
*   **Systems with wicked** (SUSE)
*   **Systems with Networkd** (Others)

## ⚙️  Prerequisites

*   Python 3.x

## 🛠️  Usage

### From Binary Release

1.  Download the release binary:
    ```bash
    wget https://github.com/itDaru/linux-repository-manager/releases/latest/download/lrm
    ```

2.  Make the binary executable:

    ```bash
    chmod +x lrm
    ```

3.  Run the binary with root privileges:

    ```bash
    sudo ./lrm
    ```


* **In Summary:**

    ```bash
    wget https://github.com/itDaru/linux-repository-manager/releases/latest/download/lrm
    chmod +x lrm
    sudo ./lrm
    ```

### From Source

1.  Clone the repository:

    ```bash
    git clone https://github.com/itDaru/linux-repository-manager.git
    ```

2.  Access the source files:

    ```bash
    cd linux-repository-manager/src
    ```

3.  Run the main script with root privileges:

    ```bash
    sudo python3 main.py
    ```

## 📂 File Structure

```
.
├── 📂 .github
├── 📂 src
│   ├── 📂 iscsi
│   │   ├── iscsi_auth.py
│   │   ├── iscsi_menu.py
│   │   └── iscsi_setup.py
│   ├── 📂 network
│   │   ├── network_check.py
│   │   ├── network_menu.py
│   │   ├── network_setup.py
│   │   ├── network_setup_ifupdown.py
│   │   ├── network_setup_netifrc.py
│   │   ├── network_setup_netplan.py
│   │   ├── network_setup_networkd.py
│   │   ├── network_setup_networkmanager.py
│   │   └── network_setup_wicked.py
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
```
