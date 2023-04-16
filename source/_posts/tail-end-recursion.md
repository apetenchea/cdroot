---
title: Tail-end recursion
date: 2019-02-12 11:14:07
tags: Programming
mathjax: true
---

There are cases when recursion can lead to [stack overflow](https://en.wikipedia.org/wiki/Stack_overflow).
Tail-end recursion can be optimized by the compiler such that the generated machine code looks like iteration.

## Why regular recursion is not always enough?

Recursion is sometimes a natural and elegant way to approach a problem, especially in the case of functional
programming languages, such as OCaml. The ability of a function to call itself is a powerful concept, but very deep
recursion can lead to crashes. One can overcome these by the use of tail-end recursion. Consider a function which
sums up all the integers between 1 and n: 

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/tail-end-recursion/code/simple-rec.ml %}

The code looks pretty nice and compact, but unfortunately if you take the *sum* function and put it into the
OCaml interpreter, it crashes for large values of n. 

```
# sum (int_of_float (10.0 ** 4.0));;
- : int = 50005000
# sum (int_of_float (10.0 ** 5.0));;
- : int = 5000050000
# sum (int_of_float (10.0 ** 6.0));;
Stack overflow during evaluation (looping recursion?).
```

The interpreter prints the "Stack overflow" message and suggests that the cause may be the way you
approached recursion. The reason why this occurs is because every function call has its own stack frame, so each
subsequent call to *sum* eats up some more space on the stack. The stack runs out of space,
thus resulting in a stack overflow. I used the `#trace` command to see what happens during execution.
It prints, in their order of occurrence, all the calls and returns of the traced function.

```
# #trace sum;;
sum is now traced.
# sum 4;;
sum <-- 4
sum <-- 3
sum <-- 2
sum <-- 1
sum --> 1
sum --> 3
sum --> 6
sum --> 10
- : int = 10
```

The depth of recursion is given by the number of consecutive calls to sum, in this case being 4.

### Under the hood

Let's compile the program and take a look inside the executable. 

```
ocamlopt -o simple-rec simple-rec.ml
objdump -d -M intel simple-rec > simple-rec.dump
```

Now you can really see what's behind the `sum` function. I will explain it bellow.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/tail-end-recursion/code/simple-rec.dump %}

The first parameter (integer n) is stored into register `rax`, but `rax` is also the register used
by the function to return a value. This may lead to some confusion.

```
00000000004022a0:
 4022a0: allocate space for a qword on the stack
 4022a4: compare n to 3
 4022a8: if n is not equal to 3 then jump to 4022b8
 4022aa: set return value as 3
 4022b1: free a qword from the stack
 4022b5: return
 4022b6: does nothing, just like a nop, used for alignment
 4022b8: copy the value of n to the stack
 4022bc: subtract 2 from n
 4022c0: call sum (n - 1)
 4022c5: store in rbx the result of sum (n - 1)
 4022c8: store in rax the current value of n, saved on the stack
 4022cc: add the result of sum (n - 1) to n
 4022cf: subtract 1 from rax
 4022d2: free a qword from the stack
 4022d6: return
 4022d7: 
 4022de: 
```

