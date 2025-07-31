# 🛡️  Linux Repository Manager 🛡️

A Python-based tool to configure and manage a linux repository.

Intended for usage with Veeam.

## 🚀 Features

*   **Network Configuration**: Setup Bonded/Normal networking on the host.
*   **iSCSI Configuration**: Connect to iSCSI servers, setup disks, mount filesystems.

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

