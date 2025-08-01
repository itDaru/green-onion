import subprocess
import os
import time

def iscsi_connect():
    target_ip = input("Enter the iSCSI target IP address: ").strip()
    if not target_ip:
        print("IP address cannot be empty.")
        return

    try:
        # Discover targets
        print(f"Discovering targets on {target_ip}...")
        discover_cmd = ["iscsiadm", "-m", "discovery", "-t", "sendtargets", "-p", target_ip]
        discover_result = subprocess.run(discover_cmd, capture_output=True, text=True, check=True)
        
        discovered_targets = []
        for line in discover_result.stdout.splitlines():
            parts = line.split()
            if len(parts) > 1:
                discovered_targets.append(parts[1])

        if not discovered_targets:
            print("No iSCSI targets found on the specified IP.")
            return

        # Check for active sessions
        sessions_cmd = ["iscsiadm", "-m", "session"]
        sessions_result = subprocess.run(sessions_cmd, capture_output=True, text=True)
        active_iqns = []
        for line in sessions_result.stdout.splitlines():
            if "tcp:" in line:
                active_iqns.append(line.split()[2])

        print("\nDiscovered iSCSI Targets:")
        for i, iqn in enumerate(discovered_targets):
            status = "(logged in)" if iqn in active_iqns else ""
            print(f"{i+1}. {iqn} {status}")

        # Select target
        while True:
            try:
                choice = int(input("\nSelect a target to manage: ")) - 1
                if 0 <= choice < len(discovered_targets):
                    selected_iqn = discovered_targets[choice]
                    break
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input.")

        # Login or Logout
        if selected_iqn in active_iqns:
            confirm = input(f"Target {selected_iqn} is already logged in. Do you want to log out? (yes/no): ").lower()
            if confirm == 'yes':
                logout_cmd = ["iscsiadm", "-m", "node", "-T", selected_iqn, "--logout"]
                subprocess.run(logout_cmd, check=True)
                print(f"Successfully logged out from {selected_iqn}")
        else:
            confirm = input(f"Do you want to log in to {selected_iqn}? (yes/no): ").lower()
            if confirm == 'yes':
                login_cmd = ["iscsiadm", "-m", "node", "-T", selected_iqn, "--login"]
                subprocess.run(login_cmd, check=True)
                print(f"Successfully logged in to {selected_iqn}")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    input("Press Enter to continue...")

def is_iscsi_device(device):    # iSCSI Disk Check
    try:
        transport = subprocess.check_output(
            ["udevadm", "info", "--query=property", "--name=" + device],
            text=True
        )
        if "ID_SCSI_TRANSPORT=iscsi" in transport:
            return True
        return False
    except subprocess.CalledProcessError:
        return False

def list_iscsi_disks():         # iSCSI Disk List
    try:
        sessions_command = ["iscsiadm", "-m", "session"]
        sessions_result = subprocess.run(sessions_command, capture_output=True, text=True, check=True)
        sessions_output = sessions_result.stdout

        if not sessions_output.strip():
            print("No active iSCSI sessions found.")
            input("Press Enter to continue...")
            return

        print("Active iSCSI sessions:")
        for line in sessions_output.splitlines():
            if "tcp" in line:
                parts = line.split()
                iqn = parts[2]
                target_ip = parts[3].split(':')[0]
                print(f"  IQN: {iqn}, IP: {target_ip}")
        lsblk_command = ["lsblk", "-d", "-n", "-o", "NAME,SIZE,MOUNTPOINT,TYPE,TRAN"]
        lsblk_result = subprocess.run(lsblk_command, capture_output=True, text=True, check=True)
        lsblk_output = lsblk_result.stdout

        print("\nDisks:")
        for line in lsblk_output.splitlines():
            if "iscsi" in line:
                print(line)

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    input("Press Enter to continue...")

