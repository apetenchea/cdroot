---
title: running windows in KVM
date: 2025-05-04 18:45:37
tags:
- Windows
---

I am running Debian "sid" on my laptop, but sometimes I need to test something on Windows. I don't want to dual boot,
so I decided to run Windows in a KVM virtual machine. This is me documenting the process.

## Requirements

### Virtualization support

I am using an Intel CPU with VT-x support. Most probably you have it too, but you can check it with the following command:

```bash
lscpu | grep Virtualization
```

On Intel you should get something like `Virtualization: VT-x` and on AMD you should get `Virtualization: AMD-V`.

Check that your kernel includes KVM modules:

```bash
zgrep CONFIG_KVM /boot/config-$(uname -r)
```

If you get a bunch of `CONFIG_KVM_*` lines with `=y` or `=m`, you are good to go.

### Install KVM

```bash
sudo apt update
sudo apt install \
    qemu-system-x86 \
    libvirt-daemon-system \
    virtinst \
    virt-manager \
    virt-viewer \
    ovmf \
    swtpm \
    qemu-utils \
    guestfs-tools \
    libosinfo-bin \
    tuned
```

**What you really need**
- `qemu-system-x86`, `libvirt-daemon-system`, `qemu-utils`: core virtualization.
- `ovmf`: mandatory for Win11 UEFI.
- `virtinst` (or another install method) and `virt-manager` (or another GUI): to create/manage the VM.

**What you can skip or add later**
- `virt-viewer`: only if you want a standalone SPICE/VNC client.
- `swtpm`: only if you plan to turn on Secure Boot or virtual TPM 2.0 inside the VM.
- `guestfs-tools` / `libosinfo-bin`: handy for advanced image tweaks or smoother GUI installs, but not strictly required.
- `tuned`: gives system-wide tuning profiles (e.g. “virtual-guest”) for latency or throughput, but you can tune manually without it.

### Get VirtIO drivers

