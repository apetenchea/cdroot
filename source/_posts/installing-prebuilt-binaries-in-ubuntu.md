---
title: Installing prebuilt binaries in Ubuntu
date: 2021-10-17 19:18:32
tags:
- Linux
---

The primary way of installing software in Ubuntu and other Debian-based distros is through
[apt-get](https://linux.die.net/man/8/apt-get). It downloads packages from repositories and
installs them locally. However, sometimes you might have to install packages that come
as prebuilt binaries.

## How does apt-get work?

`apt-get` locates packages on the software repositories listed in */etc/apt/sources.list* or */etc/apt/sources.list.d*.
It uses [dpkg](https://man7.org/linux/man-pages/man1/dpkg.1.html) as backend to perform the installation on your system.
In order to locate where a package has been installed, run `dpkg -L package_name`.
```
dpkg -L vim
/.
/usr
/usr/bin
/usr/bin/vim.basic
/usr/share
/usr/share/bug
/usr/share/bug/vim
/usr/share/bug/vim/presubj
/usr/share/bug/vim/script
/usr/share/doc
/usr/share/doc/vim
/usr/share/doc/vim/NEWS.Debian.gz
/usr/share/doc/vim/changelog.Debian.gz
/usr/share/doc/vim/copyright
/usr/share/lintian
/usr/share/lintian/overrides
/usr/share/lintian/overrides/vim
```
The example above displays all the files that come with the [vim](https://www.vim.org/) package. Run `apt show vim` to get more details.

## Prebuilt packages

Things can be really smooth with `apt` or `apt-get`, but when dealing with prebuilt packages, some manual intervention is required.
These packages generally come as `.tar.gz` archives containing compiled binaries for a specific platform. You have to extract them and
move the contents to */usr/local* or */opt* for a system-wide installation. [/usr/local](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch04s09.html)
is for use by the system administrator when installing software locally, while [/opt](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch03s13.html)
if for installing packages that are not part of the operating system. It's up to you which one you choose, in my experience either
works fine. Let's say you want to install a prebuilt package named *example.tar.gz*. Note that any of the steps described bellow may require root privileges.
1. Make sure the package is not already installed in */usr/local* or */opt*. If that's the case, remove all files from the previous
installation: `rm -rf /opt/example`.
2. Extract the contents of the archive into the desired location.
    ```sh
    tar -C /opt -xzf example.tar.gz 
    ```
    - -C is used to change the target directory
    - x is used to extract files from the archive
    - z is used to filter the archive through [gzip](https://www.gnu.org/software/gzip/). For *.tar.xz* archives use J instead of z, and for *.tar.bz2* use j.
    - f indicates the archive to be processed
3. Add the newly installed binaries to the `PATH` environment variable. The executables are typically stored in the */bin* folder of the package, so in this case we
are looking for */opt/example/bin*. To modify the `PATH` variable only for the current user, edit your *~/.bashrc* file (assuming you're using bash) or your `~/.profile` and add the *bin* folder
to `PATH`. To make the binaries available system-wide, edit */etc/profile*. You may need to restart your shell for the changes to take effect.
```sh
export PATH="$PATH:/opt/example/bin"
```

## Real examples

### Go

You can find the official tutorial on [golang.org](https://golang.org/doc/install).

1. Download the archive. Make sure to choose a recent version.
    ```
    wget https://golang.org/dl/go1.17.2.linux-amd64.tar.gz
    ```
2. Remove files from the previous installation, if any.
    ```
    sudo rm -rf /opt/go
    ```
3. Extract the archive.
    ```
    sudo tar -C /opt -xzf go1.17.2.linux-amd64.tar.gz
    ```
4. Edit the `PATH` variable into your *~/.bashrc* and then reload bash config by running `source ~/.bashrc`, or simply restart the shell.
    ```sh
    # This line should be in your .bashrc file.
    export PATH="$PATH:/opt/go/bin"
    ```
5. Check it out.
    ```
    go version
    go version go1.17.2 linux/amd64
    ```

### ArangoDB

Note that this may also be installed using `apt-get`. You can find details on [arangodb.com](https://www.arangodb.com/download-major/ubuntu/).

1. Choose your version and download the server archive.
    ```
    wget https://download.arangodb.com/arangodb38/Community/Linux/arangodb3-linux-3.8.1.tar.gz
    ```
2. Remove files from the previous installation, if any.
    ```
    sudo rm -rf /opt/arangodb3-linux-3.8.1
    ```
3. Extract the archive.
    ```
    sudo tar -C /opt -xzf arangodb3-linux-3.8.1.tar.gz 
    ```
4. Edit the `PATH` variable into your *~/.bashrc* and then `source ~/.bashrc` or restart the shell.
    ```sh
    # This line should be in your .bashrc file.
    export PATH="$PATH:/opt/arangodb3-linux-3.8.1/bin"
    ```
5. Check it out.
    ```sh
    arangod --version
    3.8.1
    
    architecture: 64bit
    # ...
    # long output cropped
    ```

### Clang + LLVM

Make sure the release is compatible with your OS version. Official releases available on [github](https://github.com/llvm/llvm-project/releases).

1. Download the archive.
    ```
    wget https://github.com/llvm/llvm-project/releases/download/llvmorg-10.0.0/clang+llvm-10.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz
    ```
2. Remove files from the previous installation, if any.
    ```
    sudo rm -rf /opt/clang+llvm-10.0.0-x86_64-linux-gnu-ubuntu-18.04
    ```
3. Extract the archive. Be mindful of the file extension.
    ```
    sudo tar -C /opt -xJf clang+llvm-10.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz
    ```
4. Edit the `PATH` variable into your *~/.bashrc* and then `source ~/.bashrc`, or restart the shell.
    ```sh
    # This line should be in your .bashrc file.
    export PATH="$PATH:/opt/clang+llvm-10.0.0-x86_64-linux-gnu-ubuntu-18.04/bin"
    ```
5. Check it out.
    ```
    clang --version
    clang version 10.0.0 
    Target: x86_64-unknown-linux-gnu
    Thread model: posix
    InstalledDir: /opt/clang+llvm-10.0.0-x86_64-linux-gnu-ubuntu-18.04/bin
    ```

## References and Further Reading

* [linuxhint](https://linuxhint.com/apt-get-install-packages-to/)
