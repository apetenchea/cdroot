---
title: Notes for C++ development on Windows
date: 2022-08-01 19:38:05
tags:
- Windows
- Programming
---

I've been writing a lot of C++ code at [ArangoDB](https://github.com/arangodb/arangodb) lately. Most people want their
databases to run on top of some Linux distro, which makes perfect sense, but we support Windows as well.
Even though that comes with extra maintenance costs, I think it's a good idea. By building your project under
different compilers, you make sure the code stays portable and uses only standard C++ features.
Multiple compilers together may point out more potential issues in your code. By testing your project on different operating
systems, you see how it behaves under different circumstances, thus making sure it doesn't rely on platform
specific behavior. I once stumbled across a stack overflow which was only revealed when running the tests on Windows,
because the stack size is by default smaller (1MB compared to 10MB on Linux). Even concurrency issues are often
uncovered this way, because different operating systems use different [schedulers](https://en.wikipedia.org/wiki/Scheduling_(computing)).

## Compilers

The staple compiler on Windows is [MSVC](https://visualstudio.microsoft.com/vs/features/cplusplus/). A good alternative is
[clang-cl](https://clang.llvm.org/docs/MSVCCompatibility.html), a driver program for clang that attempts to be compatible
with MSVC's _cl.exe_. There's also [MinGW](https://www.mingw-w64.org/), but I never tried it.  
I find compiling on Windows slower compared to Linux, probably due to [NTFS](https://en.wikipedia.org/wiki/NTFS)
and [ext4](https://en.wikipedia.org/wiki/Ext4) differences. More so, I sometimes experienced lag when using the computer during
longer builds, so I decreased the CPU and IO priority of the MSVC compiler and linker processes.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/C-development-on-Windows/code/ReduceCLPriority.reg %}

In the example above, I changed the priority to _below normal_, which works great for me. Here's a list of hex values,
so you can customize it:

- Low: 00000001
- Below Normal: 00000005
- Normal: 00000002
- Above Normal: 00000006
- High: 00000003

Changing the process priority fixed the issue for me, but in case that's not enough you could limit the number of _cl.exe_
processes (to 8, for example) by passing the `/p:CL_MPCount=8` argument to [MSBuild](https://docs.microsoft.com/en-us/visualstudio/msbuild/msbuild).
If you're using an IDE, most probably there's a setting for that.

## Debuggers

## References

* [stackoverflow.com](https://stackoverflow.com/questions/53503593/how-to-reduce-visual-studio-build-process-priority-to-prevent-unresponsive-syste)
* [answers.microsoft.com](https://answers.microsoft.com/en-us/windows/forum/all/how-to-permanently-set-priority-processes-using/2f9ec439-5333-4625-9577-69d322cfbc5e)
