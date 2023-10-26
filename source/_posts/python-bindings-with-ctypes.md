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