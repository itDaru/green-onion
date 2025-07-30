#!/bin/bash
set -e #crash on error
SKIP_TMUX=false


# detect --no-tmux flag
for arg in "$@"; do
  if [ "$arg" == "--no-tmux" ]; then
    SKIP_TMUX=true
    break
  fi
done

# --- Multiplexor Check Start ---
# check multiplexor and install it if not present
if [ "$SKIP_TMUX" = false ]; then
    if ! dnf list installed tmux &> /dev/null; then
        echo "tmux no encontrado. Instalando tmux..."
        dnf install -y tmux
        echo "tmux instalado exitosamente."
    fi

# check if running inside a multiplexor session
    if [ -z "$TMUX" ] && [ -z "$STY" ]; then
        echo "Detectado que el script no se ejecuta en una sesión de multiplexor (tmux/screen)."
        echo "Relanzando el script dentro de una sesión de tmux llamada 'rocky_prep'."
        echo "Si la conexión SSH se pierde, reconéctese y use el siguiente comando para continuar."
        echo "    tmux attach"
        echo "o"
        echo "    tmux attach -t rocky_prep"
        echo ""
        exec tmux new-session -s rocky_prep "$0" "$@" # launch new tmux session
        echo "Error: Unexpected execution path after exec tmux new-session."
        exit 1 # exit if exec fails
    fi
else
    echo "Modo sin tmux (--no-tmux) activado. Omitiendo instalación y verificación de multiplexor."
fi
# --- Multiplexor Check End ---

# --- Script Start ---
echo "Script de Preparación de Sistema Rocky Linux para Repositorios Inmutables"
echo ""
echo "Este script automatiza la configuración inicial de un sistema Rocky Linux"
echo "para ser utilizado como repositorio inmutable. Las tareas que realiza incluyen:"
echo ""
echo "1. Configuración de una dirección IP estática."
echo "2. Instalación y configuración del servicio SSH."
echo "3. Creación de un usuario de servicio específico (veeamsvc)."
echo "4. [PENDIENTE] Conexión a sistemas de almacenamiento remoto (NFS, iSCSI, SMB)."
echo "5. Montaje de discos utilizando LVM (Logical Volume Management)."
echo ""
echo "Este script está diseñado para ser ejecutado con privilegios de superusuario (root)."
echo "Se recomienda revisar y adaptar las variables y configuraciones según el entorno específico."

# Ask before proceeding
read -p "Continuar? (Y/n): " confirm
if [[ "$confirm" =~ ^[Nn]$ ]]; then
    echo "Operación cancelada por el usuario."
    exit 1
fi
echo ""
echo "Iniciando la configuración..."
echo ""

# Hostname Configuration
echo ""
read -p "¿Cambiar el nombre del servidor (hostname)? (y/N): " change_hostname_confirm
if [[ "$change_hostname_confirm" =~ ^[Yy]$ ]]; then
    echo "Configurando hostname..."
    read -p "Introduce el nuevo hostname: " new_hostname

    if [ -z "$new_hostname" ]; then
        echo "Nombre de hostname vacío. Omitiendo cambio."
    else
        echo "Cambiando hostname a '$new_hostname'..."
        hostnamectl set-hostname "$new_hostname"
        if [ $? -ne 0 ]; then
            echo "Error: Falló al cambiar el hostname con hostnamectl."
        else
            echo "Hostname cambiado a '$new_hostname'."
            echo "Nota: El cambio de hostname puede no reflejarse inmediatamente en la shell actual."
        fi
    fi
else
    echo "Cambio de hostname omitido."
fi


# Static IP Configuration
echo "Configurando dirección IP estática..."
ip link show | awk -F': ' '$0 !~ "lo:" {print $2}'
read -p "Introduce el nombre de la interfaz de red a configurar (ej: eth0, ens192): " interface
echo "Interfaz seleccionada: $interface"
read -p "Introduce la dirección IP estática (ej: 10.0.1.10): " ip_address
read -p "Introduce la máscara de subred (ej: 255.255.255.0): " subnet_mask
read -p "Introduce la puerta de enlace (ej: 10.0.1.1): " gateway
read -p "Introduce el DNS (ej: 10.0.1.100,1.0.1.99): " dns_servers

