---
title: Core Dumps
date: 2025-05-03 12:36:35
tags:
- Programming
---

A core dump is a file that captures the memory of a running process at a specific point in time, typically when the
process crashes or encounters a serious error. It contains a snapshot of the process's memory, including the call stack,
heap, and other relevant information. A core dump is useful for debugging and analyzing the state of a program at
the moment of failure. By loading it into a debugger, you can retrace exactly where and why your program crashed.

One of the first things I do when I configure my development environment is to make sure core dumps are enabled. The
process is different on each OS, so I will cover the most common ones: Linux, Windows and MacOS.

Example of a program that generates a core dump:

```c
int main() {
  int *p = 0;
  *p = 0; // This will cause a segmentation fault
  return 0;
}
```

Compile it with `clang`, for example:

```bash
clang -o crash crash.c
```

## Linux

### Howto

This is the easiest one, but it depends on the distributions. For me, on Debian Sid, it was as easy as adding
`ulimit -c unlimited` to my `.bashrc` file. This command allows core dumps to be generated without any size limit.  
Apart from that, I could set the core dump pattern by modifying the `/usr/lib/sysctl.d/10-coredump-debian.conf` file
to contain the following:

```
kernel.core_pattern=/tmp/core.%p
kernel.core_uses_pid=1
```
After running the executable, you can inspect the core dump with `gdb`:

```bash
gdb <executable> /path/to/core.<PID>
```

Or using `lldb`:

```bash
lldb <executable> -c /path/to/core.<PID>
``` 

If your distribution works differently, you can check where your system picks up the core dump pattern by running:

```bash
sudo sysctl --system
```

In my case it was obvious because one of the lines printed was _* Applying /usr/lib/sysctl.d/10-coredump-debian.conf ..._.

### Easy steps

1. Set the core dump pattern in `/usr/lib/sysctl.d/10-coredump-debian.conf` to `kernel.core_pattern=/tmp/core.%p`.
2. Set `ulimit -c unlimited` in your `.bashrc` file.
3. Source your `.bashrc` file or restart your terminal.

## MacOS

### Set a pattern

Core dumps are by default written into the `/cores` directory. If you want to keep it like that, you should make sure the
directory is writable by user running the program:

```bash
sudo chmod 1777 /cores
```

What this does:
- Everybody can create, rename, or modify files in it (because of th 777).
- Only the file owner can delete or rename their own files (because of the 1 - sticky bit).

If you want to change the location of the core dumps, you can do that by specifying a different path in the `sysctl` command:

```bash
sudo sysctl -w kern.corefile=/tmp/core.%P
```

This will write the core dumps into the `/tmp` directory, with the name `core.<PID>`, where `<PID>` is the process ID
of the process that crashed. Sadly, this is not consistent across reboots.

You can check the currently used pattern with `sysctl kern.corefile`.

### Set kernel state to allow core dumps

To enable core dumps, set the `kern.coredump` kernel state to 1. This setting is persistent across reboots.

```bash
sudo sysctl -w kern.coredump=1
```

You can check the current value with `sysctl kern.coredump`.

### Set the maximum size of core dumps

Similar to Linux, you need to let the system know that you're ok with core dumps filling up your disk.

```bash
ulimit -c unlimited
```

I personally set this in my `.bashrc` file, so that it stays somewhat consistent.

### Sign the executable

This is the most annoying part, because on MacOS only signed executables can generate core dumps. Fortunately, it's
not hard to do so. Suppose your executable is called `crash`, you can sign it with the following commands:

```bash
/usr/libexec/PlistBuddy -c "Add :com.apple.security.get-task-allow bool true" crash.entitlements
codesign -s - -f --entitlements crash.entitlements crash
```

The first command creates a file called `crash.entitlements` that contains the necessary entitlements for the executable.
It's not a big deal, just an XML file.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>com.apple.security.get-task-allow</key>
	<true/>
</dict>
</plist>
```

The second command signs the executable with the entitlements file. The `-s -` option means that you're using an ad-hoc
signature, which is sufficient for this purpose. The `-f` option forces the signing, even if the executable is already
signed.

After that, running `./crash` will generate a core dump.

### Loading the core dump

To load the core dump, you can use `lldb`:

```bash
lldb <executable> -c /path/to/core.<PID>
```

Inspect the backtrace with `bt` or see the list of threads with `thread list`. You can also use `thread select <N>`
to switch to a different thread.

### Bonus: disabling SIP

System Integrity Protection is a security feature that's very useful for the regular user, but it can get annoying when
developing or debugging. Disable it at your own risk. In my case, it slowed down the startup time of my built executables
considerably, so I disabled it.

1. Enter mac recovery mode: hold power until prompted for options.
2. From utilities choose the terminal.
3. Disable system integrity protection: `csrutil disable`.

## References and Further Reading

- [How to Dump a Core File on MacOS (Monterey 12.5)](https://nasa.github.io/trick/howto_guides/How-to-dump-core-file-on-MacOS.html)
