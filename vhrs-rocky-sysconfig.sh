#!/bin/bash

# --- Inicio de la verificación de Multiplexor ---
# Comprueba si el script ya se está ejecutando dentro de tmux o screen
if [ -z "$TMUX" ] && [ -z "$STY" ]; then
    echo "Detectado que el script no se ejecuta en una sesión de multiplexor (tmux/screen)."
    echo "Relanzando el script dentro de una sesión de tmux llamada 'rocky_prep'."
    echo "Si la conexión SSH se pierde, reconéctese y use 'tmux attach -t rocky_prep' para continuar."
    echo ""
    # Ejecuta el script actual dentro de una nueva sesión de tmux
    # El 'exec' reemplaza el proceso actual del script con el comando tmux
    exec tmux new-session -s rocky_prep "$0" "$@"
    # Si tmux falla (por ejemplo, no está instalado), el script continuará aquí.
    # Puedes añadir un mensaje de error o salir si prefieres que sea un requisito.
    if [ $? -ne 0 ]; then
        echo "Error: Falló al iniciar la sesión de tmux. Asegúrese de que tmux esté instalado."
        # Opcional: exit 1
    fi
fi
# --- Fin de la verificación de Multiplexor ---


echo "Script de Preparación de Sistema Rocky Linux para Repositorios Inmutables"
echo ""
echo "Este script automatiza la configuración inicial de un sistema Rocky Linux"
echo "para ser utilizado como repositorio inmutable. Las tareas que realiza incluyen:"
echo ""
echo "1. Configuración de una dirección IP estática."
echo "2. Instalación y configuración del servicio SSH."
echo "3. Creación de un usuario de servicio específico (veeamsvc)."
echo "4. Conexión a sistemas de almacenamiento remoto (NFS, iSCSI, SMB)."
echo "5. Montaje de discos utilizando LVM (Logical Volume Management)."
echo ""
echo "Este script está diseñado para ser ejecutado con privilegios de superusuario (root)."
echo "Se recomienda revisar y adaptar las variables y configuraciones según el entorno específico."


# Init
read -p "Continuar? (Y/n): " confirm
if [[ "$confirm" =~ ^[Nn]$ ]]; then
    echo "Operación cancelada por el usuario."
    exit 1
fi
echo ""
echo "Iniciando la configuración..."
echo ""

# Configuración de Hostname
echo ""
read -p "¿Cambiar el nombre del servidor (hostname)? (Y/n): " change_hostname_confirm
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


# Configuración de IP estática
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

# Replace commas with spaces in DNS servers string
dns_servers_spaced=$(echo "$dns_servers" | sed 's/,/ /g')

# Configure the interface using nmcli
echo "Aplicando configuración..."
nmcli connection modify "$interface" \
    ipv4.method manual \
    ipv4.addresses "$ip_address/$prefix_length" \
    ipv4.gateway "$gateway" \
    ipv4.dns "$dns_servers_spaced"

nmcli connection up "$interface"

echo "Configuración de red aplicada."

echo ""
read -p "¿Realizar test de red (ping y nslookup)? (Y/n): " test_confirm
if [[ "$test_confirm" =~ ^[Yy]$ ]]; then
    echo "Realizando tests de red..."

    # Test de ping con reintento/salida
    while true; do
        read -p "Introduce la IP para el test de ping (por defecto: 1.1.1.1): " ping_target
        ping_target=${ping_target:-1.1.1.1}
        echo "Realizando ping a $ping_target..."
        if ping -c 4 "$ping_target"; then
            echo "Ping a $ping_target exitoso."
            break # Salir del bucle de ping si es exitoso
        else
            echo "Ping a $ping_target fallido."
            read -p "¿Qué desea hacer? (r: Reintentar, e: Salir del script): " action
            if [[ "$action" =~ ^[Ee]$ ]]; then
                echo "Saliendo del script por fallo en ping."
                exit 1 # Salir del script
            elif [[ "$action" =~ ^[Rr]$ ]]; then
                echo "Reintentando ping..."
                continue # Continuar el bucle
            else
                echo "Opción no válida. Reintentando ping por defecto."
                continue # Por defecto, reintentar
            fi
        fi
    done

    # Test de nslookup con reintento/salida
    while true; do
        read -p "Introduce el dominio para el test de nslookup (por defecto: rockylinux.org): " nslookup_target
        nslookup_target=${nslookup_target:-rockylinux.org}
        echo "Realizando nslookup para $nslookup_target..."
        if nslookup "$nslookup_target"; then
            echo "Nslookup para $nslookup_target exitoso."
            break # Salir del bucle de nslookup si es exitoso
        else
            echo "Nslookup para $nslookup_target fallido."
            read -p "¿Qué desea hacer? (r: Reintentar, e: Salir del script): " action
            if [[ "$action" =~ ^[Ee]$ ]]; then
                echo "Saliendo del script por fallo en nslookup."
                exit 1 # Salir del script
            elif [[ "$action" =~ ^[Rr]$ ]]; then
                echo "Reintentando nslookup..."
                continue # Continuar el bucle
            else
                echo "Opción no válida. Reintentando nslookup por defecto."
                continue # Por defecto, reintentar
            fi
        fi
    done

    echo "Tests de red completados."
