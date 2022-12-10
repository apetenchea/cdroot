---
title: Time in Distributed Systems
date: 2022-11-22 16:31:54
tags:
- "Distributed Systems"
---

Operating Systems do a pretty good job at keeping track of time. When on the same machine, all running processes have a
single source of truth: the system clock (also known as "kernel clock"). This is a software counter based on the timer
interrupt. On Linux systems, it counts the number of seconds elapsed since Jan 1, 1970 (UTC).
This can only function while the machine is running, so there's another clock (the
[RTC](https://en.wikipedia.org/wiki/Real-time_clock)), which keeps track of time while the system is turned off.
At boot time, the system clock is initialized from the RTC.  
Keeping track of time is essential for scheduling events, measuring performance, debugging, etc. In distributed
systems, physical clocks can be used to count seconds, while a logical clocks can be used to count events.

## Physical Clocks

![Physical Clock](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/time-in-distributed-systems/media/physical-clock.png)

These can be found in any computer or mobile phone. The most commonly used type of physical clocks are quartz clocks,
because they're really cheap and provide decent accuracy. The timekeeping component of every quartz clock is a [quartz
crystal resonator](https://en.wikipedia.org/wiki/Quartz_clock#/media/File:Inside_QuartzCrystal-Tuningfork.jpg),
in the shape of a musician's tuning fork. Via an electronic circuit, a battery sends electricity to the crystal,
causing its prongs to vibrate at a certain frequency, generally 32768 Hz, or in other words, 32768 times per second.
Counting the number of vibration allows us to count the number of seconds elapsed. This is not that relevant for a
distributed system, but I find it very interesting.     

![Atom](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/time-in-distributed-systems/media/atom.png)

When accuracy becomes a problem, people turn to atomic clocks. Without getting into much detail, atomic clocks are based
on the quantum mechanical properties of the caesium atom. Thus, we are able to count
[atomic seconds](https://www.britannica.com/technology/atomic-second), which are the accepted time unit by the
[IS](https://en.wikipedia.org/wiki/International_System_of_Units). Atomic clocks are way more expensive and therefore,
not as widespread as quartz clocks.     
For our perspective, a second is roughly the 31.557.600<sup>th</sup> part of a year. We think of a year as the time it takes to our
planet to complete one revolution around the sun. While our interpretation of a second works nicely in day-to-day
life, the speed of Earth is not constant. [Coordinated Universal Time](https://en.wikipedia.org/wiki/Coordinated_Universal_Time)
(or UTC) is based on atomic time, but includes corrections to account for variations in Earth's rotation. [Such
adjustments](https://en.wikipedia.org/wiki/Leap_second) to UTC complicate software that needs to work with time and
dates.

### Network Time Protocol

Even if most computers don't come with atomic clocks, they can periodically retrieve the current time from a server that
has one. Unfortunately, in order to correctly adjust the clock, one has to take network latency and processing time into
account. This is what the [Network Time Protocol](https://datatracker.ietf.org/doc/html/rfc5905) (NTP) is for.
Just like HTTP operates over TCP, NTP operates over [UDP](https://www.ietf.org/rfc/rfc768.txt). The port on which an NTP
server listens for requests is 123.

<video controls>
  <source src="https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/time-in-distributed-systems/media/NtpIllustration.mp4" type="video/mp4">
Your browser does not support the video tag.
</video> 

When the client requests the current time from a server, it passes its own time, *t<sub>1</sub>*, with the request. The server
records time *t<sub>2</sub>*, when it received the request. Now, *t<sub>2</sub>-t<sub>1</sub>* will be used
to represent the network delay of the client request. After processing the request (i.e. fetching the current time and serializing it),
the server records *t<sub>3</sub>* and sends the response back to the client, which is going to use *t<sub>3</sub>-t<sub>2</sub>*
to deduce the processing time. Eventually, when the client receives the response, it sets *t<sub>4</sub>* as the response
time, and therefore knows that it spent *t<sub>4</sub>-t<sub>3</sub>* time travelling back through the network.  
Now, the client doesn't have an immediate answer to the current time question, but it has these 4 timestamps to work with.
It has to calculate the difference between its clock and the server's clock, called the *clock skew*, denoted by *Θ* (Greek
letter Theta). The first step is to get estimate the network delay, denoted by *Δ* (Greek letter Delta). This is easy,
because it can subtract the processing time from the total round-trip time.

$$
\begin{split}
\Delta = (t_4 - t_1) - (t_3 - t_2)
\end{split}
$$

Sometimes the request delay can be longer than the response delay, or vice versa. Since we have Δ as the total network
delay, a fair estimate of the response time would be half of that, *Δ/2*.  
The last recorded time on the server is *t<sub>3</sub>*, but it takes a network response to get that, so the current
time when the client receives *t<sub>3</sub>* can be estimated as *t<sub>3</sub>+Δ/2*. The client can compare that
to its own version of the current time, *t<sub>4</sub>*, and get the clock skew:

$$
\begin{split}
\Theta = t_3 + \frac{\Delta}{2} - t_4
\end{split}
$$

Both network latency and processing time can vary considerably. For that reason, the client sends several requests to
the server and applies statistical filters to eliminate outliers. In the end, after it has a final estimation of the
clock skew, the client tries to apply the correction to its own clock. However, if the skew is larger than 1000 seconds,
it may panic and do nothing, waiting for a human operator to resolve the issue.  

How can we apply this protocol at large scale? There are over 2 billion computers in the world, and only a tiny fraction
of these have atomic clocks, out of which an even tinier fraction are being used as NTP servers.
In order to not flood these with requests, there are multiple layers of servers that maintain the current time. The ones
in the first layer, called primary servers, receive the timestamp from an authoritative clock source, such as an atomic
clock or a GPS signal. All other layers, composed of secondary servers, maintain their clock by communicating with
multiple servers from the layer above. In the end, clients can reliably obtain the current time from the servers in the last layer.

### Monotonic clocks

Real-time clocks, such as the system time displayed by the `date` command, can be subject to various adjustments, for
example, due to NTP. When trying to get a good measurement of the time difference between events that happened on the same machine,
such as the execution time of a function, monotonic clocks are much better suited than real-time clocks. These clocks offer
better resolution (possibly nanoseconds) and are not affected by NTP. Their timestamp would not make sense across different
machines, as it's not relative to a predefined date and can be reset when the computer reboots, but, they still keep
track of the time elapsed, and most importantly, always move forward.
Every OS has some way of tracking monotonic time, and programmings languages usually have some abstraction over this.
In C++, there's [std::chrono::steady_clock](https://en.cppreference.com/w/cpp/chrono/steady_clock) for measuring time
intervals. 

```cpp
#include <chrono>

auto get_exec_time(auto&& lambda) {
    using namespace std::chrono;
    steady_clock::time_point start = steady_clock::now();
    lambda();
    steady_clock::time_point end = steady_clock::now();
    return duration_cast<nanoseconds>(end - start).count();
}
```

## References and Further Reading

* [tldp.org](https://tldp.org/HOWTO/Clock-2.html)
* [chelseaclock.com](https://www.chelseaclock.com/blog/how-do-quartz-clocks-work)
* [wikipedia.org/wiki/Quartz_clock](https://en.wikipedia.org/wiki/Quartz_clock)
* [Distributed Systems Lectures by Dr Martin Kleppmann](https://www.cl.cam.ac.uk/teaching/2122/ConcDisSys/materials.html)
* [pngwing.com](https://www.pngwing.com)
* [APNIC](https://labs.apnic.net/index.php/2014/03/10/protocol-basics-the-network-time-protocol/)
