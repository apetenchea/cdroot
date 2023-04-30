---
title: The Sleeping Barber
date: 2023-04-22 21:09:29
tags:
- Programming
---

![Sleeping barber](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/the-sleeping-barber/media/sleeping-barber.png)

_The Sleeping Barber_ is a classic synchronization problem. It was used by [Edsger W. Dijkstra](https://en.wikipedia.org/wiki/Edsger_W._Dijkstra)
as an example in [his lecture notes](https://www.cs.utexas.edu/users/EWD/ewd01xx/EWD123.PDF), illustrating the use of semaphores.
> Imagine a barbershop that has a waiting room, separated from the room where the barber works.
> The waiting room has an entry and next to it an exit to the room with the barber's chair.
> When the barber has finished a haircut, he opens the door to the waiting room and inspects it.
> If the waiting room is not empty, he invites the next customer,
> otherwise he goes to sleep in one of the chairs in the waiting room.
> The complementary behaviour of the customers is as follows: when they find zero or more customers in the waiting room,
> they just wait their turn, when they find, however, the sleeping barber — they wake him up.

![Barber Shop](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/the-sleeping-barber/media/barber-shop.svg)

In order to shape the problem further, we are going to assume that the barbershop has a limited number of chairs
in the waiting room. If a customer enters the shop and all chairs are occupied, he leaves the shop. Furthermore, before
going to sleep, the barber sets an alarm clock that wakes him up when it's time to close the shop.

## Race conditions

Although the concept may be familiar, I find it useful to start by giving a brief explanation of what exactly a race condition is,
as it brings us into a problem-solving mindset. A race condition may occur when two or more processes access and change
shared data simultaneously. **The outcome of the program depends on the relative timing of these processes,
which can cause unexpected results.** When the correct functioning of the system relies on a specific order of execution, but the
order in which the operations occur is unpredictable, we have a race condition. In our case, the barber and the customers
are processes that access and change the same data - the waiting room.  
While it may not be immediately apparent, the barbershop is affected by two race conditions:
1. **The barber may fall asleep while there are customers in the waiting room.** Imagine a customer walks in to
    an empty waiting room, an indication that the barber is currently giving a haircut. As there are no other clients in 
    the waiting room, the customer proceeds towards one of the chairs. In the meantime, the barber finishes 
    the haircut and goes to check the waiting room. If the customer is _slow_, he might not make it to his seat _before_
    the barber checks the waiting room. In that case, the barber gets to inspect the waiting chairs _first_, finds them empty, and comes to the
    conclusion that nobody is waiting for him. Hence, he falls asleep, leaving the slow customer waiting forever. Eventually, the
    customer will sit, waiting indefinitely for the barber to invite him into the working room.
2. **Two or more customers may enter the waiting room and try to sit down at the same time.** If there's only one free chair available,
    they end up bumping into each other indefinitely, like stuck characters in a video game.

## Classic solution

We need to synchronize access to the waiting room, so that only one process can access it at a time. We can achieve this
with a simple mutex. Whenever a process (a customer or the barber) wants to check and modify the state of the shared resource
(the waiting room), it has to acquire the mutex first. When it's done, it releases the mutex, allowing other processes to
access the resource. That would be the equivalent of a sliding door, which only allows one person in or out at a time.

![Sliding Door](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/the-sleeping-barber/media/SlidingDoorIllustration.gif)

As for "waking up the barber" and "waiting for the barber to finish a haircut", we can use a
[C++20 semaphore](https://en.cppreference.com/w/cpp/thread/counting_semaphore).

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/the-sleeping-barber/code/classic-solution.cpp 17 22 %}

When the barber comes to work, he opens the shop and executes the `barber` function. Note that we had to use
[try_acquire_for](https://en.cppreference.com/w/cpp/thread/counting_semaphore/try_acquire_for), checking periodically
that the shop is still open. Otherwise, if the barber doesn't get any customers before closing time, he never wakes up,
thus leaving the shop open indefinitely.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/the-sleeping-barber/code/classic-solution.cpp 41 55 %}

When customers arrive, they execute the `customer` function. The customer does not have to loop, as he only needs to
get a haircut and then leaves. Notice that there's an artificial delay introduced before a customer enters the shop, as
to randomize the order in which customers arrive.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/the-sleeping-barber/code/classic-solution.cpp 60 74 %}

The full code, together with the `main` function I used for testing, can be found
[here](https://github.com/apetenchea/cdroot/blob/master/source/_posts/the-sleeping-barber/code/classic-solution.cpp).

## Using only atomics

Since C++20, it is possible to solve the problem using only [atomics](https://en.cppreference.com/w/cpp/atomic/atomic).
We no longer need the mutex nor any semaphores. However, the barber will have to rely on his best friend coming in to
wake him up before the shop closes, instead of using an alarm clock.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/the-sleeping-barber/code/atomic-solution.cpp 15 18 %}

The barber can call [wait](https://en.cppreference.com/w/cpp/atomic/atomic/wait) on the _atomic_int_, which will block
until a customer comes in and calls [notify_one](https://en.cppreference.com/w/cpp/atomic/atomic/notify_one) on it. For a comparison, this
if very similar to the way [Object](https://docs.oracle.com/javase/8/docs/api/java/lang/Object.html) can be used in Java
as a basic synchronization mechanism. This is the root of the class hierarchy, so essentially every object in Java can
provide this functionality. However, `wait` and `notify_one` are not enough to solve the problem. We need the guarantee
that any modifications to `waiting` and `bs` happen atomically.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/the-sleeping-barber/code/atomic-solution.cpp 37 47 %}

As for the customers, we have to be careful not to end up with more of them than there are waiting chairs, when updating the state
of the waiting room. Since `waiting` is no longer protected by a mutex, two or more clients may attempt to modify it
at the same time. Although the updates themselves would happen atomically, the comparison at line _56_ could evaluate to
`true` for all of them. However, there is no guarantee that between the comparison and the update, other customers won't
come in and fill up the waiting room. Hence, we have to use a [compare_exchange](https://en.cppreference.com/w/cpp/atomic/atomic/compare_exchange)
function, which only updates the value of `waiting` if it remains unchanged. Note that if the compare-exchange operation succeeds,
it does not mean that everyone stood still in the waiting room. Other customers are still free to come and go in the meantime,
it's just that we're making sure the waiting room is not full when we try to sit down. However, this
[ABA problem](https://en.wikipedia.org/wiki/ABA_problem) will not affect the correct functioning of the barbershop.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/the-sleeping-barber/code/atomic-solution.cpp 52 69 %}

Find the complete cpp file [here](https://github.com/apetenchea/cdroot/blob/master/source/_posts/the-sleeping-barber/code/atomic-solution.cpp).

## FIFO barbershop

In the previous solutions, the customers are not necessarily served in the order they arrive. For example, if the barber
comes to the waiting room and finds it full, he picks a random customer to invite into the working room. However, we
can easily modify the classic code to make sure the customers are served in first-in-first-out order. We need maintain
a queue of customers waiting to get a haircut. Each customer has its own semaphore, which is used to notify him when
the haircut is done. Access to the queue is synchronized through a mutex, same as we did before with the waiting room.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/the-sleeping-barber/code/fifo-solution.cpp 19 25 %}

The barber picks the first customer in the queue and invites him into the working room.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/the-sleeping-barber/code/fifo-solution.cpp 44 59 %}

The customer takes a sit in the waiting queue and waits for the barber to finish the haircut. Both the barber and the customer
share a pointer to the same semaphore, which is unique to the customer. This way, the barber can use the semaphore to
signal a particular customer that the haircut is done.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/the-sleeping-barber/code/fifo-solution.cpp 64 79 %}

See the full code [here](https://github.com/apetenchea/cdroot/blob/master/source/_posts/the-sleeping-barber/code/fifo-solution.cpp).

## Catching data-races with TSan

[Clang's ThreadSanitizer (TSan)](https://clang.llvm.org/docs/ThreadSanitizer.html) is a tool that detects data races
and other threading-related issues at runtime. It is a very useful tool, consisting of a compiler instrumentation
module and a run-time library. It can help us find bugs that are very hard to detect otherwise. To use ThreadSanitized
with Clang, you need to enable it by adding the `-fsanitize=thread` flag during compilation.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/the-sleeping-barber/code/data-race.cpp %}

When running it, TSan prints the following warning (I trimmed it a bit for the sake of brevity):
```
==================
WARNING: ThreadSanitizer: data race (pid=2206)
  Write of size 4 at 0x5637e35656ac by thread T2:
    #0 increment() <null> (data-race+0xd4421) ...
    #1 std::thread::_State_impl<std::thread::_Invoker<std::tuple<void (*)()> > >::_M_run() <null> (data-race+0xd46a9) ...
    #2 <null> <null> (libstdc++.so.6+0xd44a2) ...

  Previous write of size 4 at 0x5637e35656ac by thread T1:
    #0 increment() <null> (data-race+0xd4421) ...
    #1 std::thread::_State_impl<std::thread::_Invoker<std::tuple<void (*)()> > >::_M_run() <null> (data-race+0xd46a9) ...
    #2 <null> <null> (libstdc++.so.6+0xd44a2) ...

  Location is global 'shared_data' of size 4 at 0x5637e35656ac (data-race+0x14fb6ac)
  ...
==================
Shared data: 200000
ThreadSanitizer: reported 1 warnings
```

It reported a data-race that involves two threads, _T1_ and _T2_, both trying to modify the same global location, _shared_data_.
The essential information is at lines _4_, _9_ and _13_. These indicate the places from which the threads are accessing the
shared data (in this case, both do it from the `increment` function), and the location of the shared data itself (a
global variable).  
Implementing a fix is simple, as we just have to declare _shared_data_ as `std::atomic_int`, and the warning is gone.
The point was to illustrate the ease with which one can make use of TSan in order to check for races in multi-threaded
code. Note that using it may significantly slow down the execution of the program and introduce significant memory overhead.
Nevertheless, it's generally worth it during the development and testing phase.

## References and Further Reading

* [Allen B. Downey - The Little Book of Semaphores](https://greenteapress.com/wp/semaphores/)
* [E. W. Dijkstra - EWD123](https://www.cs.utexas.edu/users/EWD/ewd01xx/EWD123.PDF)
* [Tanenbaum - The Sleeping Barber Problem](http://web.cecs.pdx.edu/~harry/Blitz/OSProject/p3/SleepingBarberProblem.pdf)

