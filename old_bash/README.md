# [DEPRECATED] & [NOT IN DEVELOPMENT]


## Rocky Linux Imutable Repository Preparation Script

This script automates the initial setup of a Rocky Linux server to be used as an immutable repository for Veeam Backup & Replication. It streamlines various system configurations, making the server ready to host your backups securely.

### Features

- **Tmux Integration:** Automatically launches the script within a tmux session, protecting against SSH disconnections. Can be skipped with '--no-tmux'.
- **Hostname Configuration:** Post-install hostname reconfiguration for the server.
- **Static IP:** Only static IP support for the moment. Configure IP, subnet mask, gateway and DNS. Includes ping and nslookup test.
- **User Configuration:** Create a service user on the sudo group and attach a key for remote login.
- [PENDING] **Remote Storage:** Configure remote storage (NFS, iSCSI, SMB).
- **Storage:** Storage configuration for local or remote disks. Implement LVM or not. Always format to XFS (Fast Clone feature). Automatic mountpoint to `/data` with correct permissions.

### Pre-requisites

- Fresh install of Rocky Linux (currently tested on Rocky Linux 9.x)
- Root (or sudo) privileges for script execution.
- Network Connectivity for Tmux installation. (can be skiped with --no-tmux)
- Veeam Backup Server for final configuration.
- A Disk for the system and a disk (or remote storage) for the backup data.
- Recommended: SSH key for veeamsvc user (not needed if locked-down).

### Usage:

1.- Download the script:
'wget https://raw.githubusercontent.com/itDaru/green-onion/refs/heads/main/vhrs-rocky-sysconfig.sh -o /tmp/vhrs-rocky-sysconfig.sh'

2.- Give execution permissions:
'chmod +x /tmp/vhrs-rocky-sysconfig.sh'

3.- Execute the script:
'/tmp/vhrs-rocky-sysconfig.sh'

4.- Follow the script instructions.