IFS='.' read -r -a octets <<< "$subnet_mask"
mask_binary=""
for octet in "${octets[@]}"; do
    mask_binary+=$(printf "%08d" $(echo "obase=2; $octet" | bc))
done
prefix_length=$(echo "$mask_binary" | grep -o '1' | wc -l)
dns_servers_spaced=$(echo "$dns_servers" | sed 's/,/ /g')

echo "Aplicando configuración..."
nmcli connection modify "$interface" \
    ipv4.method manual \
    ipv4.addresses "$ip_address/$prefix_length" \
    ipv4.gateway "$gateway" \
    ipv4.dns "$dns_servers_spaced"

nmcli connection up "$interface"

echo "Configuración de red aplicada."
echo ""

# Connectivity Tests
read -p "¿Realizar test de red (ping y nslookup)? (y/N): " test_confirm
if [[ "$test_confirm" =~ ^[Yy]$ ]]; then
    echo "Realizando tests de red..."

# Ping Test
    while true; do
        read -p "Introduce la IP para el test de ping (por defecto: 1.1.1.1): " ping_target
        ping_target=${ping_target:-1.1.1.1}
        echo "Realizando ping a $ping_target..."
        if ping -c 4 "$ping_target"; then
            echo "Ping a $ping_target exitoso."
            break
        else
            echo "Ping a $ping_target fallido."
            read -p "¿Qué desea hacer? (r: Reintentar, e: Salir del script): " action
            if [[ "$action" =~ ^[Ee]$ ]]; then
                echo "Saliendo del script por fallo en ping."
                exit 1
            elif [[ "$action" =~ ^[Rr]$ ]]; then
                echo "Reintentando ping..."
                continue
            else
                echo "Opción no válida. Reintentando ping por defecto."
                continue
            fi
        fi
    done

# Nslookup Test
    while true; do
        read -p "Introduce el dominio para el test de nslookup (por defecto: rockylinux.org): " nslookup_target
        nslookup_target=${nslookup_target:-rockylinux.org}
        echo "Realizando nslookup para $nslookup_target..."
        if nslookup "$nslookup_target"; then
            echo "Nslookup para $nslookup_target exitoso."
            sleep 2
            break
        else
            echo "Nslookup para $nslookup_target fallido."
            read -p "¿Qué desea hacer? (r: Reintentar, e: Salir del script): " action
            if [[ "$action" =~ ^[Ee]$ ]]; then
                echo "Saliendo del script por fallo en nslookup."
                exit 1
            elif [[ "$action" =~ ^[Rr]$ ]]; then
                echo "Reintentando nslookup..."
                continue
            else
                echo "Opción no válida. Reintentando nslookup por defecto."
                continue
            fi
        fi
    done

    echo "Tests de red completados."
else
    echo "Tests de red omitidos."
fi

