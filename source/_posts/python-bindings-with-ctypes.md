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
in C++. It's a simple, non-cryptographic hash that's easy to implement and fast to run. We're going to demonstrate
how to bind to it using ctypes, but it's not important to understand how the function itself works. If you're curious,
here's the pseudocode:
```
hash = offset_basis
for each octet_of_data to be hashed
 hash = hash xor octet_of_data
 hash = hash * FNV_prime
return hash
```

The library can be used to compute the 32-bit version of the hash. The `Fnv` object may be updated as many times as
needed, and the hash can be retrieved at any time using the `digest` method. The default update function is meant to
work on an array of bytes, but it's easy to create a templated version that works on any type of data.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/fnv.h 7 23 %}

As for the implementation, it's pretty simple.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/python-bindings-with-ctypes/code/fnv.cpp 4 13 %}

Note: dumpbin /EXPORTS fnv.dll (why we need extern "C")

Note: cd build; cmake ..; cmake --build . --config Release