else
    echo "Tests de red omitidos."
fi

# Configuración de SSH
echo ""
read -p "¿Configurar e instalar SSH? (Y/n): " ssh_confirm
if [[ "$ssh_confirm" =~ ^[Yy]$ ]]; then
    echo "Configurando SSH..."

    # Instalar OpenSSH Server si no está instalado
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

    # Hardenizar configuración SSH
    SSH_CONFIG="/etc/ssh/sshd_config"
    SSH_CONFIG_BACKUP="${SSH_CONFIG}.bak.$(date +%Y%m%d_%H%M%S)"

    echo "Realizando copia de seguridad de $SSH_CONFIG a $SSH_CONFIG_BACKUP"
    cp "$SSH_CONFIG" "$SSH_CONFIG_BACKUP"

    echo "Aplicando configuraciones de seguridad a $SSH_CONFIG..."

    # Deshabilitar login de root por SSH
    sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' "$SSH_CONFIG"
    if ! grep -q "^PermitRootLogin no" "$SSH_CONFIG"; then
        echo "PermitRootLogin no" >> "$SSH_CONFIG"
    fi

    # Asegurar que PasswordAuthentication está habilitado (necesario para veeamsvc)
    sed -i 's/^PasswordAuthentication.*/PasswordAuthentication yes/' "$SSH_CONFIG"
    if ! grep -q "^PasswordAuthentication yes" "$SSH_CONFIG"; then
         # Add it if not present or commented out
         if grep -q "^#PasswordAuthentication yes" "$SSH_CONFIG"; then
             sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication yes/' "$SSH_CONFIG"
         else
             echo "PasswordAuthentication yes" >> "$SSH_CONFIG"
         fi
    fi

    # Deshabilitar autenticación basada en host
    sed -i 's/^HostbasedAuthentication.*/HostbasedAuthentication no/' "$SSH_CONFIG"
    if ! grep -q "^HostbasedAuthentication no" "$SSH_CONFIG"; then
        echo "HostbasedAuthentication no" >> "$SSH_CONFIG"
    fi

    # Deshabilitar autenticación Rhosts
    sed -i 's/^IgnoreRhosts.*/IgnoreRhosts yes/' "$SSH_CONFIG"
     if ! grep -q "^IgnoreRhosts yes" "$SSH_CONFIG"; then
        echo "IgnoreRhosts yes" >> "$SSH_CONFIG"
    fi

    # Deshabilitar autenticación GSSAPI (opcional, puede ser necesario en algunos entornos)
    # sed -i 's/^GSSAPIAuthentication.*/GSSAPIAuthentication no/' "$SSH_CONFIG"
    # if ! grep -q "^GSSAPIAuthentication no" "$SSH_CONFIG"; then
    #     echo "GSSAPIAuthentication no" >> "$SSH_CONFIG"
    # fi

    # Deshabilitar X11 Forwarding (si no es necesario)
    sed -i 's/^X11Forwarding.*/X11Forwarding no/' "$SSH_CONFIG"
    if ! grep -q "^X11Forwarding no" "$SSH_CONFIG"; then
        echo "X11Forwarding no" >> "$SSH_CONFIG"
    fi

    # Reiniciar el servicio SSH para aplicar los cambios
    echo "Reiniciando el servicio SSH..."
    systemctl enable --now sshd
    systemctl restart sshd
    echo "Servicio SSH configurado y reiniciado."

