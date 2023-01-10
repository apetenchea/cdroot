---
title: Time in Distributed Systems
date: 2022-11-22 16:31:54
tags:
- "Distributed Systems"
---

Operating Systems do a pretty good job at keeping track of time. When on the same machine, all running processes have a
single source of truth: the system clock (also known as "kernel clock"). This is a software counter based on the timer
interrupt. On Linux systems, it counts the number of seconds elapsed since Jan 1, 1970 (UTC).
This can only function while the machine is running, so there's another clock, the real-time clock
([RTC](https://en.wikipedia.org/wiki/Real-time_clock)), which keeps track of time while the system is turned off.
At boot time, the system clock is initialized from the RTC.  
Keeping track of time is essential for scheduling events, measuring performance, debugging, etc. In distributed
systems, physical clocks can be used to count seconds, while logical clocks can be used to count events.

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

When accuracy becomes a problem, people turn to atomic clocks. Without getting into too much detail, atomic clocks
are based on the quantum mechanical properties of the caesium atom. Thus, we are able to count
[atomic seconds](https://www.britannica.com/technology/atomic-second), which are the accepted time unit by the
[IS](https://en.wikipedia.org/wiki/International_System_of_Units). Atomic clocks are way more expensive and therefore,
not as widespread as quartz clocks.     
From our perspective, a second is roughly the 31.557.600<sup>th</sup> part of a year. We think of a year as the time it takes for our
planet to complete one revolution around the sun. While our interpretation of a second works nicely in day-to-day
life, the speed of Earth is not constant. [Coordinated Universal Time](https://en.wikipedia.org/wiki/Coordinated_Universal_Time)
(or UTC) is based on atomic time, but includes corrections to account for variations in Earth's rotation. [Such
adjustments](https://en.wikipedia.org/wiki/Leap_second) to UTC complicate software that needs to work with time and
dates.

### Network Time Protocol

Even if most computers don't come with atomic clocks, they can periodically retrieve the current time from a server that
has one. Unfortunately, in order to correctly adjust the clock, one has to take network latency and processing time into
account. This is what the [Network Time Protocol](https://datatracker.ietf.org/doc/html/rfc5905) (NTP) is for.
Just like HTTP operates over [TCP](https://www.ietf.org/rfc/rfc793.txt), NTP operates over
[UDP](https://www.ietf.org/rfc/rfc768.txt). The port on which an NTP server listens for requests is 123.

<video controls>
  <source src="https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/time-in-distributed-systems/media/NtpIllustration.mp4" type="video/mp4">
Your browser does not support the video tag.
</video> 

When the client requests the current time from a server, it passes its own time, *t<sub>1</sub>*, with the request. The server
records time *t<sub>2</sub>*, the moment when it receives the request. Now, *t<sub>2</sub>-t<sub>1</sub>* will be used
to represent the network delay of the client request. After processing the request (i.e. fetching the current time and serializing it),
the server records *t<sub>3</sub>* and sends the response back to the client, which is going to use *t<sub>3</sub>-t<sub>2</sub>*
to calculate the processing time. Eventually, when the client receives the response, it sets *t<sub>4</sub>* as the response
time, and therefore knows that it spent *t<sub>4</sub>-t<sub>3</sub>* time travelling back through the network.  
Now, the client doesn't have an immediate answer to the current time in question, but it has these 4 timestamps to work with.
It has to calculate the difference between its clock and the server's clock, called the *clock skew*, denoted by *Θ* (Greek
letter Theta). The first step is to estimate the network delay, denoted by *Δ* (Greek letter Delta). This is easy,
because it can subtract the processing time from the total round-trip time.

$$
\begin{split}
\Delta = (t_4 - t_1) - (t_3 - t_2)
\end{split}
$$

Sometimes the request delay can be longer than the response delay, or vice versa. Since we have Δ as the total network
delay, a fair estimate of the response time would be half of that, *Δ/2*.  
The last recorded time on the server is *t<sub>3</sub>*, but it takes *Δ/2* for the client to receive that information,
so the current time, when the client gets *t<sub>3</sub>*, can be estimated as *t<sub>3</sub>+Δ/2*. Then, the client can subtract
from that its own version of the current time, *t<sub>4</sub>*, and obtain the clock skew, which represents how much the client has to
adjust its own clock in order to get back in line with the server's clock:

$$
\begin{split}
\Theta = t_3 + \frac{\Delta}{2} - t_4
\end{split}
$$

Unfortunately, network latency and processing time can vary considerably. For that reason, the client sends several requests to
the server and applies statistical filters to eliminate outliers. In the end, after it has a final estimation of the
clock skew, the client tries to apply the correction to its own clock. However, if the skew is larger than 1000 seconds,
it may panic and do nothing, waiting for a human operator to resolve the issue.  

How can this protocol be applied at large scale? There are over 2 billion computers in the world, and only a tiny fraction
of them are equipped with atomic clocks, out of which an even tinier fraction are being used as NTP servers.
In order to not flood these with requests, there are multiple layers of servers that maintain the current time. The ones
in the first layer, called primary servers, receive the timestamp from an authoritative clock source, such as an atomic
clock or a GPS signal. All other layers, composed of secondary servers, maintain their clock by communicating with
multiple servers from the layer above. In the end, clients can reliably obtain the current time from the servers in the last layer.

![NTP Layers](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/time-in-distributed-systems/media/ntp.jpg)

### Monotonic clocks

Real-time clocks, such as the system time displayed by the `date` command, can be subject to various adjustments, for
example, due to NTP. When trying to get a good measurement of the time difference between events that happened on the same machine,
such as the execution time of a function, monotonic clocks are much better suited than real-time clocks. These clocks offer
higher resolution (possibly nanoseconds) and are not affected by NTP. Their timestamp would not make sense across different
machines, as it's not relative to a predefined date and can be reset when the computer reboots, but they still keep
track of the time elapsed, and most importantly, their value is only ever increased.
Every OS has some way of tracking monotonic time, and programmings languages usually have some abstraction over that.
In C++, there's [std::chrono::steady_clock](https://en.cppreference.com/w/cpp/chrono/steady_clock) for measuring time
intervals. The following example illustrates how the execution time of a lambda function can be measured, using a
monotonic clock.

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

## Logical Clocks

The order in which two or more events have occurred, on a single machine, can be deduced from a monotonic clock.
However, this is not applicable to a distributed system, composed of multiple nodes.  
Imagine you're running a small database cluster, having only one coordinator and a DB-Server.
The coordinator is the node which the clients talk to. It knows where the data is located and coordinates cluster tasks,
such as the execution of queries. The DB-Server is the node where the data is actually hosted.
I borrowed the naming from [ArangoDB](https://www.arangodb.com/), but this is a widely used concept in databases.  
Consider two queries, we'll call them *Q<sub>1</sub>* and *Q<sub>2</sub>*, sent by the client in the following order:

**Q<sub>1</sub>**
```sql
INSERT {name: "foo", value: 1} INTO bar
```
**Q<sub>2</sub>**
```sql
FOR doc IN bar
    FILTER doc.name == "foo"
    UPDATE doc WITH {
        value: doc.value + 1
    } IN bar
```

*Q<sub>1</sub>* inserts a document with name *foo* and value 1 into collection *bar*. Then, *Q<sub>2</sub>* increments
the value of that document. When the coordinator receives *Q<sub>1</sub>*, it has to send a request to the DB-Server,
instructing it to insert the document. It then gets *Q<sub>2</sub>* and asks the DB-Server to update the same document,
based on the current value of the document. However, if the second request sent by the coordinator to the DB-Server
arrives faster than the first one, there will be no `{name: "foo", value: 1}` in the collection, because it
has not been inserted yet.

<video controls>
  <source src="https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/time-in-distributed-systems/media/CoordinatorIllustration.mp4" type="video/mp4">
Your browser does not support the video tag.
</video> 

We need to work out a way to fix this ordering issue. How can we make sure that *Q<sub>1</sub>* gets executed before
*Q<sub>2</sub>*? One thought is to make it the responsibility of the client to synchronize its queries.
It would have to wait for the *Q<sub>1</sub>* response to get back, before it can send *Q<sub>2</sub>*. However,
this moves the problem from the database to the client. Coming from the example above, we thought of the "client" as
a single node, capable of sending only one query at a time. In reality, that could become a distributed system itself,
or otherwise put, we might be dealing with multiple clients. So, the synchronization problem still exists, as now all
these clients have to synchronize the queries within themselves.  
Getting back to the database cluster, it could be composed of multiple coordinators and DB-Servers, which need to agree
on the order of queries. What if two clients contact two different coordinators, trying to modify the same document,
such as both coordinators end up contacting the same DB-Server? While the queries could reach the two coordinators
seconds apart, once forwarded, they might arrive at the DB-Server simultaneously.
We could configure all nodes to send a timestamp along with every request. Hence, in our example, the DB-Server
could compare the timestamps sent by these coordinators and deduce the order in which the requests have been sent.
The weakness of this approach is that it heavily relies on each node's physical clock. Let's consider that coordinator
*A* sends timestamp *t<sub>1</sub>*, while coordinator *B* sends timestamp *t<sub>2</sub>*.
Although coordinator *A* is the first to send the request, its clock could be a ahead of *B's*,
which causes *t<sub>1</sub> > t<sub>2</sub>*, making it appear that *A's* request was sent first.
Given enough time, all clocks are going to drift apart, and we would never
be sure that they're **perfectly** in sync, even with the clock synchronization performed by NTP.
One skewed clock is enough to mess up the entire cluster. Therefore, the more nodes you add to the system,
the more fragile this approach becomes.

### Causality

[Dr. Martin Kleppmann](https://martin.kleppmann.com/) beautifully defined, in one of his lectures, the concepts presented here.
*Causality considers whether information could have flowed from one event to another, and thus whether one event may have
influenced another.* An even is something happening at a node, such as sending or receiving a message.
Given two events, *A* and *B*, when can we say that *A* causes (or influences) *B*?

* When *A* **happens before** *B*, we can say *A* **might have caused** *B*
* When *A* and *B* are **concurrent**, we can say that *A* **cannot have caused** *B*

This is probably not what one might've expected from the description of causality. Essentially, it can rule out the
existence of causality between two events, but it cannot confirm it.

#### Happens-before relation

How can we check, given two events, *A* and *B*, whether *A* happened before *B* (noted *A &rarr; B*)?

Unlike with the relation of causality, there's a few ways to confirm this one for sure.
* First of all, if the events occurred on the same node, we could use a
monotonic clock to compare their times of occurrence.
* Secondly, if *A* is the sending of some message and *B* is the
receipt of it, then *A* must have occurred before *B*, because a message cannot be received unless it was sent in the first
place.
* Lastly, if there's another event *C* such that *A* happens before *C* and *C* happens before *B*, it's obvious that *A*
happens before *B*. Using the mathematical notation, from *A &rarr; C* and *C &rarr; B*, we can deduce that *A &rarr; B*.

These are the ways in which one could confirm the existence of a happens-before relation between two events
in a distributed system.

#### Concurrent events

When reasoning about the order of two events, *A* and *B*, we could come up to any of these conclusions:

1. *A* happens before *B*: *A &rarr; B*
2. *B* happens before *A*: *B &rarr; A*
3. None of the above, which means that *A* and *B* are concurrent: *A || B*

Looking back at how we defined causality, two concurrent events are independent; they could not have caused each other.

## References and Further Reading

* [tldp.org](https://tldp.org/HOWTO/Clock-2.html)
* [chelseaclock.com](https://www.chelseaclock.com/blog/how-do-quartz-clocks-work)
* [wikipedia.org/wiki/Quartz_clock](https://en.wikipedia.org/wiki/Quartz_clock)
* [Distributed Systems Lectures by Dr Martin Kleppmann](https://www.cl.cam.ac.uk/teaching/2122/ConcDisSys/materials.html)
* [pngwing.com](https://www.pngwing.com)
* [APNIC](https://labs.apnic.net/index.php/2014/03/10/protocol-basics-the-network-time-protocol/)
