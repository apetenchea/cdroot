---
title: First Aid Kit for Upgrading Debian
date: 2023-04-04 20:06:27
tags:
- Linux
---

On one of my workstations, I use [Debian Sid](https://wiki.debian.org/DebianUnstable). It is a rolling-release
distribution, which means that it's always up-to-date with the latest software. However, it can be unstable.
I don't mind that, because I prefer to have the latest compilers around, and I can deal with the occasional breakage.
I put together a list of recipes that I use to fix the most common problems encountered during an upgrade.

<img src="https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/first-aid-kit-for-upgrading-debian/media/first-aid-penguin.png" alt="Penguing with first aid kit" style="max-width: 40%; max-height: 40%"> 

## Upgrade procedure

Sometimes I am interested just in upgrading my kernel, but most of the time I want to upgrade the whole system.
Here's how I do it:

### System upgrade

1. Fetch the latest package information from the repositories. Updating should always be performed before upgrading.
    ```bash
   sudo apt update
    ```
2. Upgrade the packages that can be safely upgraded without removing any other packages. Replacing `upgrade` with
`full-upgrade` may remove some packages or install new ones to satisfy dependency changes. Make sure to review the
list of changes before proceeding with the upgrade.
    ```bash
   sudo apt upgrade
    ```
3. Remove packages that are no longer needed. Although an optional step, it is a good idea to keep the system clean.
    ```bash
   sudo apt autoremove
    ```
   
## Kernel upgrade

1. Update package information.
    ```bash
    sudo apt update
    ```
2. Check the available kernel versions.
    ```bash
    apt-cache search linux-image-amd64
    ```
3. Install the desired kernel version. It's recommended to install the corresponding kernel headers as well.
    If you stumble upon a meta-package, feel free to install it instead. A meta-package
    is a convenient way to bulk-install groups of applications, their libraries and documentation.
    ```bash
    sudo apt install linux-image-<kernel_version>-amd64
    sudo apt install linux-headers-<kernel_version>-amd64
    ```
4. Reboot the system to use the new kernel. **Don't remove the old one until you try it out.**
    ```bash
    sudo reboot
    ```
5. Check your kernel version.
    ```bash
    uname -r
    ```

## Common problems

### Broken packages

When you encounter a broken package, something along the lines of `E: Sub-process /usr/bin/dpkg returned an error code`,
it could mean that the package is corrupted, or that it depends on another package that is not installed. Here are two
of the things I usually try in order to fix the problem.

1. Reconfigure the affected package.
    ```bash
   sudo dpkg --configure <package_name>
    ```
   
2. Fix broken dependencies. This will attempt to fix broken dependencies and finish any interrupted package installation
or removal.
    ```bash
    sudo apt --fix-broken install
    ```
   
### Missing display manager

Sometimes, you might end up with a system that starts in TTY mode, unable to get back your graphical interface.

1. Check if there are any available display managers installed on your system.
    ```bash
   systemctl list-units --type=service | grep -E 'gdm|lightdm|sddm'
    ```
2. If there is one, start it. Also, enable it to start at boot.
    ```bash
    sudo systemctl start <display_manager>
    sudo systemctl enable <display_manager>
     ```
3. If there is none, install one. I prefer *LightDM*, but feel free to choose whatever suits you.
   After installation, make sure it is your default display manager. The file `/etc/X11/default-display-manager`
   should contain the path `/usr/sbin/lightdm` (or the path of your preferred display manager).
    ```bash
    sudo apt install lightdm
    ```
4. Reboot the system.
    ```bash
    sudo reboot
    ```

### Missing desktop environment

1. If your desktop environment is gone, install one. I prefer *xfce4*, but the steps should be very similar, regardless of what you choose to install.
    ```bash
    sudo apt update
    sudo apt install xfce4
    ```
2. Your display manager should allow you to select the desktop environment you want to use. If it doesn't, you can set it manually by adding
the following line to `~/.xinitrc`. If you use another desktop environment, replace `startxfce4` with the command that launches it.
    ```bash
    exec startxfce4
    ``` 
3. Use the following command to launch the desktop environment manually.
    ```bash
    startx
    ```

#### Related problems

1. Sometimes, in order for your desktop environment to work, you have to install missing software. For example,
    when trying to start Xfce for the first time, I got the following error message: `Failed to execute child process “dbus-launch”`.
    To resolve this issue, I had to install the `dbus-x11` package.
    ```bash
    sudo apt install dbus-x11
    ```
2. The login screen got stuck after entering my username and password. I had to switch to a TTY (`Ctrl` + `Alt` + `F1` ... up to `F6`),
and remove the `Xauthority` file, which turned out to have the wrong file permissions. After that, I was able to log in normally.
    ```bash
    rm ~/.Xauthority
    ```
3. If you're stuck, open a TTY and check the logs. Use `less` to navigate the log files, as they may be very long.
   `:q` closes the file, `:G` takes you to the end of it, and `/<pattern>` is used for searching.
   - `/var/log/Xorg.0.log` for Xorg related issues
   - `/var/log/syslog` for system-related issues
   - `/var/log/auth.log` for authentication-related issues

### No internet

1. Check the status of your network interfaces. Look for a network interface that is marked _UP_.
    ```bash
    ip addr show
    ```
2. If all interfaces are _DOWN_, pick the one you want to bring back up. Common names for wired connections start with `eth` or `enp`.
    For wireless, they start with `wl`. I find ethernet easier to set up in such situations, but for that make sure
    your ethernet cable is plugged in. Replace `<interface>` with the name of the chosen network interface.
    ```bash
     sudo ip link set <interface> up
    ```
3. Configure the network interface.
    ```bash
    sudo dhclient <interface>
    ```
4. In order to make changes persistent across reboots, add the following line to `/etc/network/interfaces`.
    ```bash
    auto <interface>
    iface <interface> inet dhcp
    ```
5. Restart networking services.
    ```bash
    sudo systemctl restart networking
    ```
6. Test it. `8.8.8.8` is the primary DNS server for Google DNS.
    ```bash
    ping 8.8.8.8
    ```

### Missing firmware

1. Often enough, the system might be unable to find the necessary firmware, especially for Realtek network cards. In this particular case,
   the following fixed it for me.
    ```bash
    sudo apt install firmware-iwlwifi
    ```
2. Be aware that such packages usually come from *non-free* repositories, which you might have to enable in your `/etc/apt/sources.list`.

## Other problems

### Incompatible modules when upgrading the kernel

When upgrading to 6.1.0-7-amd64, I encountered a problem with the `aufs` module. It was the default
storage driver used for managing images and layers on Docker. The module included a `BUILD_EXCLUSIVE` directive which
did not match my new `kernel/arch/config`. Docker [recommends](https://docs.docker.com/storage/storagedriver/aufs-driver/)
migrating to the `overlay2` storage driver. Here's how I did it:
1. Stop the Docker service.
    ```bash
    sudo systemctl stop docker
    ```
2. Make sure the `aufs` module is not in use. Unload it using the following command:
   ```bash
   sudo rmmod aufs
   ```
3. Remove related packages.
    ```bash
    sudo apt remove aufs-dkms aufs-tools
    ```
4. Switch to OverlayFS by editing the `/etc/docker/daemon.json` file. Add the following line:
    ```json
   {
       "storage-driver": "overlay2"
   }
    ```
5. Start the Docker service.
    ```bash
    sudo systemctl start docker
    ``` 

## Closing thoughts
Never be afraid of upgrading your system. Breakages happen, and they're not the end of the world. It's not your fault, and it's not the fault of the developers.
It's just a part of the process. Eventually, as the world moves on, an upgrade is unavoidable. The important thing is to learn from the experience.
