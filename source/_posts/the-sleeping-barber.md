---
title: The Sleeping Barber
date: 2023-04-22 21:09:29
tags:
- Programming
---

![Sleeping barber](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/the-sleeping-barber/media/sleeping-barber.png)

_The Sleeping Barber_ is a classic synchronization problem. It was used by [Edsger W. Dijkstra](https://en.wikipedia.org/wiki/Edsger_W._Dijkstra)
as an example in [his lecture notes](https://www.cs.utexas.edu/users/EWD/ewd01xx/EWD123.PDF), illustrating the use of semaphores.
> There is a barbershop with a separate waiting room.
> The waiting room has an entry and next to it an exit to the room with the barber's chair.
> When the barber has finished a haircut, he opens the door to the waiting room and inspects it.
> If the waiting room is not empty, he invites the next customer,
> otherwise he goes to sleep in one of the chairs in the waiting room.
> The complementary behaviour of the customers is as follows: when they find zero or more customers in the waiting room,
> they just wait their turn, when they find, however, the sleeping barber — they wake him up.
