---
title: perf
date: 2025-05-03 16:56:48
tags:
- Programming
- Linux
---

Perf is a powerful for profiling and tracing Linux applications. It comes with low overhead and directly uses kernel
hooks and performance counters to gather data. It's part of my toolkit for performance analysis, so I'm going to talk
a bit about how I use it.

## Installation

I am on Debian Sid.

```bash
sudo apt update
sudo apt install linux-perf
```

You can modify `perf` setting in `/etc/sysctl.d/99-perf.conf` (create it if it doesn't exist). For example, mine looks
like this:

```
# 0 = allow user-level + system-wide profiling
# 1 = user-level only (no system-wide)
kernel.perf_event_paranoid = 0

# 0 = show full kernel symbols in perf data
kernel.kptr_restrict       = 0
```

The reason to prefix the file with `99-` is to make sure it is loaded last, so it overrides any other settings that
might be set by others.

You can check whether `perf` works by simply checking it over the `ls` command:

```bash
perf stat ls
```

## Sample Program

Let's take a real-world example: [bzip2](https://gitlab.com/bzip2/bzip2).

It's pretty easy to build, however note that I'm not following the official instructions here, but I'm rather doing it
just for the sake of demonstrating some key points in the profiling process.  
Adding debug symbols always helps with the analysis, so I add `-g`. Whenever I profile my code, I always build it to be
as close as it can get to the production version, and one of the most common flags used is `-O2`. Unless you have a very
specific reason for it, please don't waste your time profiling unoptimized code. You don't want to work on a problem
that doesn't exist in production.

```bash
git clone --branch bzip2-1.0.8 --single-branch https://gitlab.com/bzip2/bzip2.git
cd bzip2
make CFLAGS="-O2 -g"
```

## Profiling

Let's create a 500MB blob of random data and compress it with `bzip2`:

```bash
dd if=/dev/urandom of=big.bin bs=1M count=500
```

Profiling is as simple as running the following command:

```bash
perf record --max-size 10G --call-graph dwarf -- ./bzip2 -k big.bin
```

- `record` - Launches the "record" subcommand, which runs the program and collects performance data.
- `--max-size 10G` - Sets the maximum size of the perf.data file to 10GB. It will stop collecting further samples rather
    than grow out of bound.
- `--call-graph dwarf` - Capture full stack traces (call graphs) for each sample
    using [DWARF-based unwinding](https://inria.hal.science/hal-02297690/file/main.pdf). This gives you precise
    function-call trees in the later perf report or flame-graph, at the cost of a bit more overhead and larger output.
- `--` - Indicates the end of `perf` options and the beginning of the command to be profiled.
- `./bzip2 -k big.bin` - Runs the `bzip2` program with input `big.bin`. The `-k` argument keeps the original `big.bin`
    so you can rerun without re-dd’ing.

If you want to profile the program only after a specific point, you can use the `-p` option to attach to a running process:

```bash
perf record --max-size 10G --call-graph dwarf -p <PID>
```

Finally, you can view the results with:

```bash
perf report
```

## Hotspot

### Installation

If you're looking for something prettier, you can use [hotspot](https://github.com/KDAB/hotspot).
It's a GUI for `perf` that allows you to visualize the data in a more user-friendly way. I personally prefer it over the
default `perf report`, but it's a matter of taste. Installing it should be as easy as:

```bash
sudo apt update
sudo apt install hotspot
```

Unfortunately, I experienced some problems lately because of missing dependencies (April 2025). Turns out that one of its
dependencies is `policykit-1`, which is no longer available. However, this is just a meta package to install `pkexec` and
`polkitd`, which are the actual programs that do the work. Knowing, we can trick the package manager into thinking we have
installed `policykit-1` by creating a dummy package, while we actually install the "real" dependencies. This is a bit of a
hack, but it works.

```bash
sudo apt update
sudo apt install equivs # install equivs

equivs-control policykit-1 # generate template
```

Edit the `policykit-1` template, uncommenting "Version" and "Depends".

```
Package: policykit-1
Version: 124-3
Depends: pkexec,polkitd
```

Then build and install the package:

```bash
equivs-build policykit-1
sudo apt install ./policykit-1_124-3_amd64.deb
```

Then you should be able to install `hotspot` as if nothing happened:

```bash
sudo apt install hotspot
```

### Data Visualization

Once you have `hotspot` installed, you can run it in the same directory where you have the `perf.data` file.

```bash
hotspot
```

You may start from the summary view, which shows you the most expensive functions in your program.

![Summary View](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/perf/media/hotspot-summary.png)

Here we can see the most expensive function is `generateMTFValues`, where the program spends about half of the time.  
One of my favourite features of `hotspot` is the Flame Graph, which shows the call graph in a clear and concise way. You
can explore it interactively in the application, or export it as an SVG file (View -> Export -> Flame Graph).

![Flame Graph](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/perf/media/hotspot-flamegraph.svg)

- BZ2_blockSort - 27.9% cost
- BZ2_compressBlocksendMTFValues - 9.09% cost
- generateMTFValues - 54.3% cost

If I were to optimize this code, I would start with `generateMTFValues`, since it has the highest cost.

## Other tools

Generally, `perf` is all I need, but it only works on Linux. Here are a few alternatives that are available on other
platforms.

1. [Intel VTune](https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtune-profiler.html)

    I used it in the past, and it's a great alternative to `perf` on Windows. The disadvantage is that it requires an Intel
    CPU (sorry AMD users). I especially like the GUI, which I find easy to navigate. However, it's bulkier than `perf`, and
    I don't see a clear advantage over it on Linux. I would recommend to look into it if you are on Windows and have an
    Intel CPU.
2. [Clion Profiler](https://www.jetbrains.com/help/clion/cpu-profiler.html)

    This is a built-in profiler in Clion, which has the advantage of being integrated into the IDE. On Linux it uses `perf`
    under the hood, so I usually prefer to use `perf` directly. On MacOS it uses [DTrace](https://www.brendangregg.com/dtrace.html),
    which is not bad. I have only used it a few times, but if you are a Clion user on MacOS and want a glimpse of what
    is going on in your code, it's worth checking out.
3. [Instruments](https://developer.apple.com/tutorials/instruments)
 
    Never used it, but it seems like a good alternative on MacOS, especially if you don't use Clion profiler.

## References and Further Reading

- [brendangregg.com](https://www.brendangregg.com/perf.html)
- [policykit-1](https://github.com/waydroid/waydroid/issues/1484)
- [Using perf probe to measure execution time of user-space code on Linux](https://bristot.me/using-perf-probe-to-measure-execution-time-of-user-space-code-on-linux/)