These drivers enable direct (paravirtualized) access to devices and peripherals for virtual machines using them, instead
of slower, emulated ones. Go to [pve.proxmox.com](https://pve.proxmox.com/wiki/Windows_VirtIO_Drivers) or run:

```bash
wget https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso
```

### Enable libvirt service

The `libvirtd.service` is the system-wide daemon for `libvirt`, the management layer you’re using to run and control
your VMs under KVM (and other hypervisors). Basically, `libvirtd` is the background service that actually does the work
of orchestrating your virtual machines.

```bash
sudo systemctl enable libvirtd.service
```

### Reboot

Reboot your system to make sure everything is loaded correctly.

```bash
sudo reboot
```

### Optimize the host

You can use the `tuned` package to optimize your host for virtualization. It is a Linux daemon that dynamically adjusts
system settings to match your current workload, helping you squeeze out more performance or save power without manual
tweaking. 

```bash
sudo systemctl enable --now tuned
```

You can check the current profile. It usually defaults to "balanced".

```bash
sudo tuned-adm active
```

You can check the available profiles with:

```bash
sudo tuned-adm list
```

If you want to optimize for running KVM guests, you can set the profile to "virtual-guest":

```bash
sudo tuned-adm profile virtual-host
```

### Enable internet

Check the state of your default libvirt network:

```bash
sudo virsh net-list --all
```

If you leave the default network inactive, your new Windows VM will have no guests-side NIC to get an IP or route out
through your host. In that state it won’t see the Internet at all. To get internet, do the following:

```bash
sudo virsh net-start default     # start the default NAT network now
sudo virsh net-autostart default # enable it on boot
```

### Update your user permissions

#### Give your user access to libvirt

If you want to be able to use `virsh` and `virt-manager` without `sudo`, you need to add your user to the `libvirt` group:

```bash
sudo usermod -aG libvirt $USER
sudo usermod -aG libvirt-qemu $USER
```

Also, add the following line to your `~/.bashrc` file:

```bash
export LIBVIRT_DEFAULT_URI="qemu:///system"
```

If you're using a virtual Python environment and starting `virt-manager` gives you package-related errors, but works
when being ran with `sudo`, make sure that your system packages are visible to the virtual environment. You can do this
by editing the `<path-to-venv>/pyvenv.cfg` file and then re-activate the virtual environment.

```
include-system-site-packages = true
```

#### Give your user access to the images directory

By default, virtual machine disk images are stored in the `/var/lib/libvirt/images` directory. Only the root user has
access to this directory.

```bash
sudo setfacl -R -b /var/lib/libvirt/images             # remove all existing ACLs
sudo setfacl -R -m u:$USER:rwX /var/lib/libvirt/images # give your user read/write/execute access
sudo setfacl -m d:u:$USER:rwx /var/lib/libvirt/images  # give your user default read/write/execute access
getfacl /var/lib/libvirt/images                        # check the ACLs
```

### Download Windows

I downloaded the Windows 11 ISO from [microsoft.com](https://www.microsoft.com/en-us/software-download/windows11).

## Configure Virtual Hardware

### Using virt-manager

1. Open `virt-manager` and check *Edit* -> *Preferences* -> *Enable XML editing*.
2. Then *File* -> *New Virtual Machine*.
3. Load the Windows ISO you downloaded.
4. Choose memory and CPU settings.
5. Choose the disk size.
6. Choose the image name and check *Customize configuration before install*.
7. In the *Overview* section, make sure the chipset is set to Q35 and the firmware is set to UEFI.
8. Enable Hyper-V Enlightenment. In particular, pay attention to `<hyperv>` and `<clock>`.
    ```xml
    <hyperv>
      <relaxed state="on"/>
      <vapic state="on"/>
      <spinlocks state="on" retries="8191"/>
      <vpindex state="on"/>
      <runtime state="on"/>
      <synic state="on"/>
      <stimer state="on"/>
      <frequencies state="on"/>
      <tlbflush state="on"/>
      <ipi state="on"/>
      <evmcs state="on"/>
      <avic state="on"/>
    </hyperv>
    ```
    ```xml
    <clock offset="localtime">
      <timer name="rtc" tickpolicy="catchup"/>
      <timer name="pit" tickpolicy="delay"/>
      <timer name="hpet" present="no"/>
      <timer name="hypervclock" present="yes"/>
    </clock>
    ```
9. In the *CPU* section, set the CPU model to *host-passthrough*.
10. For using *virtio-fs*, check *Enable shared memory* in the *Memory* section.
11. In the *SATA Disk 1* section, set the *Disk Bus* to *VirtIO*, *Cache mode* to *none* and *Discard mode* to *unmap*.
12. Mount the VirtIO ISO from *Add Hardware* -> *Storage* -> *Select or create custom storage*. Make sure *Device Type*
    is set to *CDROM* and *Device Bus* is set to *SATA*.
13. In the *NIC* section, set the *Device model* to *virtio*.
14. Remove the *Tablet* device (for efficiency).
15. Add a communication channel. *Add Hardware* -> *Channel* and from the drop-down list, select *org.qemu.guest_agent.0* as the *Name*.
16. For Windows 11, make sure *TPM* -> *Version* is set to *2.0*.

### Install Windows

1. Begin Installation. If possible, I recommend Windows 11 Pro N (it comes with less bloatware).
2. When you get to "Where do you want to install Windows?", select *Load Driver*, choose *E:/viostor/w11/amd64* and install
    the VirtIO driver.
3. Before continuing with the installation, repeat the process for *E:/NetKVM/w11/amd64* and install the network driver.
4. Continue with the installation.
5. Launch Windows Explorer, navigate to the *CD Drive (E:)*, and double-click the *virtio-win-guest-tools* package to install it.
6. *View* -> *Scale Display* -> *Auto resize VM to window*.
7. Unmount the *virtio-win.iso* image and then remove the second CDROM drive.
8. Unmount the ISO image of the Windows 11 installer from the first CDROM drive as well.

### Optimize the installation

1. Disable *SuperFetch* by launching *services* from the search bar and disabling the *SysMain* service.
2. Disable *Windows Web Search* by launching *regedit* and create the key `Computer\HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\Explorer`.
  Inside this key, add a new DWORD `DisableSearchBoxSuggestions` and set it to `1`.
3. Run `bcdedit /set useplatformclock No` as Administrator to disable the platform clock.
4. Run PowerShell as Administrator and execute `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`.
5. In order to trim down any unnecessary services and tasks, you can run the [trimwin11.ps1 script](https://github.com/apetenchea/cdroot/blob/master/source/_posts/running-windows-in-kvm/code/trimwin11.ps1)
  as administrator. Some tasks may be disabled and some may not, but don't worry, it is meant to iterate through them and disable whatever it has permission to.
6. Disable unnecessary startup programs: *Settings* -> *Apps* > *Startup*.
7. Enable *Developer Mode* in *System Settings*.
8. In search, *Adjust the appearance and performance of Windows* and set *Adjust for best performance*.
9. Disable whatever else you don't need in *Settings*, including *Windows Defender*, especially if you plan to use the
    VM for malware analysis.
10. Disable hibernation file by running `powercfg /h off` in an elevated command prompt.
11. Restart for the changes to take effect.

This would be a very good time to take a snapshot. On that note, I had some issues with deleting snapshots, so what worked
for me was:

```bash
virsh snapshot-delete <machine-name> <snapshot-name> --metadata
rm /var/lib/libvirt/images/<machine-name><snapshot-name> 
```

### Install the virtio-fs shared file system

Virtiofs is a shared file system that lets virtual machines access a directory tree on the host.

1. Install [winfsp](https://github.com/winfsp/winfsp) inside your guest VM and then reboot.
2. Install `virtiofsd` on host.

    ```bash
    sudo apt update
    sudo apt install virtiofsd
    sudo systemctl restart libvirtd
    ```
3. Add a new filesystem to the VM. In `virt-manager`, go to *Add Hardware* -> *Filesystem* and select the directory
  you want to share, making sure the driver type is `virtiofs`. Basically, your libvirt XML configuration should contain
  something like this:

    ```xml
    <domain>
      ...
      <memoryBacking>
        <source type='memfd'/>
        <access mode='shared'/>
      </memoryBacking>
      ...
      <devices>
        <filesystem type="mount" accessmode="passthrough">
          <driver type="virtiofs" queue="1024"/>
          <source dir="/home/user/viofs"/>
          <target dir="mount_tag"/>
          <address type="pci" domain="0x0000" bus="0x06" slot="0x00" function="0x0"/>
        </filesystem>
      </devices>
    </domain>
    ```
 
4. Make sure the `virtiofs` driver in installed on the guest VM and the service is running.
  I found mine in *Device Manger* -> *System Devices* -> *VirtIO FS Device*. You can find the driver
  in the *virtio-win.iso* image, which you can add as a CDROM device in `virt-manager` and then load the driver from there.
 
5. Start the service: `sc.exe create VirtioFsSvc binpath="(your binary location)\virtiofs.exe" start=auto depend="WinFsp.Launcher/VirtioFsDrv" DisplayName="Virtio FS Service"`
  and then run `sc.exe start VirtioFsSvc`. In case the service was already created, use `config` instead of `create`.

6. If you want it to start automatically, run `sc.exe config VirtioFsSvc start= auto`.

Symlinks don't work, but you can always mount another directory in your shared directory. For example, on the host I have
my `windows` directory in `~/windows` but I also want to make the `~/src` directory available in the VM. I can do this
by running the following command:

```bash
mkdir -p ~/windows/src
sudo mount --bind ~/src ~/windows/src
```

Or you can make it persistent by adding the following line to your `/etc/fstab` file:

```
/home/<user>/idasrc        /home/<user>/idasrc      none      bind      0      0
```

## Conclusion

It took me a while to get everything working, but now I have a fully functional Windows 11 VM running on KVM with
virtio-fs shared file system. The performance is surprisingly good!

A big thanks to [Madhu Desai](https://sysguides.com/install-a-windows-11-virtual-machine-on-kvm) for taking
the time to write a detailed guide, which helped me a lot in the process.

## References and Further Reading

- [Madhu Desai, How to Properly Install a Windows 11 Virtual Machine on KVM](https://sysguides.com/install-a-windows-11-virtual-machine-on-kvm)
- [Jochen Delabie, Hyper-V Enlightenments with Libvirt](https://www.jochendelabie.com/2020/05/15/hyper-v-enlightenments-with-libvirt/)
- [How to install virtiofs drivers on Windows](https://virtio-fs.gitlab.io/howto-windows.html)
- [Viktor Prutyanov, Virtiofs: Shared file system](https://github.com/virtio-win/kvm-guest-drivers-windows/wiki/Virtiofs:-Shared-file-system)
