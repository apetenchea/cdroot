---
title: The Sleeping Barber
date: 2023-04-22 21:09:29
tags:
- Programming
---

![Sleeping barber](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/the-sleeping-barber/media/sleeping-barber.png)

_The Sleeping Barber_ is a classic synchronization problem. It was used by [Edsger W. Dijkstra](https://en.wikipedia.org/wiki/Edsger_W._Dijkstra)
as an example in [his lecture notes](https://www.cs.utexas.edu/users/EWD/ewd01xx/EWD123.PDF), illustrating the use of semaphores.
> Imagine a barber shop that has a waiting room, separated from the room where the barber works.
> The waiting room has an entry and next to it an exit to the room with the barber's chair.
> When the barber has finished a haircut, he opens the door to the waiting room and inspects it.
> If the waiting room is not empty, he invites the next customer,
> otherwise he goes to sleep in one of the chairs in the waiting room.
> The complementary behaviour of the customers is as follows: when they find zero or more customers in the waiting room,
> they just wait their turn, when they find, however, the sleeping barber — they wake him up.

![Barber Shop](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/the-sleeping-barber/media/barber-shop.svg)

In order to shape the problem further, we are going to assume that the barber shop has a limited number of chairs
in the waiting room. If a customer enters the shop and all chairs are occupied, he leaves the shop.

## Race conditions

Although the concept may be familiar, I find it useful to start by giving a brief explanation of what exactly a race condition is,
as it brings us into a problem-solving mindset. A race condition may occur when two or more processes access and change
shared data simultaneously. **The outcome of the program depends on the relative timing of these processes,
which can cause unexpected results.** When the correct functioning of the system relies on a specific order of execution, but the
order in which the operations occur is unpredictable, we have a race condition. In our case, the barber and the customers
are processes that access and change the same data - the waiting room.  
While it may not be immediately apparent, the barber shop is affected by two race conditions:
1. **The barber may fall asleep while there are customers in the waiting room.** Imagine a customer walks in to
    an empty waiting room, an indication that the barber is currently giving a haircut. As there are no other clients in 
    the waiting room, the customer proceeds towards one of the chairs. In the meantime, the barber finishes 
    the haircut and goes to check the waiting room. If the customer is _slow_, he might not make it to his seat _before_
    the barber checks the waiting room. In that case, the barber gets to inspect the waiting chairs _first_, finds them empty, and comes to the
    conclusion that nobody is waiting for him. Hence, he falls asleep, leaving the slow customer waiting forever. Eventually, the
    customer will sit, waiting indefinitely for the barber to invite him into the working room.
2. **Two or more customers may enter the waiting room and try to sit down at the same time.** If there's only one free chair available,
    they end up bumping into each other indefinitely, like stuck characters in a video game.

## Solution

We need to synchronize access to the waiting room, so that only one process can access it at a time. We can achieve this
with a simple mutex. Whenever a process (a customer or the barber) wants to check and modify the state of the shared resource
(the waiting room), it has to acquire the mutex first. When it's done, it releases the mutex, allowing other processes to
access the resource.

