---
title: Coding Standards
date: 2021-10-07 20:47:53
tags: 
- Programming
---

A coding standard is a set of rules used to maintain a certain level of quality within a software project.
Put otherwise, it's just a convention between programmers, regarding the way they should write code.

## Why is it important?

### Consistency

As with all standards, coding standards (or guidelines), exist to ensure some kind of consistency between
software components. Two or more developers might work on totally separate parts of a codebase, but in the end
everything must come together as a whole. A common guideline could indicate whether is it ok to use the `asm` statement
in order to mix assembly instructions with C code, or whether is it ok to use exceptions. The latter is sometimes quite a
debated topic within the C++ community, so let's take that as a practical example.  
While exceptions provide an elegant way of handling failures, they can distort the natural control flow of a
program, making it hard to debug and maintain. But if you ain't gonna use exceptions, you need another way of recovering
when things flop, so you'll probably be looking at error codes. This approach has worked fine for huge projects, such as
the [Linux Kernel](https://github.com/torvalds/linux), but it requires lots of [bookkeeping](https://man7.org/linux/man-pages/man3/errno.3.html).
Without proper documentation, error codes can quickly become just some random integers that no one understands.  
Say two teams work on different data structures: one writes the *set* module, while the other maintains the *list* module.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/coding-standards/code/exceptions_bad.cpp %}

Using these classes together becomes an error prone task. Especially for a newcomer on the codebase, it is not at all clear
when a function call might cause the program to crash with an exception or return an error code. Now imagine having a few
thousand lines of code written like that. With some specifiers and a bit of extra care, the code would look something like this:

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/coding-standards/code/exceptions_better.cpp %}

That would still be less readable, which takes us to another important reasong for using a coding standard: readability.
