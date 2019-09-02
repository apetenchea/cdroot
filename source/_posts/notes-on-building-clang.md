---
title: Notes on building Clang
date: 2019-01-30 20:25:10
tags:
- LLVM
- Linux
---

How I built Clang on Ubuntu 18.04.1 LTS, using GCC.

## Requirements

Make sure you have the [required software.](https://llvm.org/docs/GettingStarted.html#requirements)
Here's what I used:
- GNU Make 4.1
- GCC 7.3.0
- CMake 3.10.2
- Python 3.6.5 (for running tests)
- zlib 1.2.11 (optional)

Before installing new packages, I usually update & upgrade.
```bash
# Update the list of available packages and their version
sudo apt update

# Actually install newer versions of packages
sudo apt upgrade
```

## Checkout

[Checkout LLVM from Git](https://llvm.org/docs/GettingStarted.html#checkout-llvm-from-git).
Take a look at their [releases](https://github.com/llvm/llvm-project/releases). I chose version 7.0.0. That's on branch
*release/7.x*, commit *00b161b8971bc6d3cb55f13502288b8fe0dbaa42*.
```bash
git clone --single-branch --branch release/7.x https://github.com/llvm/llvm-project.git
git checkout 00b161b8971bc6d3cb55f13502288b8fe0dbaa42
```

## Configure LLVM

After the checkout was complete, I created a folder where the object files would be placed.
```bash
cd llvm-project
mkdir release
cd release
```
CMake generates the build files. [Build variables](https://llvm.org/docs/GettingStarted.html#local-llvm-configuration)
are used to specify the build configuration. 
```bash
cmake -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Release -DLLVM_TARGETS_TO_BUILD="X86" -DLLVM_ENABLE_PROJECTS="clang;compiler-rt" -DCLANG_ENABLE_BOOTSTRAP=On ../llvm
```
Check the CMake output and install any missing software. I got a few errors myself:
```
Could NOT find LibXml2
Could NOT find Doxygen
Could NOT find Curses
Could NOT find SWIG
```
Fixed:
```bash
sudo apt install libxml2-dev
sudo apt install doxygen
sudo apt install libncurses5-dev
sudo apt install swig
```

## Compile

[Generate binaries](https://llvm.org/docs/GettingStarted.html#compiling-the-llvm-suite-source-code).
While still in `/release`, run `make -j5`. The `-j` parameter represents the number of workers used to parallelize
the build process. Depending on the configuration, your machine and the number of worker threads you assign,
this might take a while.

## Bootstrap

[Bootstrapping](https://llvm.org/docs/AdvancedBuilds.html#bootstrap-builds) refers to using the newly built compiler
in order to build itself again. It is only possible if makefiles were generated with `CLANG_ENABLE_BOOTSTRAP=On`.
This step is optional and it takes time. If you've had enough, consider skipping it.
```bash
make stage2
```
I didn't add any more workers this time because during linking the entire process would eat up more than 8GB of RAM.

## Test

To make sure everything went as planned, run the tests to validate your work. 
```bash
make check-clang
```
Or, to check everything:
```bash
make check-all
```

## Install
By default, the install location is `/usr/local`. You probably need root permission to install in there.
``` 
make install
```
If for some reason you want to undo this step:
```
xargs rm < install_manifest.txt
```
After installing, I removed the `/release` folder because I don't plan on doing another build. It occupies quite a lot
of disk space, but if you plan on building Clang again, make sure you keep it around.
