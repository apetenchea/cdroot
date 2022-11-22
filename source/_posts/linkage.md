---
title: Linkage
date: 2019-01-19 20:08:34
tags:
- Windows
- Reverse Engineering
---

*kernel32.dll* provides access to a significant part of the [Windows API](https://docs.microsoft.com/en-us/windows/desktop/apiindex/windows-api-list).
On *Windows 10* (and other versions), the 32 bit library is located in *C:\Windows\System32*, while the 64 bit one in
*C:\Windows\SysWOW64*.

## Linking

### Static linking

When a procedure is statically linked, the linker copies data from the library, embedding it into the executable.
There are some advantages to this, one being portability, since the program can run even on systems that don't have
the required library installed. Also, because the linking process no longer takes place at runtime, the program might
have a slightly faster startup.  
On the other hand, memory consumption quickly becomes a problem. If *kernel32.dll* were to be statically linked,
every running program would end up allocating space for it.

### Load-time dynamic linking

This is the most common way to link a library. The executable contains a section named [.idata](https://docs.microsoft.com/en-us/windows/desktop/debug/pe-format#the-idata-section),
which has the necessary linking information. Imported libraries are mapped into into the virtual address space of the process. This doesn't mean that a physical copy
is made for every library. Instead, their virtual memory pages are mapped to the same physical memory pages already
used by other processes. Think how common it is for a DLL such as *kernel32.dll* to be dynamically linked. Most of the
time its memory is read-only, so a single physical copy is enough for all the running processes. If for some reason
one tries to overwrite it, a copy of the modified memory page is instantly made for that particular process, keeping
the read-only one intact. Thus, due to [copy-on-write](https://docs.microsoft.com/en-us/windows/desktop/memory/memory-protection#copy-on-write-protection),
a process cannot impact a sheared DLL, while the system can make efficient use of space.  
The linker looks into these libraries and locates the procedures that need to be imported, writing their virtual
memory addresses to the [Import Address Table](https://docs.microsoft.com/en-us/windows/desktop/debug/pe-format#import-address-table).
This process is called **binding**.  

#### Example

Bellow is all the code it takes to display a standard message, using a procedure imported from *user32.dll*.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/linkage/code/load_time.cpp %}

#### Minimal build

I used *Visual Studio Community Edition 2015*. In order to prevent the compiler from adding extra imports I do the following:
- Set *Target* to *Release x86*.
- In *Project->Properties->Linker->Advanced->Entry Point* I set *main* as the entry point.
- I disable *Safe SEH*, *Debugging*, and *DEP*. This removes some extra checks and security measures,
creating an executable that closely resembles the source code.

#### Examining the import information

When I open the generated executable with [IDA](https://www.hex-rays.com/products/ida/), it shows me the following imports:
```
00402000  ExitProcess  KERNEL32
00402008  MessageBoxA  USER32
```
The first column is the virtual memory address, the second is the imported procedure's name and the third is the name
of the library. Just because it appears to be imported doesn't mean that a procedure is necessarily called, but there's
a pretty good chance. From a reverse engineer's point of view it is fairly easy to see that this program probably makes
use of `MessageBox` and `ExitProcess`, because this information is openly available inside the executable. 

### Run-time dynamic linking

It is possible to do the linker's job at runtime. You can map a DLL module into the virtual address space of a process
using [LoadLibrary](https://docs.microsoft.com/en-us/windows/desktop/api/libloaderapi/nf-libloaderapi-loadlibrarya).
After obtaining a *HANDLE* to the module, you can pass it to [GetProcAddress](https://docs.microsoft.com/en-us/windows/desktop/api/libloaderapi/nf-libloaderapi-getprocaddress),
along with the name of the procedure that you want to locate. On success, this will return a virtual address, which you can be
treated pretty much like a function pointer.

#### Example

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/linkage/code/run_time.cpp %}

Notice that there is no direct call to a procedure named `MessageBox`. All we have is a pointer to it, named `MsgBox`.
In case you are wandering what's up with the `A` in `MessageBoxA`, there are in fact two different procedures in *user32.dll*, 
designed to work with different string parameters: `MessageBoxW` for Unicode and `MessageBoxA` for ANSI.
Normally, the compiler takes care of this, but with `GetProcAddress` you have to be more specific. 

#### Examining the import information

```
00402000  LoadLibraryA  KERNEL32
00402004  GetProcAddress  KERNEL32
00402008  ExitProcess  KERNEL32
```

`MessageBoxA` is missing, but `LoadLibraryA` and `GetProcAddress` are there.
Because these two procedures reside in *kernel32.dll*, the library has to be linked before accessing
them. How could it be linked at runtime, when the procedures to do that must be imported from it? It's like trying
to unlock a suitcase, but you left the key inside it (happened to me once in an airport).

## Nonconventional ways of linking

### Looking up the stack

When a program is executed, a process is created. When the process is created, the main thread has to be started. How
does the system start the main tread? The `main` function is a function like any other, but where is it called from?  
There is an undocumented procedure inside *kernel32.dll*, which initializes a thread and calls the entry point.
Its name is `BaseThreadInitThunk` and it leaves on the stack a virtual address from within the library,
by calling your `main` function. So, there has to be a `call` instruction somewhere in `BaseThreadInitThunk`.
This instruction, besides changing the value of register `eip`, pushes the address of the next instruction onto the stack.
This means that right at the beginning of `main`, if you look up onto the stack, you shall see the virtual address of an instruction
belonging to `BaseThreadInitThunk`, and consequently, belonging to *kernel32.dll*.
For a quick recap, head [here](https://www.cs.virginia.edu/~evans/cs216/guides/x86.html#calling).

![Debugger illustration](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/linkage/media/BaseThreadInitThunk.png)

Long story short, 0x74958720 is the virtual address of `BaseThreadInitThunk`. The `call esi` instruction at 0x74958742 jumps
to the entry point, while pushing the address of the next instruction, 0x74958744, onto the stack. By knowing this address,
it is possible to find the base address of *kernel32.dll*. After finding the base address, one can find the library's export section
and import any function from there.

![Stack after call](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/linkage/media/stack.png)

How to get this value from the stack? When the function in generated, the compiler automatically adds the `push esi`
instruction at the beginning of `main`, so when the next instruction is being executed, the stack pointer moves down 4 bytes.
In this case, the thing is to derefence the value at `esp + 0x4` and store it somewhere.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/linkage/code/stack_linkage.cpp 89 90 %}

Getting to the base address requires a few more insights. The simplest one is that we must search towards lower addresses,
since the first byte of *kernel32.dll* is before `BaseThreadInitThunk`. Next, the `ImageBase` field, found in the
[Optional Header](https://docs.microsoft.com/en-us/windows/win32/debug/pe-format#optional-header-windows-specific-fields-image-only),
refers to the preferred address of an image when loaded into memory. It must be a multiple of 64K, which can be translated to
0x10000 in hex. It makes sense then to start from the first multiple of 0x10000 that is lower than the current address,
so I trim the last 4 zeros of the starting address. Also, I keep subtracting 64K instead of 1, in order to check only relevant
addresses. On the way to the base address, there might be some pages from which reading is not permitted. An exception handler
could be used to prevent a possible crash, but in this example I was lucky enough not to need one. 

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/linkage/code/stack_linkage.cpp 33 40 %}

Once the base address is found, the rest of the code becomes pretty strainghtforward. By following the [PE format](http://www.openrce.org/reference_library/files/reference/PE%20Format.pdf),
the `GetProcAddress` procedure can be located inside *kernel32.dll*. Using it, one can easily import other procedures.
In the full example, I wrote the code for locating `LoadLibraryA`, in order to load *user32.dll* and import `MessageBoxA` from it.
And yet, the executable has no imports section. [Here](https://github.com/apetenchea/cdroot/blob/master/source/_posts/linkage/code/stack_linkage.cpp) is the full POC.

### Searching the PEB

Every thread comes with some particularities, such as its own stack base address or thread ID. Information about the currently running thread is stored in a structure called
[TEB](https://docs.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-teb), sometimes also referred to as TIB. The Thread Environment Block can be accessed through the `fs` segment
register on 32 bit versions on Windows, or through the `gs` register on 64 bits. For the sake of simplicity, I will further consider only the 32 bit scenario. So, why do we care about the TEB in this context?
Because it contains the address of [PEB](https://docs.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-peb), a different structure which holds data about the process to which the current
thread belongs to. The Process Environment Block holds information such as the path of the process's image file, the command-line string passed to it,
whether or not the process is being debugged, and most importantly for us, the list of loaded modules. Needless to say, historically this has been widely abused by malware.
Before we move on, how exactly does one get the address of PEB?

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/linkage/code/peb_linkage.cpp 112 113 %}

A pointer to it can be found at offset 0x30, starting from `fs`. Once you got its address, you can access the
[PEB_LDR_DATA](https://docs.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-peb_ldr_data), from which you can get to the head of
a doubly linked list that holds information about the loaded modules. Every entry in this list contains the fields `FullDllName` and `DllBase`.
The problem now reduces to searching in a linked list: given the module name (as a [UNICODE_STRING](https://docs.microsoft.com/en-us/windows/win32/api/subauth/ns-subauth-unicode_string)),
find it in the list, and if it exists, return its corresponding DLL base address.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/linkage/code/peb_linkage.cpp 48 62 %}

The difficult thing to do, in my opinion, is to get to the head of the list, namely `Flink`. Due to differences in Windows
versions, these structures can differ from the official documentation. Finding the right offsets can be
[tricky](http://www.rohitab.com/discuss/topic/35251-3-ways-to-get-address-base-kernel32-from-peb/).

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/linkage/code/peb_linkage.cpp 116 116 %}

Once you get the base address of the module, you can parse it as you would do with a regular PE file. If you ever see this approach in "the wild",
you can expect the next thing to be a search for the address of `GetProcAddress`, in the library's export section.
[Here](https://github.com/apetenchea/cdroot/blob/master/source/_posts/linkage/code/peb_linkage.cpp) is the full POC.

## References

* [ntopcode](https://ntopcode.wordpress.com/2018/02/26/anatomy-of-the-process-environment-block-peb-windows-internals/)
* [microsoft](https://msdn.microsoft.com/en-us/library/windows/desktop/ms680547(v=vs.85).aspx)
* [Geoff Chappell](https://www.geoffchappell.com/studies/windows/win32/ntdll/structs/teb/index.htm)
