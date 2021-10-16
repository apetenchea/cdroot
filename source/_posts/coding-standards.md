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
program, making it hard to debug and maintain. But if you aren't gonna use exceptions, you need another way of recovering
when things flop, so you'll probably be looking at error codes. This approach has worked fine for huge projects, such as
the [Linux Kernel](https://github.com/torvalds/linux), but it requires lots of [bookkeeping](https://man7.org/linux/man-pages/man3/errno.3.html).
Without proper documentation, error codes can quickly become just some random integers that no one understands.
Clearly, both approaches have their pros and cons, while the worst possible scenario happens when you combine them.  
Say two teams work on different data structures: one writes the *set* module, while the other maintains the *list* module.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/coding-standards/code/exceptions_bad.cpp %}

Using these classes together becomes an error prone task. Especially for a newcomer on the codebase, it is not at all clear
when a function call might cause the program to crash with an exception or return an error code. Now imagine having a few
thousand lines of code written like that. With some specifiers and a bit of extra care, the code would look something like this:

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/coding-standards/code/exceptions_better.cpp %}

That would still be hard to read, which takes us to another important reasong for using a coding standard: readability.

### Readability

Unless you're competing in the [IOCCC](https://www.ioccc.org/), having a clean codebase can make a day's work more enjoyable.
Most software is built on existing software. Far more time is spent maintaining, upgrading and debugging existing code than is
ever spent on creating new work. Take a look at the following code:

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/coding-standards/code/terse_code.cpp %}

It evaluates an arithmetic expression, such as `1+2*3`. Although it works, it would be quite difficult to figure this out in the
first place, and secondly, integrate it with another piece of code or add new functionality to it. Because readability can have
such a great impact on the efficiency of programmers, spacing, variable naming and comments are regulated by pretty much
every coding standard out there. As these grew in size to almost mini-textbooks, it became hard to know all the rules. That's why
some coding standards come with a formatter or a linter. The former checks for stuff like tabs vs spaces or cammelCase vs snake\_case,
while the latter can perform static analysis and even find bugs. Such tools are used to automatically fix formatting mistakes.
The [Go](https://golang.org/) programming language comes with its out-of-the-box formatter, [gofmt](https://go.dev/blog/gofmt).

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/coding-standards/code/go_bad.go %}

Running `gofmt` on this code producess a much more readable version of itself.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/coding-standards/code/go_good.go %}

The programming community has developed a variety of coding styles, and we can't really say that one is better than the other.
Each has its own advantages and disadvantages, but they all preach one common thing: *Be consisten!*. And I'll quote
[PEP8](https://www.python.org/dev/peps/pep-0008/) here:

>A style guide is about consistency. Consistency with this style guide is important. Consistency within a project is more important.
Consistency within one module or function is the most important.

As it turns out, style guide recommendations are not always applicable, and in such cases you should not break backwards commpatibility
with the existing code. Sometimes even the language might not be particulary helpful with your coding standard. For example,
in C++ the `new` operator is designed to throw exceptions on failure. If you're following a _do not use exceptions_ policy,
you'll have to handling this, maybe by using `std::nothrow`:
```C++
int *array = new (std::nothrow) int [lengh];
```
This is not a big problem in itself, but it's an example of how sometimes things just don't work out of the box.
Imagine having to integrate your code with a third-party library that uses exceptions.

### Limiting side effects

This can be linked directly to readability, but I think it deserves its own paragraph. A side effect is an operation that
is performed in addition to the main operation executed by the statement. It's a common source of bugs and, unfortunately,
C++ allows the use side effects.
```C++
int num = 3;
num += --num - num--;
```
This is a confusing way of writing `num = num + num - 1 - num - 1;`. Coding standards are there to prevent such use of
side effects. It is true that some programmers highly value compact code. This is from the early days of computing,
when storage was very limited and expensive. Nowadays this is no longer the case, therefore clarity and maintenability
are more valuable.
Sometimes a statement can prove to be confusing even for the compiler.
```C++
int num = 3;
int other_num = (num++ * 2) + (num++ * 4); 
```
g++ displays a warning: _operation on 'num' may be undefined_.  
This is because the expression has two branches of equal priority, `(num++ * 2)` and `(num++ * 4)`. The compiler
may decide to execute `num++ * 2` first, `other_num` becoming 22, but it may also execute `num++ * 4` first, in which
case the `other_num` would be 20. You don't even need a coding guideline to tell you how wrong this is, the compiler
does it for you.  
To prevent such scenarious from happening, some languages, such as Python, deliberately do not define the `++` and `--` operators.

## In practice

### Python

[PEP8](https://www.python.org/dev/peps/pep-0008/) is a broadly accepted coding standard among Python developers. Their entire
standard library is written according to the conventions described there. The format checker is called
[pycodestyle](https://pypi.org/project/pycodestyle/) (previously known as pep8). Also, there are various tools
for auto-formatting, such as [autopep8](https://pypi.org/project/autopep8/), which can be used to automatically make your
code PEP8 compliant. Please note that there other popular Python coding standards out there,
such as the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html). Google uses [yapf](https://github.com/google/yapf) to "end
all holy wars about formatting".

### C++

[Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html) is a popular one. You can use
[cpplint](https://github.com/cpplint/cpplint) to check for style issues. For auto-formatting,
[clang-format](https://clang.llvm.org/docs/ClangFormat.html) is a great tool. It has good integration with many editors and
can be used to apply not only Google's style, but a bunch of other styles as well.
You can also create your custom style by editing the `.clang-format` file.

### One config to rule them all

Projects may be written in more than one language, therefore different coding styles are applied depending on the file type.
Developers may use different editors, each with different settings. Thus, it would be nice to have everything in a single
configuration file that could be parsed by all editors and applied on the whole project. By using
[EditorConfig](https://editorconfig.org/), you can place all of your project's configuration into a single file named `.editorconfig`,
located at the root of the project directory. Note that this tool is very flexible, allowing for custom configurations
in subdirectories.

## Bottom line

Following a coding guideline is a great thing to do, just don't go over the board with it. Beautiful code is a very subjective
matter, hence perfection is not something to strive for in here, but maintaining a good balance between productivity
and beauty is what really counts. *Use auto-formatters whenever you can.* As a matter of fact, many projects are including them in their testing
pipelines so that style is kept consistent in an automated manner. If you find yourself spending ridiculous amounts of time and
energy over manking code look pretty, there's a change you might be dealing with [OCD](https://en.wikipedia.org/wiki/Obsessive%E2%80%93compulsive_disorder).
I know it can feel very frustrating, but don't worry, it is more common than you think. Try [CBT](https://en.wikipedia.org/wiki/Cognitive_behavioral_therapy),
[meditation](https://tergar.org/meditation/) or a self help guide and let the auto-formatter do its work.  
Being proud of your code is a great feeling indeed, but getting things done feels a lot better on the long run.

## References

* [Oualline, Steve, *Practical C++ Programming, 2nd Edition*](https://www.oreilly.com/library/view/practical-c-programming/0596004192/)