def format_iscsi_disk():        # iSCSI Disk Format
    try:
        lsblk_command = ["lsblk", "-n", "-o", "NAME,SIZE,TYPE,TRAN"]
        lsblk_result = subprocess.run(lsblk_command, capture_output=True, text=True, check=True)
        lsblk_output = lsblk_result.stdout

        iscsi_disks = []
        for line in lsblk_output.splitlines():
            parts = line.split()
            if len(parts) > 3 and parts[3].lower() == "iscsi":
                device_name = parts[0]
                iscsi_disks.append(device_name)

        if not iscsi_disks:
            print("No iSCSI disks found.")
            input("Press Enter to continue...")
            return

        all_partitions = []
        for disk in iscsi_disks:
            lsblk_partition_command = ["lsblk", "-n", "-o", "NAME,SIZE,TYPE,TRAN", f"/dev/{disk}"]
            lsblk_partition_result = subprocess.run(lsblk_partition_command, capture_output=True, text=True, check=True)
            lsblk_partition_output = lsblk_partition_result.stdout
            
            partitions = []
            for line in lsblk_partition_output.splitlines():
                parts = line.split()
                if len(parts) > 3 and parts[2].lower() == "part":
                    partitions.append(parts[0])
            
            if partitions:
                print(f"Partitions found for /dev/{disk}: {partitions}")
                all_partitions.extend([f"{disk}{part.split(disk)[1]}" for part in partitions])
            else:
                print(f"No partitions found for /dev/{disk}. Formatting the whole disk.")
                all_partitions.append(disk)

        print("\nAvailable iSCSI disks and partitions:")
        for i, disk in enumerate(all_partitions):
            print(f"{i + 1}. /dev/{disk}")

        while True:
            try:
                choice = int(input("Select the disk or partition to format: ")) - 1
                if 0 <= choice < len(all_partitions):
                    selected_disk = all_partitions[choice]
                    break
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input.")

        disk_path = f"/dev/{selected_disk}"

        print("\nAvailable filesystems: xfs, ext4, ext3, ext2")
        fs_choice = input("Enter the filesystem to use (default: xfs): ").lower()
        if not fs_choice:
            fs_choice = "xfs"

        if fs_choice not in ["xfs", "ext4", "ext3", "ext2"]:
            print("Invalid filesystem choice. Using xfs instead.")
            fs_choice = "xfs"

        if selected_disk in iscsi_disks:
            print(f"\nWARNING: A new partition ({disk_path}1) will be created and formatted as {fs_choice}.")
        print(f"Formatting {disk_path} will erase all data on it.")
        confirmation = input("Are you sure you want to continue? (yes/no): ").lower()

        if confirmation == "yes":
            path_to_format = disk_path

            if selected_disk in iscsi_disks:
                print(f"Partitioning {path_to_format}...")
                partition_command = ["parted", "-s", path_to_format, "mklabel", "gpt"]
                subprocess.run(partition_command, check=True)
                print(f"Creating partition on {path_to_format}...")
                create_partition_command = ["parted", "-s", path_to_format, "mkpart", "primary", "0%", "100%"]
                subprocess.run(create_partition_command, check=True)
                path_to_format += "1"
                print("Waiting for partition to be created...")
                subprocess.run(["partprobe"], check=True, capture_output=True)
                time.sleep(2)

            print(f"Creating filesystem on {path_to_format}...")
            mkfs_command = [f"mkfs.{fs_choice}", path_to_format]

            try:
                subprocess.run(mkfs_command, check=True, capture_output=True, text=True)
                print(f"Filesystem created successfully on {path_to_format}.")
            except subprocess.CalledProcessError as e:
                print(f"Error creating filesystem: {e.stderr.strip()}")
                force_choice = input("Formatting failed. Do you want to try forcing it? (yes/no): ").lower().strip()
                if force_choice == 'yes':
                    force_flag = "-f" if fs_choice == "xfs" else " "
                    print(f"Retrying with force option ('{force_flag}')...")
                    mkfs_command_forced = [f"mkfs.{fs_choice}", force_flag, path_to_format]
                    subprocess.run(mkfs_command_forced, check=True)
                    print(f"Filesystem created successfully on {path_to_format} with force option.")
                else:
                    print("Formatting cancelled by user after initial failure.")
        else:
            print("Formatting cancelled.")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    input("Press Enter to continue...")