# SSH Configuration
echo ""
read -p "¿Configurar e instalar SSH? (y/N): " ssh_confirm
if [[ "$ssh_confirm" =~ ^[Yy]$ ]]; then
    echo "Configurando SSH..."

    # Install openssh-server if not installed
    if ! dnf list installed openssh-server &> /dev/null; then
        echo "Instalando openssh-server..."
        dnf install -y openssh-server
        if [ $? -ne 0 ]; then
            echo "Error: Falló la instalación de openssh-server."
            exit 1
        fi
    else
        echo "openssh-server ya está instalado."
    fi

    # SSH Configuration
    SSH_CONFIG="/etc/ssh/sshd_config"
    SSH_CONFIG_BACKUP="${SSH_CONFIG}.bak.$(date +%Y%m%d_%H%M%S)"

    echo "Realizando copia de seguridad de $SSH_CONFIG a $SSH_CONFIG_BACKUP"
    cp "$SSH_CONFIG" "$SSH_CONFIG_BACKUP"

    echo "Aplicando configuraciones de seguridad a $SSH_CONFIG..."

    # Disable root login
    sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' "$SSH_CONFIG"
    if ! grep -q "^PermitRootLogin no" "$SSH_CONFIG"; then
        echo "PermitRootLogin no" >> "$SSH_CONFIG"
    fi

    # Make sure PasswordAuthentication is enabled
    sed -i 's/^PasswordAuthentication.*/PasswordAuthentication yes/' "$SSH_CONFIG"
    if ! grep -q "^PasswordAuthentication yes" "$SSH_CONFIG"; then
         if grep -q "^#PasswordAuthentication yes" "$SSH_CONFIG"; then
             sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication yes/' "$SSH_CONFIG"
         else
             echo "PasswordAuthentication yes" >> "$SSH_CONFIG"
         fi
    fi

    # Disable Hostbased Authentication
    sed -i 's/^HostbasedAuthentication.*/HostbasedAuthentication no/' "$SSH_CONFIG"
    if ! grep -q "^HostbasedAuthentication no" "$SSH_CONFIG"; then
        echo "HostbasedAuthentication no" >> "$SSH_CONFIG"
    fi

    # Disable Rhost Authentication
    sed -i 's/^IgnoreRhosts.*/IgnoreRhosts yes/' "$SSH_CONFIG"
     if ! grep -q "^IgnoreRhosts yes" "$SSH_CONFIG"; then
        echo "IgnoreRhosts yes" >> "$SSH_CONFIG"
    fi

    # Disable GSSAPI Authentication (if not needed)
    # sed -i 's/^GSSAPIAuthentication.*/GSSAPIAuthentication no/' "$SSH_CONFIG"
    # if ! grep -q "^GSSAPIAuthentication no" "$SSH_CONFIG"; then
    #     echo "GSSAPIAuthentication no" >> "$SSH_CONFIG"
    # fi

    # Disable X11 Forwarding
    sed -i 's/^X11Forwarding.*/X11Forwarding no/' "$SSH_CONFIG"
    if ! grep -q "^X11Forwarding no" "$SSH_CONFIG"; then
        echo "X11Forwarding no" >> "$SSH_CONFIG"
    fi

    # Restart SSH service 
    echo "Reiniciando el servicio SSH..."
    systemctl enable --now sshd
    systemctl restart sshd
    echo "Servicio SSH configurado y reiniciado."

else
    echo "Configuración de SSH omitida."
fi