else
    echo "Configuración de SSH omitida."
fi


# Creación de Usuario de Servicio
echo ""
read -p "¿Crear usuario de servicio? (Y/n): " create_user_confirm
if [[ "$create_user_confirm" =~ ^[Yy]$ ]]; then
    echo "Configurando usuario de servicio..."

    read -p "Introduce el nombre del usuario de servicio (por defecto: veeamsvc): " service_username
    service_username=${service_username:-veeamsvc}

    # Verificar si el usuario ya existe
    if id "$service_username" &>/dev/null; then
        echo "El usuario '$service_username' ya existe. Omitiendo creación."
    else
        echo "Creando usuario '$service_username'..."
        useradd "$service_username"
        if [ $? -ne 0 ]; then
            echo "Error: Falló la creación del usuario '$service_username'."
            exit 1
        fi

        # Generar y configurar contraseña aleatoria
        echo "Generando contraseña para '$service_username'..."
        generated_password=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 12)
        echo "$generated_password" | passwd --stdin "$service_username"
        if [ $? -ne 0 ]; then
            echo "Error: Falló la configuración de la contraseña para '$service_username'."
            # Considerar si salir o continuar
        else
            echo "Contraseña generada para '$service_username': "
            echo ""
            echo "    $generated_password"
            echo ""
            echo "¡GUARDE ESTA CONTRASEÑA EN UN LUGAR SEGURO!"
        fi
    fi

    # Define the default SSH public key here.
    # Replace this placeholder with your actual default key string.
    # Example: default_ssh_key="ssh-rsa AAAAB3Nz... user@host"
    default_ssh_key="" # <-- PUT YOUR DEFAULT KEY HERE

    # Configurar llave SSH pública
    read -p "¿Configurar llave SSH pública para '$service_username'? (Y/n): " config_ssh_key_confirm
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

            # Crear directorio .ssh si no existe y establecer permisos
            if [ ! -d "$ssh_dir" ]; then
                mkdir "$ssh_dir"
                chmod 700 "$ssh_dir"
                chown "$service_username":"$service_username" "$ssh_dir"
            fi

            # Agregar la llave al archivo authorized_keys
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

    # Agregar usuario al grupo sudo o wheel
    echo "Agregando usuario '$service_username' al grupo de sudoers..."
    # Check if 'wheel' group exists (common in RHEL/Rocky)
    if getent group wheel > /dev/null; then
        usermod -aG wheel "$service_username"
        if [ $? -ne 0 ]; then
            echo "Error: Falló al agregar '$service_username' al grupo 'wheel'."
        else
            echo "'$service_username' agregado al grupo 'wheel'."
        fi
    # Check if 'sudo' group exists (common in Debian/Ubuntu)
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

# Configuración de Almacenamiento Remoto (NFS, iSCSI, SMB)
echo ""
read -p "¿Configurar Almacenamiento Remoto (NFS, iSCSI, SMB)? (Y/n): " storage_confirm
if [[ "$storage_confirm" =~ ^[Yy]$ ]]; then
    echo "Configuración de Almacenamiento Remoto - NOTA IMPORTANTE:"
    echo "Esta parte del script aún no está automatizada."
    echo "Deberá realizar la configuración manualmente."
    echo ""
    read -p "¿Desea abrir una shell para configurar manualmente? (Y/n): " open_shell_confirm
    if [[ "$open_shell_confirm" =~ ^[Yy]$ ]]; then
        echo "Abriendo una nueva shell. Por favor, configure el almacenamiento remoto manualmente."
        echo "Escriba 'exit' para volver al script (si es posible) o terminar."
        # Use bash without exec to return to the script after exiting the sub-shell
        bash
        echo "Volviendo al script principal..." # This line will execute after exiting the sub-shell
    else
        echo "Configuración manual de almacenamiento omitida."
        echo "Saliendo del script."
        exit 1
    fi
else
    echo "Configuración de Almacenamiento Remoto omitida."
fi

