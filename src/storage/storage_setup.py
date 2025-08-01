import subprocess
import os
import shlex
import time


def list_disks():
    print("\n--- Listing Local Disks ---")
    try:
        subprocess.run(["lsblk", "-o", "NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE,LABEL"], check=True)
    except FileNotFoundError:
        print("Error: 'lsblk' command not found. This feature requires 'util-linux' package.")
    except subprocess.CalledProcessError as e:
        print(f"Error listing disks: {e}")
    input("\nPress Enter to continue...")


def mount_disk():
    print("\n--- Mount Disk ---")
    try:
        lsblk_output = subprocess.run(
            ["lsblk", "-P", "-o", "NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE,UUID"],
            capture_output=True, text=True, check=True
        ).stdout

        available_devices = []
        print("\nAvailable disks and partitions:")
        for line in lsblk_output.strip().splitlines():
            device_info = {k: v.strip('"') for k, v in (pair.split('=', 1) for pair in shlex.split(line))}

            if device_info.get("TYPE") in ("part", "disk"):
                mountpoint_display = f" (Mounted at: {device_info.get('MOUNTPOINT')})" if device_info.get('MOUNTPOINT') else ""
                available_devices.append(device_info)
                print(f"{len(available_devices)}. /dev/{device_info.get('NAME')} ({device_info.get('SIZE')}){mountpoint_display}")

        if not available_devices:
            print("No unmounted disks or partitions found.")
            input("Press Enter to continue...")
            return

        while True:
            try:
                choice = int(input("Select the disk or partition to mount: ")) - 1
                if 0 <= choice < len(available_devices):
                    selected_device_info = available_devices[choice]
                    break
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        device_path = f"/dev/{selected_device_info.get('NAME')}"
        fs_type = selected_device_info.get('FSTYPE', '')
        uuid = selected_device_info.get('UUID', '')

        try:
            findmnt_result = subprocess.run(["findmnt", "-n", device_path], capture_output=True, text=True)
            if findmnt_result.returncode == 0:
                current_mount_point = findmnt_result.stdout.split()[0]
                print(f"Device {device_path} is already mounted at {current_mount_point}.")
                unmount_choice = input(f"Do you want to unmount it to proceed? (yes/no) [no]: ").strip().lower()
                if unmount_choice in ['yes', 'y']:
                    print(f"Unmounting {device_path}...")
                    subprocess.run(["umount", "-l", device_path], check=True)
                    print(f"{device_path} unmounted successfully.")
                else:
                    print("Mounting cancelled as device is already mounted.")
                    input("Press Enter to continue...")
                    return
        except Exception as e:
            print(f"Error checking or unmounting device: {e}")
            input("Press Enter to continue...")
            return

        while True:
            mount_point = input("Enter the new mount point (e.g., /mnt/data): ").strip()
            if not mount_point:
                print("Mount point cannot be empty.")
            else:
                break
        
        os.makedirs(mount_point, exist_ok=True)
        print(f"Mount point '{mount_point}' ensured.")

        print(f"Mounting {device_path} to {mount_point}...")
        subprocess.run(["mount", device_path, mount_point], check=True)
        print("Disk mounted successfully.")

        fstab_choice = input("Do you want to add this mount to /etc/fstab for persistence? (yes/no) [yes]: ").strip().lower()
        if fstab_choice in ['', 'yes', 'y']:
            print("Adding entry to /etc/fstab...")
            
            if not uuid:
                blkid_uuid_result = subprocess.run(["blkid", "-s", "UUID", "-o", "value", device_path], capture_output=True, text=True, check=True)
                uuid = blkid_uuid_result.stdout.strip()
            
            if not fs_type:
                blkid_type_result = subprocess.run(["blkid", "-s", "TYPE", "-o", "value", device_path], capture_output=True, text=True, check=True)
                fs_type = blkid_type_result.stdout.strip()

            fstab_entry = f"UUID={uuid} {mount_point} {fs_type} defaults 0 0\n"
            print(f"The following line will be added to /etc/fstab:\n{fstab_entry}")
            confirm_fstab = input("Confirm? (yes/no) [yes]: ").strip().lower()
            if confirm_fstab in ['', 'yes', 'y']:
                with open("/etc/fstab", "a") as f:
                    f.write(fstab_entry)
                print("Entry added to /etc/fstab.")
            else:
                print("Adding to /etc/fstab cancelled.")

    except (subprocess.CalledProcessError, ValueError, IndexError) as e:
        print(f"An error occurred: {e}")
    input("Press Enter to continue...")


