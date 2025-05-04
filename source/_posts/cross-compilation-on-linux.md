---
title: Cross Compiling on Linux
date: 2025-05-04 09:49:38
tags:
- Linux
- Programming
---

Sometimes I need to compile code for various CPU architectures. I have a pretty unusual reason for that, which is testing
[IDA Pro's](https://hex-rays.com/ida-pro) processor modules. While working on a processor module, I must make sure
that the newly added instructions are correctly disassembled, and the best way to do that is to feed the disassembler
with binary code generated from a compiler. The instructions presented here are the same for most architectures,
but I will focus on RISC-V as an example.

## Building

The first step is to get your cross-compilation toolchain ready. I generally prefer using Docker, because it does not
pollute my system with additional packages.

### Using Docker

Fortunately for us, the [dockcross](https://github.com/dockcross/dockcross) contains lots of cross-compilation toolchains
wrapped in Docker images.

```bash
git clone https://github.com/dockcross/dockcross.git
cd dockcross
docker run --rm dockcross/linux-riscv64 > ./dockcross-linux-riscv64
chmod +x ./dockcross-linux-riscv64
```

I usually invoke the shell and work from there. The coolest thing is that commands in the container run as the
calling user, so any created files have the expected ownership, (i.e. not root).

```bash
./dockcross-linux-riscv64 bash
[username:/work] master ± $CC -o hello test/C/hello.c 
```

In the same container, running `readelf -h hello` will show you the architecture of the compiled binary:

```
Machine: RISC-V
```

Note that it might help to add the `-static` flag to the compilation command. This will create a statically linked
binary, which is easier to run in an emulator.

### Installing the toolchain

If you want to install the toolchain on your system, you can do that by running the following commands:

```bash
sudo apt update
sudo apt install \
  gcc-riscv64-linux-gnu \
  g++-riscv64-linux-gnu \
  binutils-riscv64-linux-gnu
```

If you only care about one particular architecture, this approach might feel more stable than using Docker.
Once installed locally, use it like:

```bash
riscv64-linux-gnu-gcc -o hello hello.c
```

What if you want to compile using clang? Then, you need to tell clang where to find the C libraries
and include files. I had to do this once, because I wanted to try some exotic RISC-V instructions which were not
supported by GCC at that time (e.g. `amocas`).

```bash
clang \
  -menable-experimental-extensions \
  --target=riscv64 \
  -march=rv64imafdc_zicsr_zifencei_zacas1p0 \
  -c hello.c \
  --gcc-toolchain=/usr/riscv64-linux-gnu-
```

If you're using the Docker image, you can always install clang inside the container. You can find the path to the
toolchain by running `which $CC` and see where the compiler is located. In `dockross`, the toolchain is installed in
`/usr/xcc/riscv64-unknown-linux-gnu/`.  

Depending on what you want to do, it might get tricky to find the right include files. For C++, with `riscv64-linux-gnu`
toolchain installed locally on my system, I once had to run something like this:

```bash
clang++ \
  -std=c++14 \
  -O2 \
  --target=riscv64 \
  -march=rv64imafdc_zicsr_zifencei_zacas1p0 \
  --gcc-toolchain=/usr/riscv64-linux-gnu/ \
  -I/usr/riscv64-linux-gnu/include/c++/14 \
  -I/usr/riscv64-linux-gnu/include/c++/14/riscv64-linux-gnu/ \
  -isystem /usr/riscv64-linux-gnu/include \
  -menable-experimental-extensions \
  -c hello.cpp
```

Don't get discouraged though, it's easy once you figure out how to do it once.

### Build the toolchain from source

Sometimes you're looking into a new and exotic architecture, when you realize that the toolchain is not readily available. You
might have to compile it yourself, but don't worry, it's actually not that hard. Take for example the
[xuantie-gnu-toolchain](https://github.com/XUANTIE-RV/xuantie-gnu-toolchain). First, go to their `README.md` and make
sure the required dependencies are installed on your system.

Then, clone the repository and build the toolchain:

```bash
git clone https://github.com/XUANTIE-RV/xuantie-gnu-toolchain
cd xuantie-gnu-toolchain
./configure --prefix=/path/to/xuantie-gnu-toolchain
make -j$(nproc)
```

This will create a `bin` directory inside `xuantie-gnu-toolchain` with the cross-compilation toolchain. All the tools will
be there. Run `git status` to inspect what else has been created.

Have fun using the `theadc` extension:

```bash
./bin/riscv64-unknown-elf-gcc -march=rv64gcxtheadc -o example example.c
```

## Running programs for other architectures

Sometimes you need to run (or debug) your cross-compiled code. This is easy, you can configure `multiarch/qemu-user-static`
to run non-native Docker images.

```bash
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
```

This registers all `qemu-*-static` interpreters under `/proc/sys/fs/binfmt_misc`. Now any RISC-V ELF you 
execute or even debug outside of Docker will automatically be interpreted by `qemu-riscv64-static`.

```bash
./hello 
Hello cross-compilation world!
```

Works like magic! You can also try `gdb hello` if you want to debug it.  
If you need a full-fledged container, here's how you can get a RISC-V Debian "sid" up and running:

```bash
docker run \
  --rm \
  -it \
  --platform=linux/riscv64 \
  -v "$PWD":/work \
  --workdir /work \
  riscv64/debian:sid \
  /bin/bash
```

You end up with a temporary, RISC-V-emulated Debian “sid” container, running Bash as root, with your host’s current
directory mounted at /work. When you exit the shell, the container is automatically destroyed. This lets you install
packages, compile or run RISC-V binaries, and edit files in your host directory — all inside a genuine RISC-V
user-mode environment on your x86_64 machine.

Enjoy!