As a side note, there's something strange with the way OCaml represents integers in memory. Notice that
the base case appears to be n equals 3, instead of 1. Also at *4022cf* the sum is decremented,
yielding `n + sum (n - 1) - 1`.  This doesn't seem to resemble the code, but why?  
The reason is that in OCaml the least significant bit of an integer is used as a tag bit, in order to make the
distinction between pointers and integers at runtime. This means that you can obtain the real value of an integer if you
strip the tag bit, by doing a logical right shift, or more naturally, dividing by 2. So, OCaml will internally
represent the integer 1 as 3. That's why it does all these strange additions and subtractions.
More details can be found [here](https://v1.realworldocaml.org/v1/en/html/memory-representation-of-values.html).  

### The problem

Every `call` instruction pushes a return address (qword, 8 bytes) onto the stack. Also, before calling the function,
the value of `n` has to be stored on the stack, so there goes another qword. Every time `sum` is called,
it eats up 16 bytes from the stack. To compute the total number of bytes, you multiply the depth of the
recursion with 16. When n equals 1000000 that is approximately 16 MB, thus resulting in a stack overflow.  
Consider the following snippet of code: `n + sum (n - 1)`. The expression is dependent on the value returned by
`sum (n - 1)`, thus it has to store the current value of `n` on the stack until the result of `sum (n - 1)`
is returned. This happens again inside `sum (n - 1)`, because it has to store the value of `n - 1` on the stack until
`sum (n - 2)` returns, and so on. This long chain of dependencies is the root cause of the stack overflow.

## How tail-end recursion works?

The point of tail-end recursion is to write a function in such a way that the returned value depends only
on the subsequent calls, eliminating the need to keep local variables around.
In other words, there is no pending operation on the recursive call
(such as the addition of `n` to the computed sum). This way, if the compiler can optimize tail-end recursion,
it won't keep the state of every function call on the stack, but rather just the current one, as in a loop.
If the compiler could speak, it would say: "Ok, I won't use anything from this functions's stack frame again,
so there's no point in keeping it around. I could just go ahead and return the result of the recursive call
as the final result".  
Usually, a tail-end recursive function requires an extra argument, whose purpose is to accumulate the
result along the way. To avoid complicating the function's signature, you can write a tail-end recursive
function as a helper function and then define your "official function" to call the helper function with the
accumulator set to its initial value.

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/tail-end-recursion/code/tail-end.ml %}

`sum` doesn't crash anymore.

```
# sum (int_of_float (10.0 ** 6.0));;
- : int = 500000500000
# sum (int_of_float (10.0 ** 7.0));;
- : int = 50000005000000
# sum (int_of_float (10.0 ** 8.0));;
- : int = 5000000050000000
```

### Disassembly

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/tail-end-recursion/code/tail-end.dump %}

`acc` is initially stored in register `rax` and `n` is stored in `rbx`.
As you can see, there is not a single call instruction, only jumps! This means that the amount
of stack space needed to compute the sum is constant, no longer proportional to the depth of recursion.
In fact, this is not even recursion anymore, it's iteration. Take a look at the trace, you can see there are
no longer any recursive calls: 

```
# sum 10;;
sum <-- 10
sum --> 55
- : int = 55
# sum 12345;;
sum <-- 12345
sum --> 76205685
- : int = 76205685
```

Tail-end recursion is generally a great improvement, but it might reduce readability. A tail-end recursive version
of a function is not always this obvious, sometimes it may be harder to come up with one, and even harder for
somebody else to understand it by reading your code. Some compilers and interpreters are able to recognize tail-end
recursion and optimize it, some are not. Before you think about using it, make sure your programming language knows
how to deal with these things.

## Tail-end recursion in other languages

Let's analyze the output of some C compilers, this time on 32 bit programs. 

