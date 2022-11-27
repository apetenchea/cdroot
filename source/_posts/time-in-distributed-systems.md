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

## References

* [tldp.org](https://tldp.org/HOWTO/Clock-2.html)
* [chelseaclock.com](https://www.chelseaclock.com/blog/how-do-quartz-clocks-work)
* [wikipedia.org/wiki/Quartz_clock](https://en.wikipedia.org/wiki/Quartz_clock)
* [Distributed Systems Lectures by Dr Martin Kleppmann](https://www.cl.cam.ac.uk/teaching/2122/ConcDisSys/materials.html)
* [pngwing.com](https://www.pngwing.com)
