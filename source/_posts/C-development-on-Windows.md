---
title: Notes for C++ development on Windows
date: 2022-08-01 19:38:05
tags:
- Windows
- Programming
---

I've been writing a lot of C++ code at [ArangoDB](https://github.com/arangodb/arangodb) lately. Most people want their
databases to run on top of some Linux distro, which makes perfect sense, but ArangoDB supports Windows as well (at least
they did, until version 3.12).
Even though that comes with extra maintenance costs, I think it's a good idea. By building your project with
different compilers, you're making sure the code stays portable and uses only standard features.
Clearly, multiple compilers can point out more potential issues together. By testing our project on different operating
systems, we see how it behaves under various circumstances, thus making sure it doesn't rely on platform
specific behavior. I once stumbled across a stack overflow that was mostly reproduced when running the tests on Windows,
because the stack size is by default smaller (1MB compared to 10MB on Linux). Even concurrency issues are often
uncovered this way, because different operating systems use different [schedulers](https://en.wikipedia.org/wiki/Scheduling_(computing)).

## Compilers

The staple compiler on Windows is [MSVC](https://visualstudio.microsoft.com/vs/features/cplusplus/). A good alternative is
[clang](https://clang.llvm.org). If you care about MSVC compatibility, check out
[clang-cl](https://clang.llvm.org/docs/MSVCCompatibility.html), a driver program for clang that attempts to be compatible
with MSVC's _cl.exe_.
There's also a way to get GCC on Windows, but I never tried it, one can check out [MinGW](https://www.mingw-w64.org/) if
he's so inclined.  
I find compiling on Windows slower compared to Linux, probably due to [NTFS](https://en.wikipedia.org/wiki/NTFS)
and [ext4](https://en.wikipedia.org/wiki/Ext4) differences. More so, I sometimes experienced lag when using the computer during
longer builds, so I decreased the CPU and IO priority of the compiler and linker processes.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/C-development-on-Windows/code/ReduceCLPriority.reg %}

In the example above, I am setting the priority to _below normal_, which works great for me. Here's a list of hex values,
so you can customize it:

- Low: 00000001
- Below Normal: 00000005
- Normal: 00000002
- Above Normal: 00000006
- High: 00000003

In case that's not enough, you could limit the number of _cl.exe_
processes (to 8, for example) by passing the `/p:CL_MPCount=8` argument to [MSBuild](https://docs.microsoft.com/en-us/visualstudio/msbuild/msbuild).
If you're using an IDE, most probably there's a setting for that.

## Debuggers

On Windows, I usually go for [lldb](https://lldb.llvm.org/). You need [LLVM](https://llvm.org/) for Windows, which is
available on their [GitHub releases page](https://github.com/llvm/llvm-project/releases). You can also get
[GDB](https://sourceware.org/gdb/), but it has the disadvantage of not being able to load Windows crash dumps.
Sometimes, during debugging, I have to observe the assembly instructions. In case of _x86-64_ programs,
I prefer the Intel syntax, which can be configured from the `.lldbinit` file, placed in the user directory:
```
settings set target.x86-disassembly-flavor intel
```

These two debuggers are great for most use cases, but for debugging Windows drivers I had to use
[WinDbg](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/debugger-download-tools). Although WinDbg
can be used to debug any program, not just drivers, I used it solely for that.

## Crash Dumps
Crash Dumps are the Windows counterpart of Linux Core Dumps. When a program crashes, a dump file (.dmp) is written
to disk. This can be later used to debug and analyze the program (memory content, registers), at the moment of the crash.
By default, crash dump generation is disabled, but it can be enabled through the `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps`
registry key.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/C-development-on-Windows/code/EnableDump.reg %}

How to configure it:
- DumpFolder - where the dump files are to be stored (`%LOCALAPPDATA%\Temp`)
- DumpCount - maximum number of dump files in the folder (64)
- DumpType - Custom/Mini/Full (Full)
- CustomDumpFlags - only used when _DumpType_ is set to 0

Here's a Python one-liner to generate a _DumpFolder_ REG_EXPAND_SZ from a custom string:
```python
',00,'.join([hex(ord(c))[2:] for c in '%LOCALAPPDATA%\Temp']) + ',00'
```

To test the settings, compile and run any broken C++ program.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/C-development-on-Windows/code/broken.cpp %}

Running this program will generate a crash dump in the folder pointed by _DumpFolder_. The dump will be named _executable.pid.dmp_.
In my case, that was _broken.exe.2940.dmp_, because I called the executable `broken.exe` and the process ID was `2940`.
Load the executable alongside its core in lldb:
```
lldb broken.exe -c broken.exe.2940.dmp
```

If you're used to GDB, but are new to lldb, check out this [nice command map](https://lldb.llvm.org/use/map.html).

## References and Further Reading

* [stackoverflow.com](https://stackoverflow.com/questions/53503593/how-to-reduce-visual-studio-build-process-priority-to-prevent-unresponsive-syste)
* [answers.microsoft.com](https://answers.microsoft.com/en-us/windows/forum/all/how-to-permanently-set-priority-processes-using/2f9ec439-5333-4625-9577-69d322cfbc5e)
* [docs.microsoft.com](https://docs.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps)
* [stackoverflow.com](https://stackoverflow.com/questions/20237201/best-way-to-have-crash-dumps-generated-when-processes-crash)