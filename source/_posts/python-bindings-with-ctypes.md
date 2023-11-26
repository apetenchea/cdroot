---
title: python bindings with ctypes
date: 2023-10-04 18:45:53
tags:
  - "Programming"
---


![Python and C Bindings Cyber Image](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/python-bindings-with-ctypes/media/python-c-merged.jpg)

There's plenty of ways to write Python bindings for C/C++ code. The classic, no-frills approach is to use the
[ctypes](https://docs.python.org/3/library/ctypes.html) module of the standard library. It provides a convenient way to
load dynamic libraries in Python and call functions from them. Other common options are [pybind11](https://pybind11.readthedocs.io/en/stable/)
and [cython](https://cython.org/), which are more powerful, but also more complex. They come with a bunch of dependencies and
require a build step, which is not always desirable. Usually, bindings created using the latter methods have to be targeted at
specific Python versions, whereas ctypes allows for more portability. The best choice depends on the use case. If the
library was written with Python bindings in mind (i.e., no unsupported, cutting-edge C++ features), then go for pybind11
or cython. Otherwise, if you don't really have a say in the source code of the library you want to bind to, or even worse,
you don't have access to the source code at all, then ctypes is a great option. It's easy to use and comes with no extra
dependencies. For a small to medium-sized project, it's probably all you need.

## Fnv Hash

I've written a small library that implements the [FNV-1a hash function](http://www.isthe.com/chongo/tech/comp/fnv/)
in C++. It's a simple, non-cryptographic hash that's easy to implement and fast to run. I'm going to demonstrate
how to bind to it using ctypes, but it's not important to understand how the function itself works. If you're curious,
here's the pseudocode:
```
hash = offset_basis
for each octet_of_data to be hashed
 hash = hash xor octet_of_data
 hash = hash * FNV_prime
return hash
```

### Implementation

The library can be used to compute the 32-bit version of the hash. The `Fnv` object may be updated as many times as
needed, and the hash can be retrieved using the `digest` method. The default update function is meant to
work on an array of bytes, but it's easy to create a templated version that works on any type of data.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/fnv.h 10 23 %}

As for the implementation, it's pretty simple.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/fnv.cpp 4 13 %}

### Basic usage

Here's the complete [fnv.h](https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/fnv.h)
and [fnv.cpp](https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/fnv.cpp) code.
A basic usage example in C++ would look something like this:

```cpp
fnv::Fnv1a32 hash;
std::uint8_t x[] = "\x12\x34\x56\x78";
hash.update(x, 4);
std::cout << hash.digest();
```

## Bindings

### How ctypes works

The best thing about ctypes is that it works out of the box. There's no need to install anything. Just `import ctypes`
and you're good to go.  
The first step requires loading the library. This is done by passing the library path to the [ctypes.CDLL function](https://docs.python.org/3/library/ctypes.html#ctypes.CDLL).
For example, `libc = ctypes.CDLL("libc.so.6")` would return a handle to the C standard library on Linux. Note that the
handle can be used to access only the functions exported by the library, not all the functions inside the library.  
Once the library is loaded, you can access its functions much like accessing functions from a Python module. The most
important aspect to consider is data marshalling. C and Python have different data types, so ctypes needs to know how
to convert between them. You must explicitly specify the argument types (`argtypes`) and the return type (`restype`) of a function.
For example, [strchr](https://man7.org/linux/man-pages/man3/strchr.3.html) from the C standard library has the following signature:

```c
char *strchr(const char *s, int c);
```

It returns a pointer to the first occurrence of the character c in the string s. In order for ctypes to know how to
use the function, you need to specify the argument types and the return type like this:

```python
libc = ctypes.CDLL("libc.so.6")
strchr = libc.strchr
strchr.restype = ctypes.c_char_p
strchr.argtypes = [ctypes.c_char_p, ctypes.c_int]
```

After that, you may use the function like this:

```python
strchr(b"hello", b"l")
```

A list of fundamental data types and their corresponding C and Python types can be found [here](https://docs.python.org/3/library/ctypes.html#fundamental-data-types).

### Creating the library

#### C wrapper

Although it would be really cool to export directly the `Fnv1a32` class to Python, it's not possible. We can only export
and bind to C-style functions. The workaround is to create a function that instantiates the class and explicitly calls its methods.
We'll instantiate the object on the heap and return a pointer to it, which is going to be used as a handle in Python. This is easy
for ctypes to interpret, as a pointer is just an integer representing a memory address.
Same goes for all the parameters and return types - they're either fundamental types or pointers to a more sophisticated type.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/bindings.cpp 3 5 %}

One very important aspect is memory management. Memory allocated in C must be freed in C, as Python's garbage collector won't manage this memory.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/bindings.cpp 7 9 %}

Using the pointer, we can call the `update` and `digest` methods on the object it points to. That looks pretty much like trying
to mimic object-oriented programming in C. Note how its usage resembles the `this` pointer from C++.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/bindings.cpp 11 29 %}

#### Exporting functions

Since we're using C++, exporting functions is not as straightforward as it is in C. C++ supports function overloading,
meaning you can have multiple functions with the same name but different parameters. This is not possible in C, and more so,
it would be very confusing for ctypes. Suppose we have two functions called `fnv_update`, which take different parameters.
How would ctypes know which one to import from the library?  
Internally, C++ uses a technique called [name mangling](http://web.mit.edu/tibbetts/Public/inside-c/www/mangling.html).
It basically encodes the function name with information about the number and types of its parameters. This makes it impossible
to export a function with a specific name, because the name is not known until the code gets compiled.  
Therefore, we have to tell the compiler to use C linkage for the functions we want to export, effectively disabling name mangling
and using a consistent calling convention. This is done by wrapping the function declarations in an `extern "C"` block.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/bindings.h 11 19 %}

For example, without the `extern "C"` block, the `fnv_digest` exported function would look like this (on my Linux machine, using clang):

```
_Z10fnv_digestPN3fnv7Fnv1a32E
```

Wrapping the declaration in an `extern "C"` block causes it to be exported in a more familiar way:

```
fnv_digest
```

Note the `EXPORT` macro preceding each function declaration.
I had to use it because, on Windows, exported functions must be decorated with `__declspec(dllexport)`.
On Linux, this is not necessary, so the macro expands to nothing.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/bindings.h 5 9 %}

#### Building

There's a total of two _cpp_ files that need to be compiled: [fnv.cpp](https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/fnv.cpp),
which contains the implementation of the Fnv1a32 class, and [bindings.cpp](https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/bindings.cpp)
which contains the wrapper functions. The latter depends on the former, so we need to link them together. For convenience,
I have created a [CMakeLists.txt](https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/CMakeLists.txt) file.
Note the `SHARED` parameter passed to `add_library`. This tells CMake to create a shared library, kind of like the `-shared` flag passed to g++.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/CMakeLists.txt %}

Building is pretty straightforward.

```bash
mkdir -p build 
cd build
cmake ..
cmake --build . --config Release
```

Depending on your platform, the result is going be the either a _fnv.dll_ or a _libfnv.so_ file.
The whole code directory is available [here](https://github.com/apetenchea/cdroot/tree/master/source/_posts/python-bindings-with-ctypes/code).

#### Viewing exported functions

What if you don't have access to the source code of the library you want to bind to?  
There are various tools that can be used to inspect the exported functions of a shared library. On Linux, you can use
the `nm -D --defined-only libfnv.so` command, while on Windows, the `dumpbin` utility that comes with Visual Studio.
For example, on Windows, the output of `dumpbin /EXPORTS fnv.dll` looks like this:

```
Microsoft (R) COFF/PE Dumper Version 14.32.31332.0
Copyright (C) Microsoft Corporation.  All rights reserved.


Dump of file fnv.dll

File Type: DLL

  Section contains the following exports for fnv.dll

    00000000 characteristics
    FFFFFFFF time date stamp
        0.00 version
           1 ordinal base
           7 number of functions
           7 number of names

    ordinal hint RVA      name

          1    0 00001070 delete_fnv
          2    1 00001120 fnv_digest
          3    2 00001080 fnv_update_bytes
          4    3 000010F0 fnv_update_float
          5    4 00001090 fnv_update_uint32
          6    5 000010C0 fnv_update_uint64
          7    6 00001040 new_fnv

  Summary

        1000 .data
        1000 .pdata
        2000 .rdata
        1000 .reloc
        1000 .rsrc
        1000 .text
```

As for the function parameters and return types, if you don't have access to the source code, you may have to resort to
reverse engineering. There are various tools that can help you with that, but I'm not going to get into it in this article.

### Creating the Python module

After you got the shared library, creating the Python module is relatively easy. You just need to load the library
using `ctypes.CDLL` and specify the argument types and return types of the functions you want to use, sort of like 
"declaring" them in Python.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/fnv.py 5 10 %}

The process can get repetitive, so you might as well let the GitHub Copilot do some of the work for you.

<video controls>
  <source src="https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/python-bindings-with-ctypes/media/copilot-python-bindings.mp4" type="video/mp4">
Your browser does not support the video tag.
</video> 

As already noted, you have to take care of garbage collection yourself.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/fnv.py 36 40 %}

Also, make sure to call the correct function depending on the type of the argument.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/fnv.py 42 53 %}

Here's the complete [fnv.py](https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/fnv.py) code,
along with [a couple of small unit tests](https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/test_fnv.py),
so you can check if everything works as expected.

## Usage 

The newly created Python module can be imported and used like any other module.
Just make sure the shared library is in the same directory as the Python module, so that ctypes can find it. In practice,
you may also want to add the library to the `LD_LIBRARY_PATH` environment variable on Linux, or to the `PATH` environment
variable on Windows, but that's not necessary for this example.

```python
from fnv import Fnv

fnv = Fnv()
fnv.update(b'abcd')
print(fnv.digest())
```

Perhaps now it's a bit more obvious why ctypes can be a great way to create Python bindings for C/C++ code. May not fit
all uses cases out there, but works for most of them. I personally believe its simplicity is also its greatest strength.