# Service User Configuration
echo ""
read -p "¿Crear usuario de servicio? (y/N): " create_user_confirm
if [[ "$create_user_confirm" =~ ^[Yy]$ ]]; then
    echo "Configurando usuario de servicio..."

    read -p "Introduce el nombre del usuario de servicio (por defecto: veeamsvc): " service_username
    service_username=${service_username:-veeamsvc}

    if id "$service_username" &>/dev/null; then
        echo "El usuario '$service_username' ya existe. Omitiendo creación."
    else
        echo "Creando usuario '$service_username'..."
        useradd "$service_username"
        if [ $? -ne 0 ]; then
            echo "Error: Falló la creación del usuario '$service_username'."
            exit 1
        fi

        # Random Password Generation
        echo "Generando contraseña para '$service_username'..."
        generated_password=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 12)
        echo "$generated_password" | passwd --stdin "$service_username"
        if [ $? -ne 0 ]; then
            echo "Error: Falló la configuración de la contraseña para '$service_username'."
        else
            echo "Contraseña generada para '$service_username': "
            echo ""
            echo "    $generated_password"
            echo ""
            echo "¡GUARDE ESTA CONTRASEÑA EN UN LUGAR SEGURO!"
        fi
    fi

    # Define the default SSH public key here.
    default_ssh_key=""

    # Public SSH Key Configuration
    read -p "¿Configurar llave SSH pública para '$service_username'? (y/N): " config_ssh_key_confirm
    if [[ "$config_ssh_key_confirm" =~ ^[Yy]$ ]]; then
        echo "Por favor, pegue la llave SSH pública (doble enter para terminar):"
        ssh_key_input=""
        while IFS= read -r line; do
            if [ -z "$line" ]; then
                break
            fi
            ssh_key_input+="$line"$'\n'
        done

        # Use default key if input is empty
        ssh_key_to_use="$ssh_key_input"
        if [ -z "$ssh_key_input" ]; then
            ssh_key_to_use="$default_ssh_key"
        fi

        if [ -n "$ssh_key_to_use" ]; then
            user_home=$(eval echo "~$service_username")
            ssh_dir="$user_home/.ssh"
            authorized_keys_file="$ssh_dir/authorized_keys"

            echo "Configurando llave SSH para '$service_username' en $authorized_keys_file..."

            # Create .ssh directory if it doesn't exist and set permissions
            if [ ! -d "$ssh_dir" ]; then
                mkdir "$ssh_dir"
                chmod 700 "$ssh_dir"
                chown "$service_username":"$service_username" "$ssh_dir"
            fi

            # Add the SSH key to authorized_keys
            echo "$ssh_key_to_use" | tee -a "$authorized_keys_file" > /dev/null
            chmod 600 "$authorized_keys_file"
            chown "$service_username":"$service_username" "$authorized_keys_file"

            echo "Llave SSH pública agregada para '$service_username'."
        else
            echo "No se proporcionó ninguna llave SSH y la llave por defecto está vacía. Omitiendo configuración de llave."
        fi
    else
        echo "Configuración de llave SSH omitida."
    fi

    # Add user to sudoers group
    echo "Agregando usuario '$service_username' al grupo de sudoers..."
    # Check if 'wheel' group exists
    if getent group wheel > /dev/null; then
        usermod -aG wheel "$service_username"
        if [ $? -ne 0 ]; then
            echo "Error: Falló al agregar '$service_username' al grupo 'wheel'."
        else
            echo "'$service_username' agregado al grupo 'wheel'."
        fi
    # Check if 'sudo' group exists
    elif getent group sudo > /dev/null; then
         usermod -aG sudo "$service_username"
         if [ $? -ne 0 ]; then
            echo "Error: Falló al agregar '$service_username' al grupo 'sudo'."
        else
            echo "'$service_username' agregado al grupo 'sudo'."
        fi
    else
        echo "Advertencia: No se encontraron los grupos 'wheel' ni 'sudo'. No se pudo agregar al usuario a un grupo de sudoers."
    fi

    echo "Configuración de usuario de servicio completada."

else
    echo "Creación de usuario de servicio omitida."
fi

# [PENDING] Remote Storage Configuration
echo ""
read -p "¿Configurar Almacenamiento Remoto (NFS, iSCSI, SMB)? (y/N): " storage_confirm
if [[ "$storage_confirm" =~ ^[Yy]$ ]]; then
    echo "Configuración de Almacenamiento Remoto - NOTA IMPORTANTE:"
    echo "Esta parte del script aún no está automatizada."
    echo "Deberá realizar la configuración manualmente."
    echo ""
    read -p "¿Desea abrir una shell para configurar manualmente? (y/N): " open_shell_confirm
    if [[ "$open_shell_confirm" =~ ^[Yy]$ ]]; then
        echo "Abriendo una nueva shell. Por favor, configure el almacenamiento remoto manualmente."
        echo "Escriba 'exit' para volver al script (si es posible) o terminar."
        bash
        echo "Volviendo al script principal..."
    else
        echo "Configuración manual de almacenamiento omitida."
        echo "Saliendo del script."
        exit 1
    fi
else
    echo "Configuración de Almacenamiento Remoto omitida."