def format_disk():
    """Formats a local disk or partition, similar to how format_iscsi_disk works."""
    print("\n--- Format Disk ---")
    try:
        lsblk_output = subprocess.run(
            ["lsblk", "-P", "-o", "NAME,SIZE,TYPE,MOUNTPOINT"],
            capture_output=True, text=True, check=True
        ).stdout

        available_devices = []
        print("\nAvailable disks and partitions:")
        for line in lsblk_output.strip().splitlines():
            device_info = {k: v.strip('"') for k, v in (pair.split('=', 1) for pair in shlex.split(line))}
            if device_info.get("TYPE") in ("part", "disk"):
                mountpoint_display = f" (Mounted at: {device_info.get('MOUNTPOINT')})" if device_info.get('MOUNTPOINT') else ""
                available_devices.append(device_info)
                print(f"{len(available_devices)}. /dev/{device_info.get('NAME')} ({device_info.get('SIZE')}){mountpoint_display}")

        if not available_devices:
            print("No disks or partitions found.")
            input("Press Enter to continue...")
            return

        while True:
            try:
                choice = int(input("Select the disk or partition to format: ")) - 1
                if 0 <= choice < len(available_devices):
                    selected_device_info = available_devices[choice]
                    break
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        device_path = f"/dev/{selected_device_info.get('NAME')}"
        device_type = selected_device_info.get('TYPE')
        mount_point = selected_device_info.get('MOUNTPOINT')

        print("\nAvailable filesystems: xfs, ext4, ext3, ext2")
        fs_choice = input("Enter the filesystem to use (default: xfs): ").lower().strip()
        if not fs_choice:
            fs_choice = "xfs"

        if fs_choice not in ["xfs", "ext4", "ext3", "ext2"]:
            print("Invalid filesystem choice. Using xfs instead.")
            fs_choice = "xfs"

        print(f"\nWARNING: Formatting {device_path} will erase all data on it.")
        if mount_point:
            print(f"WARNING: {device_path} is currently mounted at {mount_point}. It will be unmounted.")
        if device_type == "disk":
            print(f"WARNING: A new partition ({device_path}1) will be created and formatted as {fs_choice}.")
        
        confirmation = input("Are you sure you want to continue? (yes/no): ").lower().strip()

        if confirmation == "yes":
            if mount_point:
                print(f"Unmounting {device_path}...")
                subprocess.run(["umount", "-l", device_path], check=True)
                print(f"{device_path} unmounted successfully.")

            path_to_format = device_path

            if device_type == "disk":
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
            subprocess.run(mkfs_command, check=True)
            print(f"Filesystem created successfully on {path_to_format}.")
        else:
            print("Formatting cancelled.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during disk formatting: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def partition_disk():
    print("\n--- Partition Disk ---")
    try:
        lsblk_output = subprocess.run(
            ["lsblk", "-P", "-o", "NAME,SIZE,TYPE"],
            capture_output=True, text=True, check=True
        ).stdout

        available_disks = []
        print("\nAvailable disks for partitioning:")
        for line in lsblk_output.strip().splitlines():
            device_info = {k: v.strip('"') for k, v in (pair.split('=', 1) for pair in shlex.split(line))}
            if device_info.get("TYPE") == "disk":
                available_disks.append(device_info)
                print(f"{len(available_disks)}. /dev/{device_info.get('NAME')} ({device_info.get('SIZE')})")

        if not available_disks:
            print("No disks found for partitioning.")
            input("Press Enter to continue...")
            return

        while True:
            try:
                choice = int(input("Select the disk to partition: ")) - 1
                if 0 <= choice < len(available_disks):
                    selected_disk_info = available_disks[choice]
                    break
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        disk_path = f"/dev/{selected_disk_info.get('NAME')}"

        parted_output = subprocess.run(
            ["parted", "-s", disk_path, "print"],
            capture_output=True, text=True, check=False
        ).stdout

        existing_partitions = []
        for line in parted_output.splitlines():
            if line.strip().startswith(tuple(str(i) for i in range(1, 10))):
                existing_partitions.append(line)
        
        if existing_partitions:
            print(f"\nWARNING: The disk {disk_path} already has existing partitions:")
            for part in existing_partitions:
                print(f"  {part}")
            confirm_continue = input("Continuing will modify the partition table. Are you sure you want to proceed? (yes/no): ").lower().strip()
            if confirm_continue != 'yes':
                print("Partitioning cancelled.")
                input("Press Enter to continue...")
                return

        last_partition_num = 0
        for line in existing_partitions:
            try:
                num = int(line.strip().split()[0])
                if num > last_partition_num:
                    last_partition_num = num
            except ValueError:
                pass

        new_partition_number = last_partition_num + 1
        new_partition_name = f"{disk_path}{new_partition_number}"
        print(f"A new partition will be created as {new_partition_name}.")

        while True:
            size_input = input("Enter the size of the new partition (e.g., 10G, 500M, or 'ALL' for remaining space): ").strip().upper()
            if size_input == "ALL":
                start_sector = "0%"
                end_sector = "100%"
                break
            elif size_input and (size_input.endswith('G') or size_input.endswith('M') or size_input.endswith('T')):
                try:
                    float(size_input[:-1])
                    start_sector = "0%"
                    end_sector = f"0%+{size_input}" 
                    break
                except ValueError:
                    print("Invalid size format. Please use G, M, or T suffix (e.g., 10G) or 'ALL'.")
            else:
                print("Invalid size format. Please use G, M, or T suffix (e.g., 10G) or 'ALL'.")

        print(f"Creating partition on {disk_path}...")
        try:
            if "Partition Table: gpt" not in parted_output:
                print(f"Creating GPT partition table on {disk_path}...")
                subprocess.run(["parted", "-s", disk_path, "mklabel", "gpt"], check=True)
                
            create_partition_cmd = ["parted", "-s", disk_path, "mkpart", "primary", start_sector, end_sector]
            subprocess.run(create_partition_cmd, check=True)
            print(f"Partition {new_partition_name} created successfully.")
            subprocess.run(["partprobe"], check=True, capture_output=True)
            time.sleep(2)
            print("New partition table:")
            subprocess.run(["lsblk", disk_path], check=True)

        except subprocess.CalledProcessError as e:
            print(f"Error creating partition: {e.stderr}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    input("Press Enter to continue...")


def setup_raid():
    """Sets up a software RAID array."""
    print("Setup RAID functionality is coming soon!")
    input("Press Enter to continue...")


def setup_lvm():
    """Sets up Logical Volume Management (LVM)."""
    print("Setup LVM functionality is coming soon!")
    input("Press Enter to continue...")