{% ghcode https://github.com/apetenchea/cdroot/blob/master/source/_posts/tail-end-recursion/code/tail-end.c %}

### GCC

```
gcc -Wall -O2 -std=c11 -m32 -masm=intel -S tail_end.c
```

The assembly code of `sum_helper` is analyzed bellow. As expected, GCC optimizes the function.
It first does a check for the base case, and if `n` is equal to 1 it jumps to `.L3`,
adding 1 to `acc`, which becomes 1. Otherwise, while `n` is not equal to 1, it executes the instructions
bellow `.L7` in a loop. 

```
sum_helper:
.LFB3:
 .cfi_startproc
 mov edx, DWORD PTR [esp+8] ; edx = n
 mov eax, DWORD PTR [esp+4] ; eax = acc
 cmp edx, 1                 ; compare n with 1
 je .L3                     ; if the above comparison is true, jump to .L3
 .p2align 4,,10
 .p2align 3
.L7:
 add eax, edx               ; add n to acc
 sub edx, 1                 ; decrement n
 cmp edx, 1                 ; compare n with 1
 jne .L7                    ; if n is not equal to 1 then jump to .L7
.L3:
 add eax, 1                 ; add 1 to acc
 ret                        ; return
 .cfi_endproc
```

### Clang

```
clang -Wall -O2 -std=c11 -m32 -masm=intel -S tail\_end.c
```

```
sum_helper:
 push edi
 push esi
 mov esi, dword ptr [esp + 16]
 mov ecx, dword ptr [esp + 12]
 cmp esi, 1
 je .LBB0_2
 lea edi, dword ptr [esi - 1]
 lea eax, dword ptr [esi - 2]
 imul edi, eax
 lea edx, dword ptr [esi - 3]
 mul edx
 shld edx, eax, 31
 add ecx, esi
 add ecx, edi
 sub ecx, edx
.LBB0_2:
 inc ecx
 mov eax, ecx
 pop esi
 pop edi
 ret
```

To be honest, I didn't expect this at all! Clang generated the following formula:  
$$n + (n - 1) * (n - 2) - (n - 2) * (n - 3) / 2 + 1$$

#### Proof

$$
\begin{split}
\frac{1}{2}(n−2)(n−3)+(n−2)(n−1)+n+1\\\\
\Leftrightarrow (n - 2)(n-1-\frac{n-3}{2})+n+1\\\\
\Leftrightarrow \frac{(n - 2)(2n-2-n+3)}{2}+n+1\\\\ 
\Leftrightarrow \frac{(n - 2)(n+1)}{2}+\frac{2(n+1)}{2}\Leftrightarrow \frac{n(n+1)}{2}\\\\
\end{split}
$$

For details, read about [arithmetic progressions](https://en.wikipedia.org/wiki/Arithmetic_progression).

#### Thorough analysis

This may go out the scope of this article, but I believe such an optimization deserves a more detailed explanation.
I will go through it step by step.

```
push edi
push esi
```

`edi` and `esi` are **callee saved registers**. This means a function has to keep a copy
before modifying them, and then restore their values before it returns. 

```
mov esi, dword ptr [esp + 16]
mov ecx, dword ptr [esp + 12]
```

The function parameters are stored on the stack. The first instruction takes the value of `n` and stores it
in register `esi`. The second one takes the value of `acc` and stores it into `ecx`. 

```
cmp esi, 1
je .LBB0_2
```

If `esi` (which now has the value of `n`) is equal to 1, jump to the location labeled `.LBB0_2`. 

```
lea edi, dword ptr [esi - 1]
lea eax, dword ptr [esi - 2]
```

The equivalent of the first instruction is `edi = n - 1`. Second instruction is: `eax = n - 2`.
Note that `lea` actually comes from "load effective address", and its original purpose was to handle memory addresses,
but it is often used for arithmetic operations. 

```
imul edi, eax
```

This takes the value in `eax`, multiplies it with `edi` and stores the result back in `edi`, whose value becomes
*(n - 1)* \* *(n - 2)*. 

```
lea edx, dword ptr [esi - 3]
```

Store the value *n - 3* in `edx`.

```
mul edx
```

This instruction multiplies the value stored in register `eax` with the value stored in register `edx`,
producing a 64 bit result, whose least significant 32 bits are in `eax`, and the other 32 bits in `edx`. 

```
shld edx, eax, 31
```

Double precision left shift: shifts `edx` left 31 times, and fills up uncovered bits from its right
side with bits copied from `eax`. Because only 31 bits from `eax` are spilled into `edx`, the
least significant bit of `eax` gets trimmed away, this operation being equivalent to a right shift, which is in
fact division by 2. After this instruction gets executed, `edx` is going to be *(n - 2)* \* *(n - 3) / 2*.

```
add ecx, esi
add ecx, edi
sub ecx, edx
.LBB0\_2:
inc ecx
```

Let's follow these instructions and pull out the formula for `ecx`. First add *n*.
Then add *(n - 1)* \* *(n - 2)*. The third instruction subtracts *(n - 2)* \* *(n - 3) / 2*.
The last one simply adds 1 to `ecx`.  
$$ecx = n + (n - 1) * (n - 2) - (n - 2) * (n - 3) / 2 + 1$$

```
mov eax, ecx
```

The result of the function has to be sored in register `eax`, so the value in `ecx` is copied.

```
pop esi
pop edi
```

Restore the previous values of `esi` and `edi`, then return to the caller.

## References and Further Reading

* [Downey, A. and Monje, N., (2008), *Think OCaml: How to Think like a (Functional) Programmer*](http://greenteapress.com/thinkocaml/)
* [Minsky, Y., Madhavapeddy, A. and Hickey, J., *Real World OCaml*](https://v1.realworldocaml.org/)