def mount_iscsi_disk():
    try:
        create_dir_choice = input("Do you want to create a new directory for the mount point? (yes/no) [yes]: ").lower().strip()
        if create_dir_choice in ['', 'yes', 'y']:
            mount_path = input("Enter the full path for the mount point [/srv/veeam]: ").strip()
            if not mount_path:
                mount_path = "/srv/veeam"
            
            print(f"Creating directory {mount_path}...")
            os.makedirs(mount_path, exist_ok=True)
            print("Directory created.")
        else:
            while True:
                mount_path = input("Enter the existing full path for the mount point: ").strip()
                if not mount_path:
                    print("Path cannot be empty.")
                    continue
                if os.path.isdir(mount_path):
                    break
                else:
                    print(f"Error: Directory '{mount_path}' does not exist or is not a directory. Please provide a valid path.")

        lsblk_command = ["lsblk", "-n", "-o", "NAME,TYPE,TRAN"]
        lsblk_result = subprocess.run(lsblk_command, capture_output=True, text=True, check=True)
        
        iscsi_disks = []
        for line in lsblk_result.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[1].lower() == "disk" and parts[2].lower() == "iscsi":
                iscsi_disks.append(parts[0])

        if not iscsi_disks:
            print("No iSCSI disks found.")
            input("Press Enter to continue...")
            return

        selectable_devices = []
        for disk in iscsi_disks:
            lsblk_partition_command = ["lsblk", "-n", "-o", "NAME,TYPE", f"/dev/{disk}"]
            lsblk_partition_result = subprocess.run(lsblk_partition_command, capture_output=True, text=True, check=True)
            
            partitions_found = []
            for line in lsblk_partition_result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 2 and parts[1].lower() == "part":
                    partitions_found.append(parts[0].lstrip('└─├ '))
            
            if partitions_found:
                selectable_devices.extend(partitions_found)
            else:
                selectable_devices.append(disk)

        selectable_devices.sort()
        print("\nAvailable iSCSI disks and partitions to mount:")
        for i, device in enumerate(selectable_devices):
            print(f"{i + 1}. /dev/{device}")

        choice = int(input("Select the disk or partition to mount: ")) - 1
        selected_device_name = selectable_devices[choice]
        device_to_mount = f"/dev/{selected_device_name}"

        if selected_device_name in iscsi_disks:
            print(f"Whole disk {device_to_mount} selected. Assuming partition 1 for mounting.")
            device_to_mount += "1"
        
        if not os.path.exists(device_to_mount):
            print(f"Error: The partition {device_to_mount} does not seem to exist. Cannot mount.")
            input("Press Enter to continue...")
            return

        try:
            subprocess.run(["findmnt", "-n", device_to_mount], check=True, capture_output=True)
            print(f"Device {device_to_mount} is already mounted. Aborting.")
            input("Press Enter to continue...")
            return
        except subprocess.CalledProcessError:
            pass

        print(f"Mounting {device_to_mount} on {mount_path}...")
        subprocess.run(["mount", device_to_mount, mount_path], check=True)
        print("Mount successful.")

        fstab_choice = input("Do you want to add this mount to /etc/fstab for persistence? (yes/no) [yes]: ").lower().strip()
        if fstab_choice in ['', 'yes', 'y']:
            print("Adding entry to /etc/fstab...")
            blkid_uuid_result = subprocess.run(["blkid", "-s", "UUID", "-o", "value", device_to_mount], capture_output=True, text=True, check=True)
            uuid = blkid_uuid_result.stdout.strip()
            blkid_type_result = subprocess.run(["blkid", "-s", "TYPE", "-o", "value", device_to_mount], capture_output=True, text=True, check=True)
            fs_type = blkid_type_result.stdout.strip()

            fstab_entry = f"UUID={uuid} {mount_path} {fs_type} defaults,nofail,_netdev 0 0\n"
            print(f"The following line will be added to /etc/fstab:\n{fstab_entry}")
            confirm_fstab = input("Confirm? (yes/no) [yes]: ").lower().strip()
            if confirm_fstab in ['', 'yes', 'y']:
                with open("/etc/fstab", "a") as f:
                    f.write(fstab_entry)
                print("Entry added to /etc/fstab.")

    except (subprocess.CalledProcessError, ValueError, IndexError) as e:
        print(f"An error occurred: {e}")
    input("Press Enter to continue...")

if __name__ == "__main__":
    list_iscsi_disks()
    format_iscsi_disk()