fi

# Disk and LVM Configuration
echo ""
read -p "¿Configurar Discos y LVM? (y/N): " disk_config_confirm
if [[ "$disk_config_confirm" =~ ^[Yy]$ ]]; then
    echo "Configurando Discos..."

    echo "Discos disponibles:"
    lsblk -dno NAME,SIZE,TYPE | grep disk
    echo ""

    read -p "¿Implementar LVM? (y/N): " use_lvm_confirm

    if [[ "$use_lvm_confirm" =~ ^[Yy]$ ]]; then
        echo "Configurando LVM..."

        if ! dnf list installed lvm2 &> /dev/null || ! dnf list installed xfsprogs &> /dev/null; then
            echo "Instalando lvm2 y xfsprogs..."
            dnf install -y lvm2 xfsprogs
            if [ $? -ne 0 ]; then
                echo "Error: Falló la instalación de lvm2 o xfsprogs."
                exit 1
            fi
        else
            echo "lvm2 y xfsprogs ya están instalados."
        fi

        pv_list=()
        echo "Introduce los nombres de los discos a usar como Volúmenes Físicos (ej: sdb, sdc). Presiona Enter sin escribir nada para terminar."
        while true; do
            read -p "Disco para PV: " disk_name
            if [ -z "$disk_name" ]; then
                break
            fi
            if [ -b "/dev/$disk_name" ]; then
                pv_list+=("/dev/$disk_name")
                echo "Añadido /dev/$disk_name a la lista de PVs."
            else
                echo "Advertencia: /dev/$disk_name no parece ser un dispositivo de bloque válido. Inténtalo de nuevo."
            fi
        done

        if [ ${#pv_list[@]} -eq 0 ]; then
            echo "No se seleccionaron discos para PVs. Saliendo de la configuración de discos."
            exit 1
        fi

        echo "Creando Volúmenes Físicos en: ${pv_list[@]}"
        pvcreate "${pv_list[@]}"
        if [ $? -ne 0 ]; then
            echo "Error: Falló la creación de Volúmenes Físicos."
            exit 1
        fi

        # Create Volume Group (VG)
        vg_name="vhr-vg"
        echo "Creando Volume Group '$vg_name'..."
        vgcreate "$vg_name" "${pv_list[@]}"
        if [ $? -ne 0 ]; then
            echo "Error: Falló la creación del Volume Group '$vg_name'."
            exit 1
        fi

        # Create Logical Volume (LV)
        lv_name="backup-lv"
        echo "Creando Logical Volume '$lv_name' en '$vg_name' (usando todo el espacio disponible)..."
        lvcreate -l 100%FREE -n "$lv_name" "$vg_name"
        if [ $? -ne 0 ]; then
            echo "Error: Falló la creación del Logical Volume '$lv_name'."
            exit 1
        fi

        # Get the path of the Logical Volume
        lv_path=$(lvs --noheadings -o lv_path "$vg_name/$lv_name" | sed -e 's/^[ \t]*//' -e 's/[ \t]*$//')

        if [ -z "$lv_path" ]; then
            echo "Error: No se pudo obtener la ruta del Logical Volume '$vg_name/$lv_name'."
            exit 1
        fi

        echo "Ruta del Logical Volume detectada: $lv_path"

        # Format LV with XFS
        echo "Formateando '$lv_path' con XFS..."
        mkfs.xfs "$lv_path"
        if [ $? -ne 0 ]; then
            echo "Error: Falló el formateo de '$lv_path'."
            exit 1
        fi

        # Create mount point
        mount_point="/data"
        echo "Creando directorio de montaje '$mount_point'..."
        mkdir -p "$mount_point"

        # Mount LV
        echo "Montando '$lv_path' en '$mount_point'..."
        mount "$lv_path" "$mount_point"
        if [ $? -ne 0 ]; then
            echo "Error: Falló el montaje de '$lv_path'."
            exit 1
        fi

        echo "Asignando permisos en '$mount_point' al usuario '$service_username'..."
        chown -R "$service_username":"$service_username" "$mount_point"
        if [ $? -ne 0 ]; then
            echo "Advertencia: Falló al asignar permisos en '$mount_point' al usuario '$service_username'."
        else
            echo "Permisos de '$mount_point' asignados a '$service_username'."
        fi

        # Add to /etc/fstab
        echo "Agregando entrada a /etc/fstab..."
        lv_uuid=$(blkid -s UUID -o value "$lv_path")
        if [ -z "$lv_uuid" ]; then
             echo "Error: No se pudo obtener el UUID para '$lv_path'. No se agregará a fstab."
        else
            echo "UUID=$lv_uuid $mount_point xfs defaults,nofail 0 0" | tee -a /etc/fstab > /dev/null
            echo "Entrada agregada a /etc/fstab."
        fi

        echo "Configuración de LVM completada."

    else # non-LVM configuration
        echo "Configurando disco sin LVM..."
        if ! dnf list installed xfsprogs &> /dev/null; then
            echo "Instalando xfsprogs..."
            dnf install -y xfsprogs
            if [ $? -ne 0 ]; then
                echo "Error: Falló la instalación de xfsprogs."
                exit 1
            fi
        else
            echo "xfsprogs ya está instalado."
        fi

        # Ask for disk name
        read -p "Introduce el nombre del disco a usar (ej: sdb): " disk_name
        disk_path="/dev/$disk_name"
        if [ ! -b "$disk_path" ]; then
            echo "Error: '$disk_path' no es un dispositivo de bloque válido. Saliendo."
            exit 1
        fi
        # Format disk with XFS
        echo "Formateando '$disk_path' con XFS..."
        mkfs.xfs "$disk_path"
        if [ $? -ne 0 ]; then
            echo "Error: Falló el formateo de '$disk_path'."
            exit 1
        fi
        # Create mount point
        mount_point="/data"
        echo "Creando directorio de montaje '$mount_point'..."
        mkdir -p "$mount_point"

        # Mount disk
        echo "Montando '$disk_path' en '$mount_point'..."
        mount "$disk_path" "$mount_point"
        if [ $? -ne 0 ]; then
            echo "Error: Falló el montaje de '$disk_path'."
            exit 1
        fi

        echo "Asignando permisos en '$mount_point' al usuario '$service_username'..."
        chown -R "$service_username":"$service_username" "$mount_point"
        if [ $? -ne 0 ]; then
            echo "Advertencia: Falló al asignar permisos en '$mount_point' al usuario '$service_username'."
        else
            echo "Permisos en '$mount_point' asignados a '$service_username'."
        fi

        # Add to /etc/fstab
        echo "Agregando entrada a /etc/fstab..."
        disk_uuid=$(blkid -s UUID -o value "$disk_path")
         if [ -z "$disk_uuid" ]; then
             echo "Error: No se pudo obtener el UUID para '$disk_path'. No se agregará a fstab."
        else
            echo "UUID=$disk_uuid $mount_point xfs defaults,nofail 0 0" | tee -a /etc/fstab > /dev/null
            echo "Entrada agregada a /etc/fstab."
        fi

        echo "Configuración de disco completada."
    fi

else
    echo "Configuración de Discos y LVM omitida."
fi

echo ""
echo "Script de Preparación de Sistema Finalizado."

# --- Cleaning Start ---
echo "Limpiando sistema (desinstalando tmux)..."
dnf remove -y tmux
if [ $? -ne 0 ]; then
    echo "Advertencia: Falló la desinstalación de tmux."
else
    echo "tmux desinstalado exitosamente."
fi
# --- Cleaning End ---

echo "Proceso de preparación completado."
echo "Por favor, ingresa a la consola de Veeam Backup & Replication y configura el repositorio inmutable."
echo "Gracias por usar este script. ¡Hasta luego!"
exit 0