# Configuración de Discos y LVM
echo ""
read -p "¿Configurar Discos y LVM? (Y/n): " disk_config_confirm
if [[ "$disk_config_confirm" =~ ^[Yy]$ ]]; then
    echo "Configurando Discos..."

    # Listar discos disponibles
    echo "Discos disponibles:"
    lsblk -dno NAME,SIZE,TYPE | grep disk
    echo ""

    # Preguntar si usar LVM
    read -p "¿Implementar LVM? (Y/n): " use_lvm_confirm

    if [[ "$use_lvm_confirm" =~ ^[Yy]$ ]]; then
        echo "Configurando LVM..."

        # Instalar lvm2 y xfsprogs si no están instalados
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

        # Leer Volúmenes Físicos (PVs)
        pv_list=()
        echo "Introduce los nombres de los discos a usar como Volúmenes Físicos (ej: sdb, sdc). Presiona Enter sin escribir nada para terminar."
        while true; do
            read -p "Disco para PV: " disk_name
            if [ -z "$disk_name" ]; then
                break
            fi
            # Basic validation: check if it's a block device
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

        # Crear Volume Group (VG)
        vg_name="vhr-vg"
        echo "Creando Volume Group '$vg_name'..."
        vgcreate "$vg_name" "${pv_list[@]}"
        if [ $? -ne 0 ]; then
            echo "Error: Falló la creación del Volume Group '$vg_name'."
            exit 1
        fi

        # Crear Logical Volume (LV)
        lv_name="backup-lv"
        echo "Creando Logical Volume '$lv_name' en '$vg_name' (usando todo el espacio disponible)..."
        lvcreate -l 100%FREE -n "$lv_name" "$vg_name"
        if [ $? -ne 0 ]; then
            echo "Error: Falló la creación del Logical Volume '$lv_name'."
            exit 1
        fi

        # Obtener la ruta real del LV después de la creación
        lv_path=$(lvs --noheadings -o lv_path "$vg_name/$lv_name" | sed -e 's/^[ \t]*//' -e 's/[ \t]*$//')

        if [ -z "$lv_path" ]; then
            echo "Error: No se pudo obtener la ruta del Logical Volume '$vg_name/$lv_name'."
            exit 1
        fi

        echo "Ruta del Logical Volume detectada: $lv_path"

        # Formatear LV con XFS
        echo "Formateando '$lv_path' con XFS..."
        mkfs.xfs "$lv_path"
        if [ $? -ne 0 ]; then
            echo "Error: Falló el formateo de '$lv_path'."
            exit 1
        fi

        # Crear directorio de montaje
        mount_point="/data"
        echo "Creando directorio de montaje '$mount_point'..."
        mkdir -p "$mount_point"

        # Montar LV
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
            # Decide if this should be a fatal error or just a warning
        else
            echo "Permisos de '$mount_point' asignados a '$service_username'."
        fi

        # Agregar a /etc/fstab
        echo "Agregando entrada a /etc/fstab..."
        lv_uuid=$(blkid -s UUID -o value "$lv_path")
        if [ -z "$lv_uuid" ]; then
             echo "Error: No se pudo obtener el UUID para '$lv_path'. No se agregará a fstab."
        else
            echo "UUID=$lv_uuid $mount_point xfs defaults,nofail 0 0" | tee -a /etc/fstab > /dev/null
            echo "Entrada agregada a /etc/fstab."
        fi

        echo "Configuración de LVM completada."

    else # Caso no-LVM
        echo "Configurando disco sin LVM..."

        # Instalar xfsprogs si no está instalado
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

        # Preguntar qué disco usar
        read -p "Introduce el nombre del disco a usar (ej: sdb): " disk_name
        disk_path="/dev/$disk_name"

        # Basic validation
        if [ ! -b "$disk_path" ]; then
            echo "Error: '$disk_path' no es un dispositivo de bloque válido. Saliendo."
            exit 1
        fi

        # Formatear disco con XFS
        echo "Formateando '$disk_path' con XFS..."
        mkfs.xfs "$disk_path"
        if [ $? -ne 0 ]; then
            echo "Error: Falló el formateo de '$disk_path'."
            exit 1
        fi

        # Crear directorio de montaje
        mount_point="/data"
        echo "Creando directorio de montaje '$mount_point'..."
        mkdir -p "$mount_point"

        # Montar disco
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
            # Decide if this should be a fatal error or just a warning
        else
            echo "Permisos en '$mount_point' asignados a '$service_username'."
        fi

        # Agregar a /etc/fstab
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
